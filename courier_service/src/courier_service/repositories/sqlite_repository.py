import sqlite3
from pathlib import Path

from courier_service.delivery import (
    BookingResult,
    Delivery,
    DeliveryPriority,
    DispatchRecord,
    DispatchStatus,
)


class SQLiteRepository:
    """Persistent implementation of the ShipmentRepository protocol."""

    def __init__(self, database: str | Path):
        self._connection = sqlite3.connect(database)
        try:
            with self._connection:
                self._connection.execute(
                    """
                    CREATE TABLE IF NOT EXISTS shipments (
                        id TEXT PRIMARY KEY,
                        destination TEXT NOT NULL,
                        weight REAL NOT NULL,
                        priority TEXT NOT NULL
                    )
                    """
                )
                # A separate table also works with existing shipments databases.
                self._connection.execute(
                    """
                    CREATE TABLE IF NOT EXISTS dispatches (
                        delivery_id TEXT PRIMARY KEY,
                        destination TEXT NOT NULL,
                        weight REAL NOT NULL,
                        priority TEXT NOT NULL,
                        courier_name TEXT NOT NULL,
                        quote REAL NOT NULL,
                        status TEXT NOT NULL,
                        tracking_number TEXT,
                        courier_reference TEXT
                    )
                    """
                )
        except Exception:
            self._connection.close()
            raise

    def save(self, delivery: Delivery) -> None:
        with self._connection:
            self._save_delivery(delivery)

    def _save_delivery(self, delivery: Delivery) -> None:
        self._connection.execute(
            """
            INSERT INTO shipments (id, destination, weight, priority)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                destination = excluded.destination,
                weight = excluded.weight,
                priority = excluded.priority
            """,
            (delivery.id, delivery.destination, delivery.weight, delivery.priority.name),
        )

    def get(self, delivery_id: str) -> Delivery | None:
        row = self._connection.execute(
            "SELECT id, destination, weight, priority FROM shipments WHERE id = ?",
            (delivery_id,),
        ).fetchone()
        if row is None:
            return None
        return Delivery(
            id=row[0], destination=row[1], weight=row[2], priority=DeliveryPriority[row[3]]
        )

    def close(self) -> None:
        self._connection.close()

    def save_dispatch(self, record: DispatchRecord) -> None:
        # Persist the delivery and its dispatch state in the same transaction.
        with self._connection:
            self._save_delivery(record.delivery)
            self._connection.execute(
                """
                INSERT INTO dispatches (
                    delivery_id, destination, weight, priority, courier_name,
                    quote, status, tracking_number, courier_reference
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(delivery_id) DO UPDATE SET
                    destination = excluded.destination,
                    weight = excluded.weight,
                    priority = excluded.priority,
                    courier_name = excluded.courier_name,
                    quote = excluded.quote,
                    status = excluded.status,
                    tracking_number = excluded.tracking_number,
                    courier_reference = excluded.courier_reference
                """,
                (
                    record.delivery.id,
                    record.delivery.destination,
                    record.delivery.weight,
                    record.delivery.priority.name,
                    record.courier_name,
                    record.quote,
                    record.status.name,
                    record.booking.tracking_number if record.booking else None,
                    record.booking.courier_reference if record.booking else None,
                ),
            )

    def get_dispatch(self, delivery_id: str) -> DispatchRecord | None:
        row = self._connection.execute(
            """
            SELECT delivery_id, destination, weight, priority, courier_name,
                   quote, status, tracking_number, courier_reference
            FROM dispatches WHERE delivery_id = ?
            """,
            (delivery_id,),
        ).fetchone()
        if row is None:
            return None
        return DispatchRecord(
            delivery=Delivery(
                id=row[0], destination=row[1], weight=row[2],
                priority=DeliveryPriority[row[3]],
            ),
            courier_name=row[4],
            quote=row[5],
            status=DispatchStatus[row[6]],
            booking=BookingResult(row[7], row[8]) if row[7] is not None else None,
        )
