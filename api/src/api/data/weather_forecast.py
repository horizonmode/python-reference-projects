from dataclasses import dataclass


@dataclass
class WeatherForecast:
    temperature: float
    humidity: float
    wind_speed: float
    description: str

    __post_init__ = lambda self: (
        isinstance(self.temperature, (int, float))
        and isinstance(self.humidity, (int, float))
        and isinstance(self.wind_speed, (int, float))
        and isinstance(self.description, str)
        or (_ for _ in ()).throw(
            ValueError(
                "Temperature, Humidity, Wind Speed must be numeric values and Description must be a string."
            )
        )
    )
