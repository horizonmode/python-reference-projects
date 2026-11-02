from delivery import Delivery

from .courier import Courier


class DHLCourier(Courier):
    rate_per_kg: float = 5.0  # Example rate for DHL
    bookings: list[Delivery] = []

    def quote(self, delivery) -> float:
        return delivery.weight * self.rate_per_kg  # Example quote calculation

    def book_shipment(self, delivery) -> None:
        # Implement DHL-specific booking logic here
        self.bookings.append(delivery)
