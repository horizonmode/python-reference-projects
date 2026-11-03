from enum import Enum, auto


class DeliveryStatus(Enum):
    PENDING = auto()
    IN_TRANSIT = auto()
    DELIVERED = auto()
