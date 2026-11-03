from .shipment_repository import ShipmentRepository
from courier_service.delivery import Delivery, DispatchRecord


class InMemoryRepository(ShipmentRepository):
    def __init__(self):
        self.storage = {}
        self._dispatches: dict[str, DispatchRecord] = {}

    def save(self, delivery: Delivery) -> None:
        self.storage[delivery.id] = delivery

    def get(self, delivery_id: str) -> Delivery | None:
        return self.storage.get(delivery_id)

    def save_dispatch(self, record: DispatchRecord) -> None:
        self.storage[record.delivery.id] = record.delivery
        self._dispatches[record.delivery.id] = record

    def get_dispatch(self, delivery_id: str) -> DispatchRecord | None:
        return self._dispatches.get(delivery_id)
