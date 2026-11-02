import io
from pathlib import Path
from queue import Empty
import subprocess
import sys
import unittest
from contextlib import redirect_stdout

from delivery import Delivery
from main import simulate
from ship_worker import ShipWorker
from station import SpaceStation
from supply_type import SupplyType
from transport import Mailboxes


class ShipWorkerTests(unittest.TestCase):
    def test_cargo_waits_for_unload_command(self):
        worker = ShipWorker("rocinante")
        delivery = Delivery(SupplyType.FOOD, 100, delivery_id=1)
        worker.execute(("pickup", delivery))
        self.assertFalse(worker.ship.is_available_for_delivery())
        self.assertEqual(worker.execute(("unload", delivery)), delivery)
        self.assertTrue(worker.ship.is_available_for_delivery())
        self.assertEqual(worker.ship.supplies[SupplyType.FOOD], 0)

    def test_cannot_unload_missing_delivery(self):
        with self.assertRaisesRegex(RuntimeError, "not aboard"):
            ShipWorker("rocinante").execute(("unload", Delivery(SupplyType.FOOD, 100)))

    def test_duplicate_worker_names_are_rejected(self):
        mailboxes = Mailboxes()
        mailboxes.register("rocinante")
        with self.assertRaisesRegex(ValueError, "already registered"):
            mailboxes.register("rocinante")

    def test_main_owns_travel_ticks(self):
        worker = ShipWorker("rocinante")
        output = io.StringIO()
        actions = []

        class ImmediateMailboxes(Mailboxes):
            def send(self, name, command):
                command_id, action, delivery = command
                actions.append((action, output.getvalue().splitlines()[-1]))
                cargo = worker.execute((action, delivery))
                self.report((name, command_id, cargo, None))

        station = SpaceStation("Test")
        with redirect_stdout(output):
            simulate(ImmediateMailboxes(), ["rocinante"],
                     [Delivery(SupplyType.FOOD, 100)], station, travel_ticks=3, timeout=1)
        self.assertEqual(actions, [("pickup", "Time 0:"), ("unload", "Time 3:")])
        self.assertEqual(station.get_supply_quantity(SupplyType.FOOD), 100)

    def test_missing_acknowledgement_has_timeout(self):
        class SilentMailboxes(Mailboxes):
            def send(self, name, command):
                pass

            def next_result(self, timeout):
                raise Empty

        with self.assertRaisesRegex(RuntimeError, "Timed out waiting for: lost-ship"):
            simulate(SilentMailboxes(), ["lost-ship"], [Delivery(SupplyType.FOOD, 100)],
                     SpaceStation("Test"), travel_ticks=2, timeout=0.1)

    def test_second_worker_can_join_after_start(self):
        ships = {name: ShipWorker(name) for name in ("rocinante", "serenity")}

        class JoiningMailboxes(Mailboxes):
            def send(self, name, command):
                command_id, action, delivery = command
                cargo = ships[name].execute((action, delivery))
                self.report((name, command_id, cargo, None))
                if command_id == 1:
                    self.register("serenity")

        station = SpaceStation("Test")
        workers = ["rocinante"]
        output = io.StringIO()
        with redirect_stdout(output):
            simulate(JoiningMailboxes(), workers,
                     [Delivery(SupplyType.FOOD, 100, 1), Delivery(SupplyType.FUEL, 50, 2)],
                     station, travel_ticks=2, timeout=1)
        self.assertEqual(workers, ["rocinante", "serenity"])
        self.assertIn("Time 3:", output.getvalue())
        self.assertNotIn("Time 4:", output.getvalue())
        self.assertEqual(station.get_supply_quantity(SupplyType.FOOD), 100)
        self.assertEqual(station.get_supply_quantity(SupplyType.FUEL), 50)

    def test_separate_terminal_processes(self):
        self.run_terminal_processes(("rocinante", "serenity"), ["--workers", "2"], 2)

    def test_single_worker_completes_with_more_ticks(self):
        self.run_terminal_processes(("rocinante",), [], 5)

    def run_terminal_processes(self, names, options, final_tick):
        directory = Path(__file__).resolve().parents[1]
        processes = []
        try:
            central = subprocess.Popen(
                [sys.executable, "main.py", "--port", "0", "--startup-timeout", "10",
                 "--tick-seconds", "0", *options],
                cwd=directory, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
            )
            processes.append(central)
            assert central.stdout is not None
            address = central.stdout.readline().strip()
            self.assertTrue(address.startswith("Manager listening on"), address)
            port = address.rsplit(":", 1)[1]
            for name in names:
                processes.append(subprocess.Popen(
                    [sys.executable, "ship_worker.py", "--name", name, "--port", port],
                    cwd=directory, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                ))
            output, _ = central.communicate(timeout=20)
            self.assertEqual(central.returncode, 0, output)
            self.assertIn(f"Time {final_tick}:", output)
            self.assertNotIn(f"Time {final_tick + 1}:", output)
            self.assertIn("All deliveries completed.", output)
            self.assertIn("FOOD: 100", output)
            self.assertIn("FUEL: 50", output)
            for process in processes[1:]:
                worker_output, _ = process.communicate(timeout=5)
                self.assertEqual(process.returncode, 0, worker_output)
                self.assertIn("picked up delivery", worker_output)
                self.assertIn("unloaded delivery", worker_output)
        finally:
            for process in processes:
                if process.poll() is None:
                    process.kill()
                process.communicate()


if __name__ == "__main__":
    unittest.main()
