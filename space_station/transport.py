"""Manager-backed mailboxes shared by independently launched processes."""
import argparse
import os
from multiprocessing.managers import BaseManager
from queue import Queue
from threading import Lock
from typing import TYPE_CHECKING


class Mailboxes:
    def __init__(self):
        self.registrations = Queue()
        self.results = Queue()
        self.commands = {}
        self.lock = Lock()

    def register(self, name):
        with self.lock:
            if name in self.commands:
                raise ValueError(f"Worker {name!r} is already registered")
            self.commands[name] = Queue()
        self.registrations.put(name)

    def next_registration(self, timeout):
        return self.registrations.get(timeout=timeout)

    def send(self, name, command):
        self.commands[name].put(command)

    def receive(self, name, timeout):
        return self.commands[name].get(timeout=timeout)

    def report(self, result):
        self.results.put(result)

    def next_result(self, timeout):
        return self.results.get(timeout=timeout)


_mailboxes = None


def get_mailboxes():
    global _mailboxes
    if _mailboxes is None:
        _mailboxes = Mailboxes()
    return _mailboxes


class SimulationManager(BaseManager):
    if TYPE_CHECKING:
        # register() creates this method at runtime; declare its interface for IDEs.
        def mailboxes(self) -> Mailboxes: ...


SimulationManager.register("mailboxes", callable=get_mailboxes)


def connection_arguments(parser: argparse.ArgumentParser):
    parser.add_argument("--port", type=int, default=50000)
    parser.add_argument(
        "--authkey", default=os.environ.get("SPACE_STATION_AUTHKEY", "space-station-demo")
    )


def make_manager(port, authkey):
    return SimulationManager(address=("127.0.0.1", port), authkey=authkey.encode())
