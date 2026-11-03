from dataclasses import dataclass


@dataclass
class LongLat:
    latitude: float
    longitude: float

    __post_init__ = lambda self: (
        isinstance(self.latitude, (int, float))
        and isinstance(self.longitude, (int, float))
        or (_ for _ in ()).throw(
            ValueError("Latitude and Longitude must be numeric values.")
        )
    )
