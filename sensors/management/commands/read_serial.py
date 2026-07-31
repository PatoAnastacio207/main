import time
import serial
from django.utils import timezone
from django.core.cache import cache
from django.core.management.base import BaseCommand
from sensors.models import Sps30Data

SERIAL_PORT = "/dev/ttyACM0"
BAUD_RATE = 115200
CACHE_KEY = "arduino_latest_reading"
DATA_PREFIX = "DATA,"


class Command(BaseCommand):
    help = "Continuously reads Arduino serial output and caches the latest value"

    def handle(self, *args, **options):
        while True:
            try:
                self.stdout.write(f"Connecting to {SERIAL_PORT}...")
                with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1) as ser:
                    self.stdout.write(self.style.SUCCESS("Connected"))

                    while True:
                        line = ser.readline().decode("utf-8", errors="ignore").strip()
                        if not line:
                            continue

                        if line.startswith(DATA_PREFIX):
                            _, pm1, pm25, pm4, pm10, nc0, nc1, nc25, nc4, nc10, typicalParticleSize = line.split(',')

                            Sps30Data.objects.create(
                                pm1=pm1, 
                                pm25=pm25, 
                                pm4=pm4, 
                                pm10=pm10, 
                                nc0=nc0,
                                nc1=nc1, 
                                nc25=nc25,
                                nc4=nc4,
                                nc10=nc10,
                                typicalParticleSize=typicalParticleSize,
                                timestamp=timezone.now()
                            )

                            cache.set(CACHE_KEY, {
                                "value": line[len(DATA_PREFIX):],
                                "timestamp": time.time(),
                            }, timeout=None)
                        else:
                            self.stdout.write(f"[arduino] {line}")

            except serial.SerialException as e:
                self.stderr.write(self.style.ERROR(f"Serial error: {e}"))
                cache.set(CACHE_KEY, {"error": str(e)}, timeout=None)
                time.sleep(3)