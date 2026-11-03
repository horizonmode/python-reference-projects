from .notifier import Notifier


class ConsoleNotifier(Notifier):
    def notify(self, message: str) -> None:
        print(message)
