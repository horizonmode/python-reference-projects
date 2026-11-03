from dataclasses import dataclass


@dataclass(frozen=True)
class BookingResult:
    tracking_number: str
    courier_reference: str
