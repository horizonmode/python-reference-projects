from delivery import Delivery

from .courier import Courier


class PostOfficeCourier(Courier):
    rate_per_kg: float = 3.0  # Example rate for Post Office
    bookings: list[Delivery] = []

    def quote(self, delivery) -> float:
        return delivery.weight * self.rate_per_kg  # Example quote calculation

    def book_shipment(self, delivery) -> None:
        # Implement Post Office-specific booking logic here
        self.bookings.append(delivery)
