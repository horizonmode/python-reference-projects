from rest_framework.exceptions import APIException, ValidationError
from rest_framework.views import exception_handler


class WeatherUnavailable(APIException):
    status_code = 502
    default_detail = "Weather is unavailable. Please try again."
    default_code = "weather_unavailable"


def api_exception_handler(exc, context):
    """Expose DRF errors using the Vue client's existing error contract."""
    response = exception_handler(exc, context)
    if response is None:
        return None
    if isinstance(exc, ValidationError):
        response.data = {"error": "Check the fields below.", "errors": response.data}
    else:
        detail = response.data.get("detail", "Request failed.") if isinstance(response.data, dict) else "Request failed."
        response.data = {"error": detail}
    return response
