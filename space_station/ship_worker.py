import argparse
from queue import Empty

from ship import Ship
from transport import connection_arguments, make_manager


class ShipWorker:
    """Executes commands only; all simulation timing belongs to main.py."""

    def __init__(self, name):
        self.ship = Ship(name)

    def execute(self, command):
        action, delivery = command
        if action == "pickup":
            if not self.ship.is_available_for_delivery():
                raise RuntimeError("Ship already has cargo")
            self.ship.pickup_delivery(delivery)
            print(f"{self.ship.name} picked up delivery {delivery.delivery_id}", flush=True)
            return None
        if action == "unload":
            cargo = self.ship.drop_delivery(delivery.delivery_id)
            if cargo is None:
                raise RuntimeError(f"Delivery {delivery.delivery_id} is not aboard")
            print(f"{self.ship.name} unloaded delivery {cargo.delivery_id}", flush=True)
            return cargo
        raise ValueError(f"Unknown command: {action}")

    def run(self, mailboxes):
        mailboxes.register(self.ship.name)
        print(f"{self.ship.name} connected; waiting for commands.", flush=True)
        while True:
            try:
                command = mailboxes.receive(self.ship.name, 1)
            except Empty:
                continue
            if command is None:
                mailboxes.report((self.ship.name, None, None, None))
                return
            command_id, action, delivery = command
            try:
                cargo = self.execute((action, delivery))
            except Exception as error:
                mailboxes.report((self.ship.name, command_id, None, str(error)))
            else:
                mailboxes.report((self.ship.name, command_id, cargo, None))


def main():
    parser = argparse.ArgumentParser(description="Run one ship in its own terminal")
    connection_arguments(parser)
    parser.add_argument("--name", required=True)
    args = parser.parse_args()
    manager = make_manager(args.port, args.authkey)
    try:
        manager.connect()
        ShipWorker(args.name).run(manager.mailboxes())
    except (ConnectionError, EOFError, OSError) as error:
        parser.exit(1, f"Connection to simulation lost or unavailable: {error}\n")
    except KeyboardInterrupt:
        parser.exit(130, "Worker stopped.\n")


if __name__ == "__main__":
    main()
