import argparse
from contextlib import closing
from pathlib import Path
from collections.abc import Sequence

from courier_service.couriers import RateBasedCourier, StandardSelector, Courier
from courier_service.delivery import Delivery, DeliveryPriority
from courier_service.dispatch_service import DispatchService
from courier_service.notifiers import ConsoleNotifier
from courier_service.repositories import SQLiteRepository


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Dispatch a delivery and save it to SQLite"
    )
    parser.add_argument(
        "--database",
        type=Path,
        default=Path("shipments.sqlite3"),
        help="SQLite file (default: shipments.sqlite3 in the current directory)",
    )
    args = parser.parse_args(argv)

    couriers: list[Courier] = [
        RateBasedCourier(name="DHL", rate_per_kg=5.0),
        RateBasedCourier(name="FedEx", rate_per_kg=4.0),
    ]

    with closing(SQLiteRepository(args.database)) as repository:
        dispatch_service = DispatchService(
            shipment_repository=repository,
            courier_selector=StandardSelector(couriers=couriers),
            notifier=ConsoleNotifier(),
        )
        delivery = Delivery(
            weight=10.0,
            destination="123 Main St, Anytown, USA",
            priority=DeliveryPriority.STANDARD,
        )
        result = dispatch_service.dispatch(delivery)
        print(f"Saved delivery {delivery.id} to {args.database}")
        print(f"Tracking number: {result.tracking_number}")


if __name__ == "__main__":
    main()
