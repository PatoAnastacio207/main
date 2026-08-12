from django.db import models


class Sps30Data(models.Model):
    timestamp = models.DateTimeField()
    pm1 = models.PositiveSmallIntegerField()
    pm25 = models.PositiveSmallIntegerField()
    pm4 = models.PositiveSmallIntegerField()
    pm10 = models.PositiveSmallIntegerField()
    nc0 = models.PositiveSmallIntegerField()
    nc1 = models.PositiveSmallIntegerField()
    nc25 = models.PositiveSmallIntegerField()
    nc4 = models.PositiveSmallIntegerField()
    nc10 = models.PositiveSmallIntegerField()
    typical_particle_size = models.PositiveSmallIntegerField()

    def __str__(self):
        return f"{self.pm1} {self.pm25} {self.pm4} {self.pm10}"

    class Meta:
        ordering = ["-timestamp"]


class WeatherData(models.Model):
    timestamp = models.DateTimeField()
    temperature = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    humidity = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    pressure = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
    wind_direction = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        help_text="Wind direction in degrees, 0-359",
    )
    wind_speed = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    sps30_data = models.OneToOneField(
        Sps30Data,
        on_delete=models.CASCADE,
        related_name="weather_data",
        null=True,
        blank=True,
    )

    def __str__(self):
        return f"Weather at {self.timestamp}"

    class Meta:
        ordering = ["-timestamp"]
