try:
    from dragons.dragon import Dragon
except ModuleNotFoundError:
    from dragon import Dragon


def main():
    ember = Dragon("Ember", "Fire", 100, 50)
    print(ember.status())
    print(ember.fly())
    print(ember.attack())
    print(ember.feed(20))
    print(ember.status())


if __name__ == "__main__":
    main()
