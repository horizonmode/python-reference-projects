from queue import Queue

from delivery import Delivery
from dock_manager import DockManager
from ship import Ship
from station import SpaceStation
from supply_type import SupplyType

station = SpaceStation("International Space Station")
dock_manager = DockManager("Dock Manager", station)

ship1 = Ship("rocinante")
ship2 = Ship("serenity")

ship_roster = [ship1, ship2]

delivery1 = Delivery(ship1, SupplyType.FOOD, 100)
delivery2 = Delivery(ship2, SupplyType.FUEL, 50)

delivery_queue = Queue()
delivery_queue.put(delivery1)
delivery_queue.put(delivery2)

time_step = 0
time_interval = 1

finished = (
    ship1.is_available_for_delivery()
    and ship2.is_available_for_delivery()
    and delivery_queue.empty()
)


def do_action():
    for ship in ship_roster:
        if not ship.is_available_for_delivery():
            delivery = ship.drop_next_delivery()
            if delivery:
                dock_manager.unload_ship(ship, delivery.delivery_id)
                print(
                    f"Time {time_step}: {ship.name} dropped off {delivery.quantity} of {delivery.supply_type.name}"
                )
                continue
        else:
            if not delivery_queue.empty():
                delivery = delivery_queue.get()
                ship.pickup_delivery(delivery)
                print(
                    f"Time {time_step}: {ship.name} picked up {delivery.quantity} of {delivery.supply_type.name}"
                )
                continue


print("Starting delivery simulation...")

while not finished:
    do_action()
    time_step += time_interval
    finished = (
        ship1.is_available_for_delivery()
        and ship2.is_available_for_delivery()
        and delivery_queue.empty()
    )

print("All deliveries completed.")
