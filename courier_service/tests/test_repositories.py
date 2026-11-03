from contextlib import closing
from dataclasses import replace
from pathlib import Path
from tempfile import TemporaryDirectory
import sqlite3
import unittest

from courier_service.delivery import BookingResult, Delivery, DeliveryPriority, DispatchRecord, DispatchStatus
from courier_service.repositories import InMemoryRepository, SQLiteRepository


class RepositoryTests(unittest.TestCase):
    def test_repository_contract(self):
        with closing(SQLiteRepository(":memory:")) as sqlite_repository:
            for repository in (InMemoryRepository(), sqlite_repository):
                with self.subTest(repository=type(repository).__name__):
                    self.assertIsNone(repository.get("missing"))
                    for priority in DeliveryPriority:
                        delivery = Delivery(
                            id=priority.name,
                            destination="12 O'Brien Street",
                            weight=10.5,
                            priority=priority,
                        )
                        repository.save(delivery)
                        self.assertEqual(repository.get(delivery.id), delivery)
                        updated = replace(delivery, weight=20.0, destination="New address")
                        repository.save(updated)
                        self.assertEqual(repository.get(delivery.id), updated)

    def test_sqlite_persists_after_reopening(self):
        with TemporaryDirectory() as directory:
            database = Path(directory) / "shipments.sqlite3"
            delivery = Delivery("Test address", 2.5, DeliveryPriority.EXPRESS, id="shipment-1")
            with closing(SQLiteRepository(database)) as repository:
                repository.save(delivery)
            with closing(SQLiteRepository(database)) as repository:
                self.assertEqual(repository.get(delivery.id), delivery)

    def test_dispatch_state_contract(self):
        delivery = Delivery("Test address", 2.5, DeliveryPriority.EXPRESS, id="dispatch-1")
        with closing(SQLiteRepository(":memory:")) as sqlite_repository:
            for repository in (InMemoryRepository(), sqlite_repository):
                with self.subTest(repository=type(repository).__name__):
                    self.assertIsNone(repository.get_dispatch(delivery.id))
                    record = DispatchRecord(delivery, "Demo", 12.5)
                    for status in DispatchStatus:
                        booking = (
                            None if status is DispatchStatus.BOOKING_PENDING
                            else BookingResult("tracking-1", "reference-1")
                        )
                        record = replace(record, status=status, booking=booking)
                        repository.save_dispatch(record)
                        self.assertEqual(repository.get_dispatch(delivery.id), record)
                        self.assertEqual(repository.get(delivery.id), delivery)

    def test_dispatch_save_is_atomic(self):
        with TemporaryDirectory() as directory:
            database = Path(directory) / "shipments.sqlite3"
            with closing(SQLiteRepository(database)) as repository:
                with closing(sqlite3.connect(database)) as connection:
                    connection.execute(
                        """CREATE TRIGGER reject_dispatch BEFORE INSERT ON dispatches
                        BEGIN SELECT RAISE(ABORT, 'Cannot save dispatch'); END"""
                    )
                    connection.commit()
                delivery = Delivery("Test", 1, DeliveryPriority.STANDARD, id="atomic")
                with self.assertRaises(sqlite3.IntegrityError):
                    repository.save_dispatch(DispatchRecord(delivery, "Demo", 3))
                self.assertIsNone(repository.get(delivery.id))
                self.assertIsNone(repository.get_dispatch(delivery.id))


if __name__ == "__main__":
    unittest.main()
