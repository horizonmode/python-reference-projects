import pytest

from api.data import LongLat, WeatherForecast
from api.weather_service import WeatherService


class FakeWeatherProvider:
    def __init__(self, forecast: WeatherForecast):
        self.forecast = forecast
        self.locations: list[LongLat] = []
        self.error: Exception | None = None

    def get_weather(self, location: LongLat) -> WeatherForecast:
        self.locations.append(location)
        if self.error is not None:
            raise self.error
        return self.forecast


class RecordingNotifier:
    def __init__(self):
        self.messages: list[str] = []
        self.error: Exception | None = None

    def notify(self, message: str) -> None:
        self.messages.append(message)
        if self.error is not None:
            raise self.error


@pytest.fixture
def forecast() -> WeatherForecast:
    return WeatherForecast(15.0, 60.0, 5.0, "Cloudy")


@pytest.fixture
def location() -> LongLat:
    return LongLat(51.5, -0.1)


@pytest.fixture
def dependencies(forecast: WeatherForecast):
    provider = FakeWeatherProvider(forecast)
    notifier = RecordingNotifier()
    return WeatherService(provider, notifier), provider, notifier


def test_service_requests_forecast_once_for_supplied_location(dependencies, location):
    service, provider, _ = dependencies
    service.check_weather_and_notify(location)
    assert provider.locations == [location]


def test_service_returns_the_providers_forecast(dependencies, location, forecast):
    service, _, _ = dependencies
    assert service.check_weather_and_notify(location) is forecast


def test_service_sends_one_notification_with_location_and_forecast(
    dependencies, location, forecast,
):
    service, _, notifier = dependencies
    service.check_weather_and_notify(location)
    assert notifier.messages == [f"Weather data for {location}: {forecast}"]


def test_provider_failure_propagates_without_notifying(dependencies, location):
    service, provider, notifier = dependencies
    error = RuntimeError("Forecast unavailable")
    provider.error = error
    with pytest.raises(RuntimeError) as raised:
        service.check_weather_and_notify(location)
    assert raised.value is error
    assert provider.locations == [location]
    assert notifier.messages == []


def test_notification_failure_propagates_without_refetching(dependencies, location):
    service, provider, notifier = dependencies
    error = RuntimeError("Notification unavailable")
    notifier.error = error
    with pytest.raises(RuntimeError) as raised:
        service.check_weather_and_notify(location)
    assert raised.value is error
    assert provider.locations == [location]
    assert len(notifier.messages) == 1


def test_repeated_checks_use_latest_location_and_forecast(dependencies, location, forecast):
    service, provider, notifier = dependencies
    first = service.check_weather_and_notify(location)
    other_location = LongLat(-33.9, 151.2)
    other_forecast = WeatherForecast(28.0, 40.0, 12.0, "Sunny")
    provider.forecast = other_forecast
    second = service.check_weather_and_notify(other_location)
    assert first is forecast
    assert second is other_forecast
    assert provider.locations == [location, other_location]
    assert notifier.messages == [
        f"Weather data for {location}: {forecast}",
        f"Weather data for {other_location}: {other_forecast}",
    ]
