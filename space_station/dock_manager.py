class DockManager:
    def __init__(self, name, space_station):
        self.name = name
        self.space_station = space_station

    def unload_ship(self, ship, delivery_id):
        delivery = ship.drop_delivery(delivery_id)
        if delivery:
            self.space_station.receive_delivery(delivery)
            return True
        return False
