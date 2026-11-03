from api.data import LongLat
from api.notifier import ConsoleNotifier
from api.provider.dummy_weather_provider import DummyWeatherProvider
from api.weather_service import WeatherService


def main() -> None:
    print("Hello from api!")
    user_input = input("Enter a location (latitude,longitude): ")
    try:
        latitude, longitude = map(float, user_input.split(","))
        location = LongLat(latitude=latitude, longitude=longitude)
        weather_service = WeatherService(DummyWeatherProvider(), ConsoleNotifier())
        weather_service.check_weather_and_notify(location)
    except ValueError:
        print(
            "Invalid input. Please enter latitude and longitude as numbers separated by a comma."
        )
        main()
