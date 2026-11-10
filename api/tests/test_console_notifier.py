import pytest

from api.notifier import ConsoleNotifier


@pytest.mark.parametrize("message", ["Test notification", "Rain expected ☂", ""])
def test_console_notifier_prints_message(message: str, capsys: pytest.CaptureFixture[str]):
    ConsoleNotifier().notify(message)
    captured = capsys.readouterr()
    assert captured.out == message + "\n"
    assert captured.err == ""
