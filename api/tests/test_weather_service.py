from api.notifier import ConsoleNotifier


def test_console_notifier_prints_message(capsys):
    notifier = ConsoleNotifier()
    test_message = "Test notification message"
    notifier.notify(test_message)

    captured = capsys.readouterr()
    print(f"Captured output: {captured.out.strip()}")  # Debugging line
    assert captured.out.strip() == test_message
