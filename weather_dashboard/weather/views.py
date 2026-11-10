import requests
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render

from api.data import LongLat
from api.provider import ApiWeatherProvider
from api.provider.photon_location_provider import PhotonLocationProvider

from .forms import WeatherForm
from .models import Forecast


def index(request: HttpRequest) -> HttpResponse:
    form = WeatherForm(request.POST if request.method == "POST" else None)
    error = None

    if request.method == "POST" and form.is_valid():
        location = LongLat(
            latitude=form.cleaned_data["latitude"],
            longitude=form.cleaned_data["longitude"],
        )

        try:
            forecast = ApiWeatherProvider().get_weather(location)
            location_name = (
                PhotonLocationProvider().get_location_name(location)
                or "Location name unavailable"
            )
        except requests.RequestException:
            error = "Weather is unavailable. Please try again."
        else:
            Forecast.objects.create(
                location_name=location_name,
                latitude=location.latitude,
                longitude=location.longitude,
                temperature=forecast.temperature,
                humidity=forecast.humidity,
                wind_speed=forecast.wind_speed,
                description=forecast.description,
            )
            return redirect("index")

    forecasts = Forecast.objects.order_by("-fetched_at", "-pk")[:20]
    latest_forecast = forecasts.first()

    return render(
        request,
        "weather/index.html",
        {
            "form": form,
            "forecasts": forecasts,
            "forecast": latest_forecast,
            "location_name": latest_forecast.location_name if latest_forecast else None,
            "error": error,
        },
    )
