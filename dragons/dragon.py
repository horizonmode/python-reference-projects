class Dragon:

    MAX_ENERGY = 100
    MAX_HUNGER = 100
    FLY_ENERGY_COST = 20
    FLY_HUNGER_GAIN = 10
    ATTACK_POWER = 10

    def __init__(self, name, element, energy=MAX_ENERGY, hunger=0):
        if not 0 <= energy <= self.MAX_ENERGY:
            raise ValueError(
                f"Energy must be between 0 and {self.MAX_ENERGY}"
            )
        if not 0 <= hunger <= self.MAX_HUNGER:
            raise ValueError(
                f"Hunger must be between 0 and {self.MAX_HUNGER}"
            )

        self.name = name
        self.element = element
        self._energy = energy
        self.hunger = hunger

    @property
    def energy(self):
        return self._energy

    def fly(self):
        if self.energy >= self.FLY_ENERGY_COST:
            self._energy -= self.FLY_ENERGY_COST
            self.hunger = min(
                self.MAX_HUNGER,
                self.hunger + self.FLY_HUNGER_GAIN,
            )
            return f"{self.name} flies through the sky! Energy left: {self.energy}, Hunger: {self.hunger}"
        else:
            return f"{self.name} is too tired to fly."

    def attack(self):
        if self.energy >= self.ATTACK_POWER:
            self._energy -= self.ATTACK_POWER
            return f"{self.name} attacks with {self.element} power! Energy left: {self.energy}"
        else:
            return f"{self.name} is too tired to attack."

    def feed(self, food):
        if food <= 0:
            raise ValueError("Food must be positive")

        if self.hunger > 0:
            self.hunger -= food
            if self.hunger < 0:
                self.hunger = 0
            return f"{self.name} has been fed. Hunger level: {self.hunger}"
        else:
            return f"{self.name} is not hungry."

    def status(self):
        return f"{self.name} - Element: {self.element}, Energy: {self.energy}, Hunger: {self.hunger}"
