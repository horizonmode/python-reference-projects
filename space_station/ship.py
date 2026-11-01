from supply_type import SupplyType


class Ship:

    SHIP_STATUS = ["available", "in_transit"]

    def __init__(self, name):
        self.name = name
        self.supplies = {SupplyType.FOOD: 0, SupplyType.FUEL: 0, SupplyType.MEDICAL: 0}
        self.deliveries = []

    def pickup_delivery(self, delivery):
        if delivery.supply_type in self.supplies:
            self.supplies[delivery.supply_type] += delivery.quantity
        self.deliveries.append(delivery)

    def drop_delivery(self, delivery_id):
        for delivery in self.deliveries:
            if delivery.delivery_id == delivery_id:
                if delivery.supply_type in self.supplies:
                    self.supplies[delivery.supply_type] -= delivery.quantity
                self.deliveries.remove(delivery)
                return delivery
                break

    def is_available_for_delivery(self):
        return len(self.deliveries) == 0

    def drop_next_delivery(self):
        if self.deliveries:
            delivery = self.deliveries.pop(0)
            if delivery.supply_type in self.supplies:
                self.supplies[delivery.supply_type] -= delivery.quantity
            return delivery
        return None
