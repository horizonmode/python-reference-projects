from typing import Protocol
from ..courier import Courier


class CourierSelector(Protocol):
    def select_courier(self, delivery) -> Courier: ...
