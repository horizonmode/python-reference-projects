from dataclasses import dataclass
from enum import Enum, auto

from .booking_result import BookingResult
from .delivery import Delivery


class DispatchStatus(Enum):
    BOOKING_PENDING = auto()
    BOOKED = auto()
    NOTIFIED = auto()


@dataclass(frozen=True)
class DispatchRecord:
    delivery: Delivery
    courier_name: str
    quote: float
    status: DispatchStatus = DispatchStatus.BOOKING_PENDING
    booking: BookingResult | None = None

    def __post_init__(self):
        if self.status is DispatchStatus.BOOKING_PENDING and self.booking is not None:
            raise ValueError("A pending dispatch cannot already have a booking")
        if self.status is not DispatchStatus.BOOKING_PENDING and self.booking is None:
            raise ValueError("A booked dispatch must include its booking result")
