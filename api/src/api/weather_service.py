from api.notifier import Notifier
from api.provider import WeatherProvider
from api.data import LongLat, WeatherForecast
from api.provider.location_provider import LocationProvider


class WeatherService:
    def __init__(
        self, weather_provider: WeatherProvider, notifier: Notifier,
        location_provider: LocationProvider | None = None,
    ):
        self.weather_provider = weather_provider
        self.notifier = notifier
        self.location_provider = location_provider

    def check_weather_and_notify(self, location: LongLat) -> WeatherForecast:
        weather_data = self.weather_provider.get_weather(location)
        place = (
            self.location_provider.get_location_name(location)
            if self.location_provider else None
        )
        label = place or str(location)
        message = f"Weather data for {label}: {weather_data}"
        if self.location_provider is not None:
            location_line = place or "Name unavailable"
            message = f"Location: {location_line}\n{message}"
        self.notifier.notify(message)
        return weather_data
