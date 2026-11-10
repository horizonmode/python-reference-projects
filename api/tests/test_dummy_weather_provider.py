import pytest

from api.data import LongLat, WeatherForecast
from api.provider import DummyWeatherProvider


@pytest.mark.parametrize("location", [LongLat(51.5, -0.1), LongLat(-33.9, 151.2)])
def test_dummy_provider_returns_forecast_without_external_dependencies(location: LongLat):
    provider = DummyWeatherProvider()
    assert provider.get_weather(location) == WeatherForecast(
        temperature=25.0,
        humidity=50.0,
        wind_speed=10.0,
        description="Sunny",
    )
