from couriers import (
    DHLCourier,
    PostOfficeCourier,
    StandardSelector,
)
from delivery import Delivery, DeliveryPriority
from dispatch_service import DispatchService
from notifiers import ConsoleNotifier
from repositories import InMemoryRepository

dhl_courier = DHLCourier()
post_office_courier = PostOfficeCourier()

courier_selector = StandardSelector()

notifier = ConsoleNotifier()

repository = InMemoryRepository()

dispatch_service = DispatchService(
    shipment_repository=repository,
    courier_selector=courier_selector,
    notifier=notifier,
)

# Example delivery
delivery = Delivery(
    weight=10.0,
    destination="123 Main St, Anytown, USA",
    priority=DeliveryPriority.STANDARD,
)

# Dispatch the delivery
dispatch_service.dispatch(delivery)
