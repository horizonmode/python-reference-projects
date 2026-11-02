from typing import Protocol
from delivery import Delivery


class ShipmentRepository(Protocol):
    def save(self, delivery: Delivery) -> None: ...
    def get(self, delivery_id: str) -> Delivery | None: ...
