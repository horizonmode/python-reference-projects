from api.data import LongLat, WeatherForecast
from api.weather_service import WeatherService
from api.provider import WeatherProvider
from api.notifier import Notifier


class MockWeatherProvider(WeatherProvider):
    def __init__(self):
        self.received_location = None

    def get_weather(self, location: LongLat) -> WeatherForecast:
        self.received_location = location
        return WeatherForecast(
            temperature=25.0,
            humidity=50.0,
            wind_speed=10.0,
            description="Sunny",
        )


class MockNotifier(Notifier):
    def notify(self, message: str):
        pass  # Do nothing for testing


def test_service_passes_location_to_provider():
    mock_provider = MockWeatherProvider()
    mock_notifier = MockNotifier()
    service = WeatherService(mock_provider, mock_notifier)

    test_location = LongLat(latitude=40.7128, longitude=-74.0060)
    service.check_weather_and_notify(test_location)

    assert mock_provider.received_location == test_location


def test_service_returns_weather_data():
    mock_provider = MockWeatherProvider()
    mock_notifier = MockNotifier()
    service = WeatherService(mock_provider, mock_notifier)

    test_location = LongLat(latitude=40.7128, longitude=-74.0060)
    weather_data = service.check_weather_and_notify(test_location)

    assert weather_data.temperature == 25.0
    assert weather_data.humidity == 50.0
    assert weather_data.wind_speed == 10.0
    assert weather_data.description == "Sunny"


def test_service_notifies_with_correct_message():
    class TestNotifier(Notifier):
        def __init__(self):
            self.last_message = None

        def notify(self, message: str):
            self.last_message = message

    mock_provider = MockWeatherProvider()
    test_notifier = TestNotifier()
    service = WeatherService(mock_provider, test_notifier)

    test_location = LongLat(latitude=40.7128, longitude=-74.0060)
    service.check_weather_and_notify(test_location)

    expected_message = (
        f"Weather data for {test_location}: {mock_provider.get_weather(test_location)}"
    )
    assert test_notifier.last_message == expected_message
