import requests

from api.data import LongLat, WeatherForecast


class ApiWeatherProvider:
    METEO_API_URL = "https://api.open-meteo.com/v1/forecast"

    def get_weather(self, location: LongLat) -> WeatherForecast:
        response = requests.get(
            self.METEO_API_URL,
            params={
                "latitude": location.latitude,
                "longitude": location.longitude,
                "current": (
                    "temperature_2m,relative_humidity_2m," "wind_speed_10m,weather_code"
                ),
                "temperature_unit": "celsius",
                "wind_speed_unit": "kmh",
            },
            timeout=10,
        )
        response.raise_for_status()
        current = response.json()["current"]

        # Start with common conditions; extend using the docs' WMO table.
        descriptions = {
            0: "Clear sky",
            1: "Mainly clear",
            2: "Partly cloudy",
            3: "Overcast",
            45: "Fog",
            61: "Slight rain",
            63: "Moderate rain",
            65: "Heavy rain",
        }
        code = current["weather_code"]

        return WeatherForecast(
            temperature=current["temperature_2m"],
            humidity=current["relative_humidity_2m"],
            wind_speed=current["wind_speed_10m"],
            description=descriptions.get(code, f"Weather code {code}"),
        )
