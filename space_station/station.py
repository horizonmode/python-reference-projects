from supply_type import SupplyType


class SpaceStation:
    def __init__(self, name: str):
        self.name = name
        self.supplies = {SupplyType.FOOD: 0, SupplyType.FUEL: 0, SupplyType.MEDICAL: 0}

    def receive_delivery(self, delivery):
        if delivery.supply_type in self.supplies:
            self.supplies[delivery.supply_type] += delivery.quantity

    def get_supply_quantity(self, supply_type: SupplyType):
        if supply_type in self.supplies:
            return self.supplies[supply_type]
        else:
            raise ValueError(f"Supply type {supply_type} is not recognized.")
