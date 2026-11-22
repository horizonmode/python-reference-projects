from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from weather.models import Forecast
from weather.services import WeatherProviderError, fetch_forecast_data

from .exceptions import WeatherUnavailable
from .pagination import ForecastPagination
from .serializers import CoordinatesSerializer, ForecastSerializer


class ForecastViewSet(viewsets.ModelViewSet):
    queryset = Forecast.objects.order_by("-fetched_at", "-pk")
    serializer_class = ForecastSerializer
    pagination_class = ForecastPagination

    def list(self, request, *args, **kwargs):
        page = self.paginate_queryset(self.filter_queryset(self.get_queryset()))
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)
        response.data = {"forecast": response.data}
        return response

    def update(self, request, *args, **kwargs):
        # DRF's partial_update also uses this method with partial=True.
        response = super().update(request, *args, **kwargs)
        response.data = {"forecast": response.data}
        return response

    @action(
        detail=False,
        methods=["post"],
        url_path="fetch",
        serializer_class=CoordinatesSerializer,
    )
    def fetch(self, request):
        coordinates = self.get_serializer(data=request.data)
        coordinates.is_valid(raise_exception=True)
        try:
            data = fetch_forecast_data(**coordinates.validated_data)
        except WeatherProviderError as exc:
            raise WeatherUnavailable from exc
        serializer = ForecastSerializer(data=data)
        if not serializer.is_valid():
            raise WeatherUnavailable("The weather provider returned invalid data.")
        serializer.save()
        return Response({"forecast": serializer.data}, status=status.HTTP_201_CREATED)
