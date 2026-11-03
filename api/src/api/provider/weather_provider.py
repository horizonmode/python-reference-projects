from typing import Protocol

from api.data import LongLat, WeatherForecast


class WeatherProvider(Protocol):
    def get_weather(self, location: LongLat) -> WeatherForecast: ...
