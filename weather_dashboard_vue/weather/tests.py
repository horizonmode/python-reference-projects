import json
from unittest.mock import patch

import requests
from django.test import Client, TestCase

from api.data import WeatherForecast

from .models import Forecast


class ForecastApiTests(TestCase):
    def setUp(self):
        self.data = {
            "location_name": "Frome", "latitude": 51.231, "longitude": -2.3218,
            "temperature": 12, "humidity": 70, "wind_speed": 8, "description": "Cloudy",
        }
        self.forecast = Forecast.objects.create(**self.data)
        self.url = f"/api/forecasts/{self.forecast.pk}/"

    def write(self, method, url, data):
        return getattr(self.client, method)(url, data=json.dumps(data), content_type="application/json")

    def test_first_page_embeds_forecasts_and_csrf(self):
        self.forecast.description = '</script><script>alert("test")</script>'
        self.forecast.save()
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["initial_data"]["forecasts"][0]["id"], self.forecast.pk)
        self.assertTrue(response.context["initial_data"]["csrfToken"])
        self.assertContains(response, 'id="initial-data" type="application/json"')
        self.assertNotContains(response, self.forecast.description)
        self.assertContains(response, r"\u003C/script\u003E")

    def test_list_and_detail_have_same_shape_as_initial_data(self):
        bootstrap = self.client.get("/").context["initial_data"]["forecasts"]
        self.assertEqual(self.client.get("/api/forecasts/").json()["forecasts"], bootstrap)
        self.assertEqual(self.client.get(self.url).json()["forecast"], bootstrap[0])

    def test_create(self):
        response = self.write("post", "/api/forecasts/", self.data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Forecast.objects.count(), 2)
        self.assertEqual(response.json()["forecast"]["location_name"], "Frome")

    def test_put_replaces_editable_fields_and_preserves_timestamp(self):
        timestamp = self.forecast.fetched_at
        response = self.write("put", self.url, {**self.data, "temperature": 20})
        self.assertEqual(response.status_code, 200)
        self.forecast.refresh_from_db()
        self.assertEqual(self.forecast.temperature, 20)
        self.assertEqual(self.forecast.fetched_at, timestamp)

    def test_patch_updates_only_supplied_fields(self):
        response = self.write("patch", self.url, {"description": "Sunny"})
        self.assertEqual(response.status_code, 200)
        self.forecast.refresh_from_db()
        self.assertEqual(self.forecast.description, "Sunny")
        self.assertEqual(self.forecast.temperature, 12)

    def test_delete_and_missing_forecast(self):
        self.assertEqual(self.client.delete(self.url).status_code, 204)
        for method in ("get", "delete"):
            self.assertEqual(getattr(self.client, method)(self.url).status_code, 404)
        self.assertEqual(self.write("patch", self.url, {}).status_code, 404)

    def test_validation_does_not_change_database(self):
        for invalid in ({"latitude": 91}, {"humidity": 101}, {"wind_speed": -1},
                        {"temperature": float("nan")}, {"location_name": ""},
                        {"latitude": True}, {"description": ["Cloudy"]}):
            with self.subTest(invalid=invalid):
                response = self.write("patch", self.url, invalid)
                self.assertEqual(response.status_code, 400)
        self.forecast.refresh_from_db()
        self.assertEqual(self.forecast.latitude, self.data["latitude"])
        self.assertEqual(self.forecast.humidity, self.data["humidity"])

    def test_put_requires_all_fields_and_rejects_read_only_fields(self):
        self.assertEqual(self.write("put", self.url, {"temperature": 20}).status_code, 400)
        self.assertEqual(self.write("patch", self.url, {"id": 100}).status_code, 400)

    def test_bad_json_and_content_type(self):
        for body in ("{", "null", "[]", '"text"'):
            self.assertEqual(self.client.post("/api/forecasts/", body, content_type="application/json").status_code, 400)
        self.assertEqual(self.client.post("/api/forecasts/", self.data).status_code, 415)

    def test_wrong_methods_are_rejected(self):
        self.assertEqual(self.client.delete("/api/forecasts/").status_code, 405)
        self.assertEqual(self.client.post(self.url).status_code, 405)
        self.assertEqual(self.client.get("/api/forecasts/fetch/").status_code, 405)

    def test_csrf_is_required_for_all_mutations(self):
        client = Client(enforce_csrf_checks=True)
        for method, url in (("post", "/api/forecasts/"), ("put", self.url),
                            ("patch", self.url), ("delete", self.url),
                            ("post", "/api/forecasts/fetch/")):
            self.assertEqual(getattr(client, method)(url, data=json.dumps(self.data), content_type="application/json").status_code, 403)
        token = client.get("/").context["initial_data"]["csrfToken"]
        response = client.post("/api/forecasts/", data=json.dumps(self.data),
                               content_type="application/json", HTTP_X_CSRFTOKEN=token)
        self.assertEqual(response.status_code, 201)

    def test_fetch_and_save_live_weather(self):
        with patch("weather.services.ApiWeatherProvider.get_weather", return_value=WeatherForecast(15, 75, 10, "Sunny")), patch(
            "weather.services.PhotonLocationProvider.get_location_name", return_value="Bath"
        ):
            response = self.write("post", "/api/forecasts/fetch/", {"latitude": 51, "longitude": -2})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["forecast"]["location_name"], "Bath")
        self.assertEqual(Forecast.objects.count(), 2)

    def test_fetch_failure_does_not_save(self):
        with patch("weather.services.ApiWeatherProvider.get_weather", side_effect=requests.Timeout):
            response = self.write("post", "/api/forecasts/fetch/", {"latitude": 51, "longitude": -2})
        self.assertEqual(response.status_code, 502)
        self.assertEqual(Forecast.objects.count(), 1)

    def test_invalid_coordinates_do_not_call_provider(self):
        with patch("weather.services.ApiWeatherProvider.get_weather") as provider:
            response = self.write("post", "/api/forecasts/fetch/", {"latitude": 100, "longitude": 0})
        self.assertEqual(response.status_code, 400)
        provider.assert_not_called()

    def test_empty_database_bootstraps_empty_list(self):
        Forecast.objects.all().delete()
        self.assertEqual(self.client.get("/").context["initial_data"]["forecasts"], [])

    def test_pagination_is_shared_with_initial_page_and_links_use_api(self):
        Forecast.objects.bulk_create([Forecast(**self.data) for _ in range(24)])
        initial = self.client.get("/").context["initial_data"]
        first = self.client.get("/api/forecasts/").json()
        for key in ("forecasts", "count", "next", "previous"):
            self.assertEqual(initial[key], first[key])
        self.assertEqual(first["count"], 25)
        self.assertEqual(len(first["forecasts"]), 20)
        self.assertEqual(first["next"], "http://testserver/api/forecasts/?page=2")
        self.assertIsNone(first["previous"])
        second = self.client.get(first["next"]).json()
        self.assertEqual(len(second["forecasts"]), 5)
        self.assertIsNone(second["next"])
        self.assertTrue(second["previous"].endswith("/api/forecasts/?page=1"))
        ids = [item["id"] for item in first["forecasts"] + second["forecasts"]]
        self.assertEqual(len(set(ids)), 25)
        missing = self.client.get("/api/forecasts/?page=999")
        self.assertEqual(missing.status_code, 404)
        self.assertIn("error", missing.json())

    def test_errors_have_consistent_json_envelope(self):
        invalid = self.write("patch", self.url, {"humidity": 200})
        self.assertIn("error", invalid.json())
        self.assertIn("humidity", invalid.json()["errors"])
        for response in (
            self.client.get("/api/forecasts/999/"),
            self.client.post(self.url),
            self.client.post("/api/forecasts/", "{", content_type="application/json"),
        ):
            self.assertIn("error", response.json())

    def test_invalid_provider_data_is_not_saved(self):
        with patch("weather.services.ApiWeatherProvider.get_weather", return_value=WeatherForecast(15, 200, 10, "Sunny")), patch(
            "weather.services.PhotonLocationProvider.get_location_name", return_value="Bath"
        ):
            response = self.write("post", "/api/forecasts/fetch/", {"latitude": 51, "longitude": -2})
        self.assertEqual(response.status_code, 502)
        self.assertEqual(Forecast.objects.count(), 1)

    def test_infinite_string_and_read_only_input_are_rejected(self):
        for value in ("nan", "inf", "-inf"):
            self.assertEqual(self.write("patch", self.url, {"temperature": value}).status_code, 400)
        for values in ({"fetched_at": "2026-01-01T00:00:00Z"}, {"id": 100}, {"typo": "x"}):
            self.assertEqual(self.write("post", "/api/forecasts/", {**self.data, **values}).status_code, 400)

    def test_authenticated_session_still_requires_csrf(self):
        from django.contrib.auth import get_user_model

        user = get_user_model().objects.create(username="weather-test")
        client = Client(enforce_csrf_checks=True)
        client.force_login(user)
        self.assertEqual(client.delete(self.url).status_code, 403)
        token = client.get("/").context["initial_data"]["csrfToken"]
        self.assertEqual(client.delete(self.url, HTTP_X_CSRFTOKEN=token).status_code, 204)
