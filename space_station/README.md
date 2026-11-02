# Space station simulation

Run the central simulation first, then launch each ship in a separate terminal.
Run these commands from the repository root:

```sh
# Terminal 1: owns the simulation clock and station
python3 space_station/main.py

# Terminal 2
python3 space_station/ship_worker.py --name rocinante

# Terminal 3 (optional: another ship speeds up pending deliveries)
python3 space_station/ship_worker.py --name serenity
```

Main starts when the first ship connects. One ship completes all deliveries
sequentially; additional ships can join between ticks and take pending deliveries.
Ships exit automatically when the run finishes. Restart main and your workers for
another run. No external dependencies are required.

## How it works

Main starts a `multiprocessing.managers.BaseManager` server exposing command and
acknowledgement mailboxes. Each independently launched worker connects and
registers its unique name. Main assigns pending deliveries to available ships;
deliveries have no ship assigned up front.

Only `main.py` counts ticks and calculates arrival times. It sends pickup or
unload commands to workers and waits for all acknowledgements before advancing.
Workers execute commands without knowing the current tick. The default trip takes
two ticks: pickup at tick 0 and unload at tick 2. Main updates station supplies
only after an unload is acknowledged. Main pauses one second between ticks by
default so you can watch progress and connect additional ships. With the sample
deliveries, one ship finishes at tick 5; two ships starting together finish at
tick 2. Use `--tick-seconds 0` to run without pauses.

## Options

- `main.py --workers 2`: wait for two workers before starting (default: one).
- `main.py --tick-seconds 0.5`: pause half a second between ticks.
- `main.py --travel-ticks 5`: use five ticks per journey.
- `main.py --startup-timeout 120`: seconds allowed for workers to register.
- `main.py --worker-timeout 10`: seconds allowed for command acknowledgements.
- `--port 50001`: choose another port; pass it to main and every worker.

The server binds to localhost. The default authentication key is for this local
example. Set the same `SPACE_STATION_AUTHKEY` environment variable in every
terminal to change it, or pass `--authkey` to each command.

State is in memory and is lost when main exits. A missing or failed worker aborts
the simulation with an error; deliveries are not automatically retried.

## Tests

From the `space_station` directory:

```sh
python3 -m unittest discover -s tests -v
```

The tests launch main with one and two worker processes and verify that a single
worker delivers the same supplies but needs more ticks.
