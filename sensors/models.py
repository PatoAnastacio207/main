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
    typicalParticleSize = models.PositiveSmallIntegerField()

    def __str__(self):
            return f"{self.pm1} {self.pm25} {self.pm4} {self.pm10}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    class Meta:
         ordering = ["-timestamp"]
