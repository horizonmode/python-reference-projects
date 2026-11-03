from typing import Protocol
from courier_service.delivery import BookingResult, DeliveryStatus, Delivery


class Courier(Protocol):
    def quote(self, delivery: Delivery) -> float: ...
    def book_shipment(
        self, delivery: Delivery, *, idempotency_key: str
    ) -> BookingResult:
        """Repeated requests with the same key must return the original booking."""
        ...
    def update_delivery_status(
        self, delivery_id: str, status: DeliveryStatus
    ) -> None: ...

    name: str
