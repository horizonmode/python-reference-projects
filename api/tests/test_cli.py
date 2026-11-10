import pytest

from api import main
from api.provider import DummyWeatherProvider


@pytest.fixture(autouse=True)
def offline_providers(monkeypatch):
    monkeypatch.setattr("api.ApiWeatherProvider", DummyWeatherProvider)
    monkeypatch.setattr(
        "api.PhotonLocationProvider.get_location_name",
        lambda self, location: "London, United Kingdom",
    )


def test_cli_reports_weather_for_entered_coordinates(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str],
):
    monkeypatch.setattr("builtins.input", lambda prompt: "51.5,-0.1")
    main()
    output = capsys.readouterr().out
    assert "Weather data for London, United Kingdom:" in output
    assert "LongLat(" not in output
    assert "Sunny" in output
    assert "Location: London, United Kingdom" in output.splitlines()
    assert "London, United Kingdom" in output
    assert "Invalid input" not in output


@pytest.mark.parametrize("invalid_input", ["not-coordinates", "north,west", "1,2,3"])
def test_cli_reports_bad_input_and_accepts_next_attempt(
    invalid_input: str, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str],
):
    responses = iter([invalid_input, "51.5,-0.1"])
    monkeypatch.setattr("builtins.input", lambda prompt: next(responses))
    main()
    output = capsys.readouterr().out
    assert output.count("Invalid input.") == 1
    assert output.count("Weather data for") == 1
    assert "Weather data for London, United Kingdom:" in output
    assert "LongLat(" not in output
