from api.notifier import Notifier
from api.provider import WeatherProvider
from api.data import LongLat, WeatherForecast


class WeatherService:
    def __init__(self, weather_provider: WeatherProvider, notifier: Notifier):
        self.weather_provider = weather_provider
        self.notifier = notifier

    def check_weather_and_notify(self, location: LongLat) -> WeatherForecast:
        weather_data = self.weather_provider.get_weather(location)
        self.notifier.notify(f"Weather data for {location}: {weather_data}")
        return weather_data
