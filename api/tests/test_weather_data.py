from dataclasses import replace

import pytest

from api.data import LongLat, WeatherForecast


@pytest.mark.parametrize("field", ["latitude", "longitude"])
@pytest.mark.parametrize("value", ["51.5", None, []])
def test_coordinates_reject_non_numeric_values(field: str, value: object):
    with pytest.raises(ValueError, match="must be numeric"):
        replace(LongLat(51.5, -0.1), **{field: value})


@pytest.mark.parametrize("latitude,longitude", [(0, 0), (90.0, 180.0), (-90.0, -180.0)])
def test_coordinates_accept_numeric_values(latitude: float, longitude: float):
    location = LongLat(latitude, longitude)
    assert location.latitude == latitude
    assert location.longitude == longitude


@pytest.mark.parametrize("field", ["temperature", "humidity", "wind_speed"])
@pytest.mark.parametrize("value", ["10.0", None, []])
def test_forecast_rejects_non_numeric_measurements(field: str, value: object):
    with pytest.raises(ValueError, match="must be numeric"):
        replace(WeatherForecast(15.0, 60.0, 5.0, "Cloudy"), **{field: value})


@pytest.mark.parametrize("value", [10, None, []])
def test_forecast_rejects_non_text_description(value: object):
    with pytest.raises(ValueError, match="Description must be a string"):
        replace(WeatherForecast(15.0, 60.0, 5.0, "Cloudy"), description=value)
