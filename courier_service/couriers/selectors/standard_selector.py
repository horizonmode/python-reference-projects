from .courier_selector import CourierSelector
from ..courier import Courier
from ..dhl_courier import DHLCourier
from ..post_office_courier import PostOfficeCourier


class StandardSelector(CourierSelector):
    def select_courier(self, delivery) -> Courier:
        # Implement logic to select the best courier based on the delivery details
        # For example, you could compare quotes from different couriers and choose the cheapest one
        dhl_courier = DHLCourier()
        post_office_courier = PostOfficeCourier()

        dhl_quote = dhl_courier.quote(delivery)
        post_office_quote = post_office_courier.quote(delivery)

        if dhl_quote < post_office_quote:
            return dhl_courier
        else:
            return post_office_courier
