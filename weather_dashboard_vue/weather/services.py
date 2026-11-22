import requests

from api.data import LongLat
from api.provider import ApiWeatherProvider
from api.provider.photon_location_provider import PhotonLocationProvider


class WeatherProviderError(Exception):
    pass


def fetch_forecast_data(*, latitude, longitude):
    """Fetch provider data without coupling the providers to HTTP API responses."""
    location = LongLat(latitude=latitude, longitude=longitude)
    try:
        result = ApiWeatherProvider().get_weather(location)
        name = PhotonLocationProvider().get_location_name(location) or "Location name unavailable"
        return {
            "latitude": latitude, "longitude": longitude, "location_name": name,
            "temperature": result.temperature, "humidity": result.humidity,
            "wind_speed": result.wind_speed, "description": result.description,
        }
    except (requests.RequestException, ValueError, KeyError, TypeError) as exc:
        raise WeatherProviderError from exc
