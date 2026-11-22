import math
from collections.abc import Mapping

from rest_framework import serializers

from weather.models import Forecast


class FiniteFloatField(serializers.FloatField):
    def to_internal_value(self, data):
        if isinstance(data, bool):
            self.fail("invalid")
        value = super().to_internal_value(data)
        if not math.isfinite(value):
            raise serializers.ValidationError("Enter a finite number.")
        return value


class ExplicitInputSerializer(serializers.Serializer):
    """Reject typos and attempts to write server-controlled fields."""

    def to_internal_value(self, data):
        if isinstance(data, Mapping):
            writable = {name for name, field in self.fields.items() if not field.read_only}
            invalid = set(data) - writable
            if invalid:
                raise serializers.ValidationError({
                    name: ["Unknown or read-only field."] for name in sorted(invalid)
                })
        return super().to_internal_value(data)


class CoordinatesSerializer(ExplicitInputSerializer):
    latitude = FiniteFloatField(min_value=-90, max_value=90)
    longitude = FiniteFloatField(min_value=-180, max_value=180)


class ForecastSerializer(ExplicitInputSerializer, serializers.ModelSerializer):
    latitude = FiniteFloatField(min_value=-90, max_value=90)
    longitude = FiniteFloatField(min_value=-180, max_value=180)
    temperature = FiniteFloatField()
    humidity = FiniteFloatField(min_value=0, max_value=100)
    wind_speed = FiniteFloatField(min_value=0)

    # DRF declares Meta in its stubs, but it has no runtime base Meta to inherit.
    class Meta:  # pyright: ignore[reportIncompatibleVariableOverride]
        model = Forecast
        fields = (
            "id", "location_name", "latitude", "longitude", "temperature",
            "humidity", "wind_speed", "description", "fetched_at",
        )
        read_only_fields = ("id", "fetched_at")
