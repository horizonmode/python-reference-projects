import argparse
from collections import deque
from queue import Empty
from time import monotonic, sleep

from delivery import Delivery
from station import SpaceStation
from supply_type import SupplyType
from transport import connection_arguments, make_manager


def positive_int(value):
    number = int(value)
    if number < 1:
        raise argparse.ArgumentTypeError("must be at least 1")
    return number


def wait_for_workers(mailboxes, count, timeout, workers):
    deadline = monotonic() + timeout
    while len(workers) < count:
        try:
            name = mailboxes.next_registration(max(0, deadline - monotonic()))
        except Empty:
            raise RuntimeError(
                f"Timed out waiting for workers ({len(workers)}/{count} connected)"
            ) from None
        workers.append(name)
        print(f"Worker connected: {name} ({len(workers)}/{count})", flush=True)


def simulate(
    mailboxes, workers, deliveries, station, travel_ticks, timeout, tick_seconds=0
):
    pending = deque(deliveries)
    in_transit = {}
    time_step = 0
    command_id = 0
    while pending or in_transit:
        # Admit additional ships between ticks without holding up the simulation.
        while True:
            try:
                name = mailboxes.next_registration(0)
            except Empty:
                break
            workers.append(name)
            print(f"Worker connected: {name}", flush=True)
        print(f"Time {time_step}:", flush=True)
        expected = {}
        for name in workers:
            if name in in_transit:
                delivery, arrival = in_transit[name]
                if time_step < arrival:
                    continue
                action = "unload"
            elif pending:
                delivery = pending.popleft()
                action = "pickup"
            else:
                continue
            command_id += 1
            expected[name] = (command_id, action, delivery)
            mailboxes.send(name, (command_id, action, delivery))

        # A wall-clock timeout detects missing workers; it does not advance ticks.
        deadline = monotonic() + timeout
        while expected:
            try:
                name, result_id, cargo, error = mailboxes.next_result(
                    max(0, deadline - monotonic())
                )
            except Empty:
                raise RuntimeError(
                    f"Timed out waiting for: {', '.join(expected)}"
                ) from None
            if name not in expected or result_id != expected[name][0]:
                raise RuntimeError(f"Unexpected acknowledgement from {name}")
            _, action, delivery = expected.pop(name)
            if error is not None:
                raise RuntimeError(f"{name}: {error}")
            if action == "pickup":
                in_transit[name] = (delivery, time_step + travel_ticks)
            else:
                if cargo != delivery:
                    raise RuntimeError(f"{name} returned the wrong delivery")
                station.receive_delivery(cargo)
                del in_transit[name]
        time_step += 1
        if tick_seconds and (pending or in_transit):
            sleep(tick_seconds)


def stop_workers(mailboxes, workers, timeout):
    remaining = set(workers)
    for name in workers:
        mailboxes.send(name, None)
    deadline = monotonic() + timeout
    while remaining:
        try:
            name, command_id, _, _ = mailboxes.next_result(
                max(0, deadline - monotonic())
            )
        except Empty:
            return
        if command_id is None:
            remaining.discard(name)


def main():
    parser = argparse.ArgumentParser(description="Central space station simulation")
    connection_arguments(parser)
    parser.add_argument(
        "--workers",
        type=positive_int,
        default=1,
        help="minimum number of workers needed to start (default: 1)",
    )
    parser.add_argument("--travel-ticks", type=positive_int, default=2)
    parser.add_argument(
        "--tick-seconds",
        type=float,
        default=1,
        help="pause between ticks in seconds; 0 runs at full speed",
    )
    parser.add_argument("--startup-timeout", type=float, default=120)
    parser.add_argument("--worker-timeout", type=float, default=10)
    args = parser.parse_args()
    if args.startup_timeout <= 0 or args.worker_timeout <= 0:
        parser.error("timeouts must be positive")
    if args.tick_seconds < 0:
        parser.error("--tick-seconds must be nonnegative")
    station = SpaceStation("International Space Station")
    deliveries = [
        Delivery(SupplyType.FOOD, 100, delivery_id=1),
        Delivery(SupplyType.FUEL, 50, delivery_id=2),
        Delivery(SupplyType.MEDICAL, 25, delivery_id=3),
        Delivery(SupplyType.FOOD, 75, delivery_id=4),
        Delivery(SupplyType.FUEL, 100, delivery_id=5),
        Delivery(SupplyType.MEDICAL, 50, delivery_id=6),
    ]
    workers = []
    try:
        with make_manager(args.port, args.authkey) as manager:
            mailboxes = manager.mailboxes()
            address = manager.address
            if not isinstance(address, tuple):
                raise RuntimeError("Manager did not start with a TCP address")
            print(f"Manager listening on 127.0.0.1:{address[1]}", flush=True)
            print(f"Waiting for {args.workers} workers...", flush=True)
            try:
                wait_for_workers(mailboxes, args.workers, args.startup_timeout, workers)
                simulate(
                    mailboxes,
                    workers,
                    deliveries,
                    station,
                    args.travel_ticks,
                    args.worker_timeout,
                    args.tick_seconds,
                )
                print("All deliveries completed.", flush=True)
                for supply_type in station.supplies:
                    print(
                        f"{supply_type.name}: {station.get_supply_quantity(supply_type)}",
                        flush=True,
                    )
            finally:
                stop_workers(mailboxes, workers, args.worker_timeout)
    except (RuntimeError, OSError, EOFError) as error:
        parser.exit(1, f"Simulation failed: {error}\n")
    except KeyboardInterrupt:
        parser.exit(130, "Simulation stopped.\n")


if __name__ == "__main__":
    main()
