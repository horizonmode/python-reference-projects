from delivery import Delivery
from supply_type import SupplyType


class Ship:
    def __init__(self, name):
        self.name = name
        self.supplies: dict[SupplyType, int] = {
            SupplyType.FOOD: 0,
            SupplyType.FUEL: 0,
            SupplyType.MEDICAL: 0,
        }
        self.deliveries: list[Delivery] = []

    def pickup_delivery(self, delivery: Delivery):
        if delivery.supply_type in self.supplies:
            self.supplies[delivery.supply_type] += delivery.quantity
        self.deliveries.append(delivery)

    def drop_delivery(self, delivery_id: int):
        for delivery in self.deliveries:
            if delivery.delivery_id == delivery_id:
                if delivery.supply_type in self.supplies:
                    self.supplies[delivery.supply_type] -= delivery.quantity
                self.deliveries.remove(delivery)
                return delivery

    def is_available_for_delivery(self):
        return len(self.deliveries) == 0
