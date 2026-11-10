from unittest.mock import patch

import requests
from django.test import TestCase

from api.data import WeatherForecast

from .models import Forecast


class ForecastViewTests(TestCase):
    def test_get_displays_form_without_fetching(self):
        with patch("weather.views.ApiWeatherProvider.get_weather") as get_weather:
            response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context["form"].is_bound)
        get_weather.assert_not_called()

    def test_successful_post_saves_and_redirects_without_resaving(self):
        with patch("weather.views.ApiWeatherProvider.get_weather", return_value=WeatherForecast(12, 70, 8, "Cloudy")), patch(
            "weather.views.PhotonLocationProvider.get_location_name", return_value="Frome"
        ):
            response = self.client.post("/", {"latitude": "51.231", "longitude": "-2.3218"})
        self.assertRedirects(response, "/")
        saved = Forecast.objects.get()
        self.assertEqual(saved.location_name, "Frome")
        self.assertEqual(saved.temperature, 12)
        self.assertEqual(saved.latitude, 51.231)
        response = self.client.get("/")
        self.assertEqual(response.context["forecast"], saved)
        self.assertEqual(list(response.context["forecasts"]), [saved])
        self.assertEqual(Forecast.objects.count(), 1)

    def test_invalid_post_does_not_fetch_or_save(self):
        with patch("weather.views.ApiWeatherProvider.get_weather") as get_weather:
            response = self.client.post("/", {"latitude": "100", "longitude": "0"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("latitude", response.context["form"].errors)
        get_weather.assert_not_called()
        self.assertFalse(Forecast.objects.exists())

    def test_api_failure_keeps_form_and_does_not_save(self):
        with patch("weather.views.ApiWeatherProvider.get_weather", side_effect=requests.Timeout):
            response = self.client.post("/", {"latitude": "51.231", "longitude": "-2.3218"})
        self.assertContains(response, "Weather is unavailable")
        self.assertEqual(response.context["form"]["latitude"].value(), "51.231")
        self.assertFalse(Forecast.objects.exists())
