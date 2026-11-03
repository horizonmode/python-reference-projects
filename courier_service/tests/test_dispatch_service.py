from contextlib import closing
from dataclasses import replace
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from courier_service.couriers import Courier, RateBasedCourier, StandardSelector
from courier_service.delivery import Delivery, DeliveryPriority, DispatchRecord, DispatchStatus
from courier_service.dispatch_service import DispatchService
from courier_service.repositories import InMemoryRepository, SQLiteRepository


class RecordingNotifier:
    def __init__(self):
        self.messages: list[str] = []
        self.fail_next = False

    def notify(self, message: str) -> None:
        if self.fail_next:
            self.fail_next = False
            raise RuntimeError("Notification unavailable")
        self.messages.append(message)


class FailingRepository(InMemoryRepository):
    def __init__(self, fail_status: DispatchStatus):
        super().__init__()
        self.fail_status = fail_status
        self.fail_next = True

    def save_dispatch(self, record: DispatchRecord) -> None:
        if self.fail_next and record.status is self.fail_status:
            self.fail_next = False
            raise RuntimeError("Storage unavailable")
        super().save_dispatch(record)


class DispatchServiceTests(unittest.TestCase):
    def setUp(self):
        self.delivery = Delivery("Test address", 10, DeliveryPriority.STANDARD, id="one")
        self.courier = RateBasedCourier("Demo", 3)
        self.selector = StandardSelector([self.courier])
        self.notifier = RecordingNotifier()
        self.repository = InMemoryRepository()

    def test_repeated_dispatch_returns_original_booking_without_notifying_again(self):
        service = DispatchService(self.repository, self.selector, self.notifier)
        result = service.dispatch(self.delivery)
        self.assertEqual(service.dispatch(self.delivery), result)
        self.assertEqual(result.courier_name, "Demo")
        self.assertTrue(result.tracking_number)
        self.assertTrue(result.courier_reference)
        self.assertEqual(len(self.courier.bookings), 1)
        self.assertEqual(len(self.notifier.messages), 1)
        record = self.repository.get_dispatch(self.delivery.id)
        assert record is not None
        self.assertEqual(record.status, DispatchStatus.NOTIFIED)

    def test_intent_save_failure_does_not_book(self):
        repository = FailingRepository(DispatchStatus.BOOKING_PENDING)
        service = DispatchService(repository, self.selector, self.notifier)
        with self.assertRaisesRegex(RuntimeError, "Storage"):
            service.dispatch(self.delivery)
        self.assertEqual(self.courier.bookings, [])
        self.assertEqual(self.notifier.messages, [])
        service.dispatch(self.delivery)
        self.assertEqual(len(self.courier.bookings), 1)

    def test_booking_save_failure_reuses_key_and_original_courier(self):
        repository = FailingRepository(DispatchStatus.BOOKED)
        other = RateBasedCourier("Other", 10)
        couriers: list[Courier] = [self.courier, other]
        service = DispatchService(repository, StandardSelector(couriers), self.notifier)
        with self.assertRaisesRegex(RuntimeError, "Storage"):
            service.dispatch(self.delivery)
        self.assertEqual(self.notifier.messages, [])
        # A retry must not select the now-cheaper alternative.
        other.rate_per_kg = 1
        result = service.dispatch(self.delivery)
        self.assertEqual(result.courier_name, "Demo")
        self.assertEqual(result.quote, 30)
        self.assertEqual(len(self.courier.bookings), 1)
        self.assertEqual(other.bookings, [])
        self.assertEqual(len(self.notifier.messages), 1)

    def test_lost_booking_response_does_not_create_second_booking(self):
        class LostResponseCourier(RateBasedCourier):
            fail_next = True

            def book_shipment(self, delivery: Delivery, *, idempotency_key: str):
                result = super().book_shipment(delivery, idempotency_key=idempotency_key)
                if self.fail_next:
                    self.fail_next = False
                    raise RuntimeError("Response lost after booking")
                return result

        courier = LostResponseCourier("Demo", 3)
        service = DispatchService(self.repository, StandardSelector([courier]), self.notifier)
        with self.assertRaisesRegex(RuntimeError, "Response lost"):
            service.dispatch(self.delivery)
        self.assertEqual(self.notifier.messages, [])
        service.dispatch(self.delivery)
        self.assertEqual(len(courier.bookings), 1)

    def test_failed_booking_can_be_retried(self):
        class UnavailableCourier(RateBasedCourier):
            fail_next = True

            def book_shipment(self, delivery: Delivery, *, idempotency_key: str):
                if self.fail_next:
                    self.fail_next = False
                    raise RuntimeError("Booking unavailable")
                return super().book_shipment(delivery, idempotency_key=idempotency_key)

        courier = UnavailableCourier("Demo", 3)
        service = DispatchService(self.repository, StandardSelector([courier]), self.notifier)
        with self.assertRaisesRegex(RuntimeError, "Booking unavailable"):
            service.dispatch(self.delivery)
        self.assertEqual(courier.bookings, [])
        self.assertEqual(self.notifier.messages, [])
        service.dispatch(self.delivery)
        self.assertEqual(len(courier.bookings), 1)

    def test_notification_failure_retries_only_notification(self):
        self.notifier.fail_next = True
        service = DispatchService(self.repository, self.selector, self.notifier)
        with self.assertRaisesRegex(RuntimeError, "Notification"):
            service.dispatch(self.delivery)
        record = self.repository.get_dispatch(self.delivery.id)
        assert record is not None
        self.assertEqual(record.status, DispatchStatus.BOOKED)
        service.dispatch(self.delivery)
        self.assertEqual(len(self.courier.bookings), 1)
        self.assertEqual(len(self.notifier.messages), 1)

    def test_notification_checkpoint_failure_never_rebooks(self):
        repository = FailingRepository(DispatchStatus.NOTIFIED)
        service = DispatchService(repository, self.selector, self.notifier)
        with self.assertRaisesRegex(RuntimeError, "Storage"):
            service.dispatch(self.delivery)
        service.dispatch(self.delivery)
        self.assertEqual(len(self.courier.bookings), 1)
        # Sending succeeded before its checkpoint failed: notification can repeat.
        self.assertEqual(len(self.notifier.messages), 2)

    def test_same_id_with_changed_details_is_rejected(self):
        service = DispatchService(self.repository, self.selector, self.notifier)
        service.dispatch(self.delivery)
        with self.assertRaisesRegex(ValueError, "different details"):
            service.dispatch(replace(self.delivery, weight=20))
        self.assertEqual(len(self.courier.bookings), 1)

    def test_courier_rejects_key_reuse_for_different_delivery(self):
        self.courier.book_shipment(self.delivery, idempotency_key="key")
        with self.assertRaisesRegex(ValueError, "another delivery"):
            self.courier.book_shipment(replace(self.delivery, weight=20), idempotency_key="key")
        self.assertEqual(len(self.courier.bookings), 1)

    def test_sqlite_resumes_notification_after_reopening(self):
        with TemporaryDirectory() as directory:
            database = Path(directory) / "shipments.sqlite3"
            self.notifier.fail_next = True
            with closing(SQLiteRepository(database)) as repository:
                service = DispatchService(repository, self.selector, self.notifier)
                with self.assertRaisesRegex(RuntimeError, "Notification"):
                    service.dispatch(self.delivery)
                saved = repository.get_dispatch(self.delivery.id)
                assert saved is not None and saved.booking is not None
            # Recovery after reopening needs no courier call for an existing booking.
            with closing(SQLiteRepository(database)) as repository:
                service = DispatchService(repository, StandardSelector([]), self.notifier)
                result = service.dispatch(self.delivery)
                self.assertEqual(result.tracking_number, saved.booking.tracking_number)
                self.assertEqual(service.dispatch(self.delivery), result)
            self.assertEqual(len(self.courier.bookings), 1)
            self.assertEqual(len(self.notifier.messages), 1)


if __name__ == "__main__":
    unittest.main()
