from .courier_selector import CourierSelector
from ..courier import Courier


class StandardSelector(CourierSelector):
    def __init__(self, couriers: list[Courier]):
        # Initialize the list of available couriers
        self.couriers = couriers
        if len({courier.name for courier in couriers}) != len(couriers):
            raise ValueError("Courier names must be unique")

    def get_courier(self, name: str) -> Courier:
        for courier in self.couriers:
            if courier.name == name:
                return courier
        raise ValueError(f"Previously selected courier {name!r} is unavailable")

    def select_courier(self, delivery) -> Courier:
        # Implement standard selection logic here
        # For example, you could select the courier with the lowest quote for the given delivery
        best_courier = min(self.couriers, key=lambda c: c.quote(delivery))
        print(
            f"Selected courier '{best_courier.name}' for delivery {delivery.id} with quote {best_courier.quote(delivery)}."
        )
        return best_courier
