from django.db import models


class Forecast(models.Model):
    location_name = models.CharField(max_length=200)
    latitude = models.FloatField()
    longitude = models.FloatField()

    temperature = models.FloatField()
    humidity = models.FloatField()
    wind_speed = models.FloatField()
    description = models.CharField(max_length=200)

    fetched_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.location_name} — {self.fetched_at}"
