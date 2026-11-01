from dataclasses import dataclass
from ship import Ship
from supply_type import SupplyType


@dataclass(frozen=True)
class Delivery:
    ship: Ship
    supply_type: SupplyType
    quantity: int
    delivery_id: int = 0
