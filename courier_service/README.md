# Courier service

A Python 3.10+ project demonstrating dependency injection with courier selection,
notifications, and interchangeable in-memory and SQLite shipment repositories.

## Set up

From the `courier_service` directory:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]' -c requirements-dev.lock
```

On Windows, activate with `.venv\Scripts\activate` instead.

The editable install uses the local source files directly. Project metadata and
dependencies are declared in `pyproject.toml`. The `dev` extra installs pytest
and Pyright. `requirements-dev.lock` pins their transitive dependencies to the
versions tested with Python 3.13. The application itself needs no third-party
dependencies: SQLite
is provided by Python's standard-library `sqlite3` module.

For an installation without development tools, use `python -m pip install -e .`.

## Run

```sh
python main.py
```

Install the project once before running the wrapper. You can also use the
installed command or module entry point, from any directory:

```sh
courier-dispatch
python -m courier_service
```

Each command dispatches a sample delivery and saves it in `shipments.sqlite3` in
the current working directory, outside the installed package. To choose a
different database:

```sh
python main.py --database another.sqlite3
```

## Check

```sh
python -m pytest
pyright
```

Tests import the installed `courier_service` package; pytest does not add `src`
to the import path. They cover repository behaviour, SQLite persistence, dispatch
retries, and all three entry points from another working directory.

After installing the project, the tests can also run without third-party test
tools:

```sh
python -m unittest discover -s tests -v
```

## Retrying dispatch

Call `dispatch_service.dispatch(delivery)` again with the same delivery ID and
details to retry a failed dispatch. A new ID represents a new shipment; running
the sample script again creates a new delivery rather than retrying the old one.

Dispatch progresses through persisted checkpoints:

1. `BOOKING_PENDING`: save the delivery, chosen courier, and quote before booking.
2. `BOOKED`: save the tracking number and courier reference before notifying.
3. `NOTIFIED`: record successful notification; further calls return the original
   `DispatchResult` without booking or notifying again.

Booking requests use the delivery ID as their idempotency key. If a booking
response is lost or its local save fails, a retry asks the same courier using the
same key. Notification failures resume from `BOOKED` without booking again.
Changing delivery details while reusing an existing dispatch ID is rejected.

SQLite stores checkpoints in a new `dispatches` table alongside the existing
`shipments` table. Existing shipment data is preserved. In-memory repository
checkpoints last only for the lifetime of that repository instance.

This example supports sequential retries. Its demo courier caches idempotency
results in memory, so a pending booking whose result was not saved cannot be
deduplicated after recreating that courier. A real courier adapter must forward
the key to a provider that durably enforces idempotency. Saved `BOOKED` records
can resume notifications after reopening SQLite without contacting a courier.

Notifications may repeat if sending succeeds but recording `NOTIFIED` fails.
Exactly-once notification delivery and concurrent dispatch coordination are
outside this example's scope.

## Packaging

Build a wheel from the project directory:

```sh
python -m pip wheel --no-deps . --wheel-dir dist
```

The wheel contains only the named `courier_service` package. Tests, the root
wrapper, virtual environments, and SQLite files are not installed as application
modules. A regular wheel install can run `courier-dispatch` and
`python -m courier_service` without access to the source tree.

When intentionally updating development dependencies, use a clean virtual
environment, install the updated `.[dev]` extra without the constraints, run the
checks, then regenerate the pins:

```sh
python -m pip freeze --exclude courier-service-example > requirements-dev.lock
```

The build backend is specified separately under `[build-system]` in
`pyproject.toml`; the lock file pins development tools, not the Python interpreter
or build-isolation environment.

## Structure

```text
courier_service/
├── pyproject.toml
├── requirements-dev.lock
├── main.py                      # Local wrapper for the installed package
├── src/
│   └── courier_service/
│       ├── __init__.py
│       ├── __main__.py           # python -m courier_service
│       ├── cli.py                # CLI and dependency construction
│       ├── dispatch_service.py
│       ├── couriers/
│       ├── delivery/
│       ├── notifiers/
│       └── repositories/
└── tests/
```
