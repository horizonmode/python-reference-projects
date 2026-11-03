from .weather_provider import WeatherProvider
from api.data import LongLat, WeatherForecast


class DummyWeatherProvider(WeatherProvider):
    def get_weather(self, location: LongLat) -> WeatherForecast:
        # Return dummy weather data for testing purposes
        return WeatherForecast(
            temperature=25.0,
            humidity=50.0,
            wind_speed=10.0,
            description="Sunny",
        )
