from .shipment_repository import ShipmentRepository
from delivery import Delivery


class InMemoryRepository(ShipmentRepository):
    def __init__(self):
        self.storage = {}

    def save(self, delivery: Delivery) -> None:
        self.storage[delivery.id] = delivery

    def get(self, delivery_id: str) -> Delivery | None:
        return self.storage.get(delivery_id)
