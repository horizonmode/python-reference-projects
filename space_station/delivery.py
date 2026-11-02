from dataclasses import dataclass
from supply_type import SupplyType


@dataclass(frozen=True)
class Delivery:
    supply_type: SupplyType
    quantity: int
    delivery_id: int = 0
