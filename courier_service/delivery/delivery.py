from dataclasses import dataclass, field
from random import Random

from .delivery_priority import DeliveryPriority


@dataclass(frozen=True)
class Delivery:
    destination: str
    weight: float
    priority: DeliveryPriority
    id: str = field(default_factory=lambda: str(Random().randint(100000, 999999)))
