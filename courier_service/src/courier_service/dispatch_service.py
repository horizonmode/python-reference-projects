from dataclasses import dataclass, replace

from courier_service.couriers import CourierSelector
from courier_service.delivery import Delivery, DispatchRecord, DispatchStatus
from courier_service.notifiers import Notifier
from courier_service.repositories import ShipmentRepository


@dataclass(frozen=True)
class DispatchResult:
    courier_name: str
    tracking_number: str
    courier_reference: str
    quote: float


class DispatchService:
    def __init__(
        self,
        shipment_repository: ShipmentRepository,
        courier_selector: CourierSelector,
        notifier: Notifier,
    ):
        self.shipment_repository = shipment_repository
        self.courier_selector = courier_selector
        self.notifier = notifier

    def dispatch(self, delivery: Delivery) -> DispatchResult:
        record = self.shipment_repository.get_dispatch(delivery.id)
        if record is not None and record.delivery != delivery:
            raise ValueError(
                "Delivery ID was already dispatched with different details"
            )

        if record is None:
            courier = self.courier_selector.select_courier(delivery)
            record = DispatchRecord(
                delivery=delivery,
                courier_name=courier.name,
                quote=courier.quote(delivery),
            )
            # Persist the chosen courier before making any booking request.
            self.shipment_repository.save_dispatch(record)

        if record.status is DispatchStatus.BOOKING_PENDING:
            # A retry must use the original courier, even if prices have changed.
            courier = self.courier_selector.get_courier(record.courier_name)
            booking = courier.book_shipment(delivery, idempotency_key=delivery.id)
            record = replace(record, status=DispatchStatus.BOOKED, booking=booking)
            self.shipment_repository.save_dispatch(record)

        booking = record.booking
        if booking is None:
            raise RuntimeError("Dispatch has no booking result")

        if record.status is DispatchStatus.BOOKED:
            message = (
                f"Your shipment with {record.courier_name} has been dispatched. "
                f"Tracking: {booking.tracking_number}. Quote: ${record.quote:.2f}"
            )
            self.notifier.notify(message)
            record = replace(record, status=DispatchStatus.NOTIFIED)
            self.shipment_repository.save_dispatch(record)

        return DispatchResult(
            courier_name=record.courier_name,
            tracking_number=booking.tracking_number,
            courier_reference=booking.courier_reference,
            quote=record.quote,
        )
