from threading import Lock

from delivery import Delivery
from supply_type import SupplyType


class SpaceStation:
    def __init__(self, name: str):
        self.name = name
        self._supplies_lock = Lock()
        self.supplies: dict[SupplyType, int] = {
            SupplyType.FOOD: 0,
            SupplyType.FUEL: 0,
            SupplyType.MEDICAL: 0,
        }

    def receive_delivery(self, delivery: Delivery):
        with self._supplies_lock:
            if delivery.supply_type in self.supplies:
                self.supplies[delivery.supply_type] += delivery.quantity

    def get_supply_quantity(self, supply_type: SupplyType):
        with self._supplies_lock:
            if supply_type in self.supplies:
                return self.supplies[supply_type]
            else:
                raise ValueError(f"Supply type {supply_type} is not recognized.")
