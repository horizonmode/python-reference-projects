from unittest.mock import Mock, patch

import pytest
import requests

from api.data import LongLat
from api.provider.photon_location_provider import PhotonLocationProvider
from api.provider import DummyWeatherProvider
from api.weather_service import WeatherService


@pytest.mark.parametrize("features,expected", [
    ([{"properties": {"name": "London", "city": "London", "country": "United Kingdom"}}],
     "London, United Kingdom"),
    ([], None),
    ([{"properties": {}}], None),
    ([{"properties": {"name": "Market Place", "city": "Frome", "county": "Somerset",
                       "state": "England", "country": "United Kingdom"}}],
     "Frome, Somerset, England, United Kingdom"),
])
def test_reverse_lookup(features, expected):
    response = Mock()
    response.json.return_value = {"features": features}
    with patch("api.provider.photon_location_provider.requests.get", return_value=response) as get:
        assert PhotonLocationProvider().get_location_name(LongLat(51.5, -0.1)) == expected
    assert get.call_args.kwargs["params"]["lat"] == 51.5
    assert get.call_args.kwargs["params"]["lon"] == -0.1
    assert get.call_args.kwargs["headers"]["User-Agent"].startswith("WeatherCLI/")
    response.raise_for_status.assert_called_once()


def test_lookup_failure_is_optional(caplog):
    with patch("api.provider.photon_location_provider.requests.get", side_effect=requests.Timeout):
        assert PhotonLocationProvider().get_location_name(LongLat(51.5, -0.1)) is None
    assert "Location lookup failed" in caplog.text


@pytest.mark.parametrize("name", ["London, United Kingdom", None])
def test_service_includes_place_or_falls_back_to_coordinates(name):
    notifier = Mock()
    provider = Mock()
    provider.get_location_name.return_value = name
    location = LongLat(51.5, -0.1)
    WeatherService(DummyWeatherProvider(), notifier, provider).check_weather_and_notify(location)
    message = notifier.notify.call_args.args[0]
    if name:
        assert f"Location: {name}" in message.splitlines()
        assert f"Weather data for {name}:" in message
        assert str(location) not in message
    else:
        assert "Location: Name unavailable" in message.splitlines()
        assert str(location) in message
        assert "None" not in message
