from enum import Enum


class ShipStatus(Enum):
    IDLE = 1
    IN_TRANSIT = 2
    DELIVERING = 3
