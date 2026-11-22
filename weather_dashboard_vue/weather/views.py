from django.middleware.csrf import get_token
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.http import require_GET

from .api.serializers import ForecastSerializer
from .api.pagination import ForecastPagination
from .models import Forecast


@require_GET
def index(request):
    forecasts = Forecast.objects.order_by("-fetched_at", "-pk")
    pagination = ForecastPagination()
    page = pagination.paginate_initial_queryset(forecasts, request)
    return render(request, "weather/index.html", {
        "initial_data": {
            **pagination.payload(ForecastSerializer(page, many=True).data),
            "csrfToken": get_token(request),
            "forecastsUrl": reverse("forecast-list"),
            "fetchUrl": reverse("forecast-fetch"),
        },
    })
