from uuid import uuid4

from courier_service.delivery import BookingResult, Delivery, DeliveryStatus
from .courier import Courier


class RateBasedCourier(Courier):
    def __init__(self, name: str, rate_per_kg: float):
        self.name = name
        self.rate_per_kg = rate_per_kg
        self.bookings: list[Delivery] = []
        self._booking_results: dict[str, tuple[Delivery, BookingResult]] = {}
        print(
            f"RateBasedCourier '{self.name}' initialized with rate {self.rate_per_kg} per kg."
        )

    def quote(self, delivery) -> float:
        # Implement rate-based quoting logic here
        # For example, you could calculate the quote based on weight and distance
        return delivery.weight * self.rate_per_kg

    def book_shipment(
        self, delivery: Delivery, *, idempotency_key: str
    ) -> BookingResult:
        # This demo cache lasts for this courier instance. A real adapter must
        # forward the key to a provider that persists idempotency records.
        previous = self._booking_results.get(idempotency_key)
        if previous is not None:
            previous_delivery, result = previous
            if previous_delivery != delivery:
                raise ValueError("Idempotency key was already used for another delivery")
            return result
        result = BookingResult(
            tracking_number=str(uuid4()), courier_reference=str(uuid4())
        )
        print(f"Booking shipment for delivery {delivery.id} with {self.name}.")
        self.bookings.append(delivery)
        self._booking_results[idempotency_key] = (delivery, result)
        return result

    def update_delivery_status(self, delivery_id: str, status: DeliveryStatus) -> None:
        # Implement rate-based logic to update the delivery status
        print(
            f"Updating delivery {delivery_id} status to '{status.name}' for {self.name}."
        )
