from couriers import CourierSelector
from delivery import Delivery
from notifiers import Notifier
from repositories import ShipmentRepository


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

    def dispatch(self, delivery: Delivery) -> None:
        # Select the best courier for the delivery
        courier = self.courier_selector.select_courier(delivery)

        # Get a quote from the selected courier
        quote = courier.quote(delivery)
        print(f"Quote from {courier.__class__.__name__}: ${quote:.2f}")

        # Book the shipment with the selected courier
        courier.book_shipment(delivery)

        # Save the delivery details in the repository
        self.shipment_repository.save(delivery)

        # Notify the customer about the dispatch
        message = f"Your shipment with {courier.__class__.__name__} has been dispatched. Quote: ${quote:.2f}"
        self.notifier.notify(message)
