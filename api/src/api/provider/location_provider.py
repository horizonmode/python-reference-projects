from typing import Protocol

from api.data import LongLat


class LocationProvider(Protocol):
    def get_location_name(self, location: LongLat) -> str | None: ...
