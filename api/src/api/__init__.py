from api.data import LongLat
from api.notifier import ConsoleNotifier
from api.provider import ApiWeatherProvider
from api.weather_service import WeatherService
from api.provider.photon_location_provider import PhotonLocationProvider


def main() -> None:
    print("Hello from api!")
    user_input = input("Enter a location (latitude,longitude): ")
    try:
        latitude, longitude = map(float, user_input.split(","))
        location = LongLat(latitude=latitude, longitude=longitude)
        weather_service = WeatherService(
            ApiWeatherProvider(), ConsoleNotifier(), PhotonLocationProvider()
        )
        weather_service.check_weather_and_notify(location)
        print("Location data: © OpenStreetMap contributors (https://www.openstreetmap.org/copyright)")
    except ValueError:
        print(
            "Invalid input. Please enter latitude and longitude as numbers separated by a comma."
        )
        main()
