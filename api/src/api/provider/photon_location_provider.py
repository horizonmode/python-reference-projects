import logging

import requests

from api.data import LongLat


logger = logging.getLogger(__name__)


class PhotonLocationProvider:
    """Look up a nearby named place using OpenStreetMap data."""

    def get_location_name(self, location: LongLat) -> str | None:
        try:
            response = requests.get(
                "https://photon.komoot.io/reverse",
                params={
                    "lat": location.latitude,
                    "lon": location.longitude,
                    "limit": 1,
                    "lang": "en",
                },
                headers={"User-Agent": "WeatherCLI/0.1 (Python weather learning project)"},
                timeout=10,
            )
            response.raise_for_status()
            features = response.json().get("features", [])
            if not features:
                return None
            properties = features[0]["properties"]
            parts = []
            locality = properties.get("city") or properties.get("district") or properties.get("name")
            if locality:
                parts.append(locality)
            for key in ("county", "state", "country"):
                value = properties.get(key)
                if value and value not in parts:
                    parts.append(value)
            return ", ".join(parts) or None
        except (requests.RequestException, ValueError, KeyError, TypeError) as error:
            logger.warning("Location lookup failed: %s", error)
            return None
