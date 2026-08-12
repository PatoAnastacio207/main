import time

import serial
from django.core.cache import cache
from django.core.management.base import BaseCommand
from django.utils import timezone

from sensors.models import Sps30Data, WeatherData
from sensors.weather import get_weather_data

SERIAL_PORT = "/dev/ttyUSB0"
BAUD_RATE = 115200
DATA_PREFIX = "DATA,"


class Command(BaseCommand):
    help = "Continuously reads Arduino serial output and caches the latest value"

    def parse_sps30_line(self, line: str) -> dict | None:
        if not line.startswith(DATA_PREFIX):
            return None

        print("passes DATA_PREFIX")

        parts = line.split(",")
        if len(parts) != 11:
            return None

        _, pm1, pm25, pm4, pm10, nc0, nc1, nc25, nc4, nc10, typicalParticleSize = parts
        return {
            "pm1": pm1,
            "pm25": pm25,
            "pm4": pm4,
            "pm10": pm10,
            "nc0": nc0,
            "nc1": nc1,
            "nc25": nc25,
            "nc4": nc4,
            "nc10": nc10,
            "typicalParticleSize": typicalParticleSize,
            "timestamp": timezone.now(),
        }

    def write_sps_reading_to_cache(self, reading: str):
        cache.set(
            "sps30_latest_reading",
            {
                "value": reading,
                "timestamp": time.time(),
            },
            timeout=None,
        )

    def write_weather_reading_to_cache(self, reading: dict):
        weather_string = ",".join(
            [
                str(reading.get("timestamp")),
                str(reading.get("temperature")),
                str(reading.get("humidity")),
                str(reading.get("pressure")),
                str(reading.get("wind_direction")),
                str(reading.get("wind_speed")),
                str(reading.get("latitude")),
                str(reading.get("longitude")),
            ]
        )
        cache.set(
            "weather_latest_reading",
            {
                "value": weather_string,
                "timestamp": time.time(),
            },
            timeout=None,
        )

    def save_sps30_record(self, payload: dict) -> Sps30Data | None:
        try:
            return Sps30Data.objects.create(
                pm1=payload["pm1"],
                pm25=payload["pm25"],
                pm4=payload["pm4"],
                pm10=payload["pm10"],
                nc0=payload["nc0"],
                nc1=payload["nc1"],
                nc25=payload["nc25"],
                nc4=payload["nc4"],
                nc10=payload["nc10"],
                typicalParticleSize=payload["typicalParticleSize"],
                timestamp=payload["timestamp"],
            )
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Error saving SPS30 data to DB: {e}"))
            return None

    def save_weather_record(self, timestamp, sps30_record: Sps30Data) -> WeatherData | None:
        weather_payload = get_weather_data()
        if not weather_payload:
            return None

        try:
            weather_record = WeatherData.objects.create(
                timestamp=timestamp,
                sps30_data=sps30_record,
                **weather_payload,
            )
            weather_payload["timestamp"] = timestamp.isoformat()
            self.write_weather_reading_to_cache(weather_payload)
            return weather_record
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Error saving weather data to DB: {e}"))
            return None

    def handle_loop(self, ser) -> None:
        while True:
            line = ser.readline().decode("utf-8", errors="ignore").strip()
            if not line:
                continue

            if not line.startswith(DATA_PREFIX):
                self.stdout.write(f"[arduino] {line}")
                continue

            payload = self.parse_sps30_line(line)
            print(line)
            if payload is None:
                self.stderr.write(self.style.ERROR("Could not parse SPS30 payload."))
                continue

            sps30_record = self.save_sps30_record(payload)
            if sps30_record is None:
                continue

            self.write_sps_reading_to_cache(line[len(DATA_PREFIX):])
            self.save_weather_record(payload["timestamp"], sps30_record)

    def handle(self, *args, **options):
        while True:
            try:
                self.stdout.write(f"Connecting to {SERIAL_PORT}...")
                with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1) as ser:
                    self.stdout.write(self.style.SUCCESS("Connected"))
                    self.handle_loop(ser)
            except serial.SerialException as e:
                self.stderr.write(self.style.ERROR(f"Serial error: {e}"))
                cache.set("sps30_latest_reading", {"error": str(e)}, timeout=None)
                time.sleep(3)