import hmac
import json
import time
from datetime import datetime, timedelta

from django.conf import settings
from django.core.cache import cache
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.utils.dateparse import parse_date
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .models import Sps30Data, WeatherData
from .weather import get_weather_data

DATA_PREFIX = "DATA,"

SPS30_READING_FIELDS = [
    "pm1", "pm25", "pm4", "pm10",
    "nc0", "nc1", "nc25", "nc4", "nc10",
    "typical_particle_size",
]


def dashboard(request):
    return render(request, "dashboard.html")


def _resolve_range(request):
    """Resolve the (start, end) datetime range for graph queries from the
    optional `start`/`end` GET params (YYYY-MM-DD). Defaults to the last
    24 hours when a param is missing or invalid.
    """
    tz = timezone.get_current_timezone()
    now = timezone.now()

    end_date = parse_date(request.GET.get("end", ""))
    start_date = parse_date(request.GET.get("start", ""))

    if end_date:
        end = timezone.make_aware(datetime.combine(end_date, datetime.max.time()), tz)
    else:
        end = now

    if start_date:
        start = timezone.make_aware(datetime.combine(start_date, datetime.min.time()), tz)
    else:
        start = end - timedelta(days=1)

    return start, end


def get_available_range(request):
    """Returns the earliest and latest dates for which sensor data exists,
    so the frontend can bound and default its date range picker.
    """
    earliest = Sps30Data.objects.order_by("timestamp").values_list("timestamp", flat=True).first()
    latest = Sps30Data.objects.order_by("-timestamp").values_list("timestamp", flat=True).first()

    if not earliest or not latest:
        return JsonResponse({"min": None, "max": None})

    return JsonResponse({
        "min": timezone.localtime(earliest).date().isoformat(),
        "max": timezone.localtime(latest).date().isoformat(),
    })


def get_latest_sps(request):
    sps30_reading = cache.get("sps30_latest_reading", {"value": None, "timestamp": None})

    if sps30_reading.get("value") and sps30_reading.get("value").startswith(DATA_PREFIX):
        return JsonResponse(sps30_reading)

    return JsonResponse({"error": "No hay datos disponibles"}, status=404)


def get_latest_weather(request):
    weather_reading = cache.get("weather_latest_reading", {"value": None, "timestamp": None})

    if weather_reading.get("value"):
        return JsonResponse(weather_reading)

    return JsonResponse({"error": "No hay datos disponibles"}, status=404)


def get_pm_graph(request):
    start, end = _resolve_range(request)
    qs = Sps30Data.objects.filter(timestamp__gte=start, timestamp__lte=end).order_by("timestamp")

    data = {
        "labels": [e.timestamp.strftime("%Y-%m-%d %H:%M:%S") for e in qs],
        "pm1": [e.pm1 for e in qs],
        "pm25": [e.pm25 for e in qs],
        "pm4": [e.pm4 for e in qs],
        "pm10": [e.pm10 for e in qs],
    }

    return JsonResponse(data)


def get_nc_graph(request):
    start, end = _resolve_range(request)
    qs = Sps30Data.objects.filter(timestamp__gte=start, timestamp__lte=end).order_by("timestamp")

    data = {
        "labels": [e.timestamp.strftime("%Y-%m-%d %H:%M:%S") for e in qs],
        "nc0": [e.nc0 for e in qs],
        "nc1": [e.nc1 for e in qs],
        "nc25": [e.nc25 for e in qs],
        "nc10": [e.nc10 for e in qs],
    }

    return JsonResponse(data)


def get_nc_pm_graph(request):
    start, end = _resolve_range(request)
    qs = Sps30Data.objects.filter(timestamp__gte=start, timestamp__lte=end).order_by("timestamp")

    data = {
        "labels": [e.timestamp.strftime("%m-%d %H:%M") for e in qs],
        "pm1": [e.pm1 for e in qs],
        "pm25": [e.pm25 for e in qs],
        "nc0": [e.nc0 for e in qs],
        "nc1": [e.nc1 for e in qs],
        "nc25": [e.nc25 for e in qs],
    }

    return JsonResponse(data)


def get_weather_graph(request):
    start, end = _resolve_range(request)
    qs = WeatherData.objects.filter(timestamp__gte=start, timestamp__lte=end).order_by("timestamp")

    data = {
        "labels": [e.timestamp.strftime("%Y-%m-%d %H:%M:%S") for e in qs],
        "temperature": [float(e.temperature) if e.temperature is not None else None for e in qs],
        "humidity": [float(e.humidity) if e.humidity is not None else None for e in qs],
    }

    return JsonResponse(data)


@csrf_exempt
@require_POST
def ingest_sps30_reading(request):
    """HTTP ingest endpoint for devices (e.g. an ESP32) that push SPS30
    readings over WiFi instead of being read from a local serial port.

    Expects a JSON body with the fields in SPS30_READING_FIELDS, and an
    X-Api-Key header matching settings.SENSOR_API_KEY.
    """
    expected_key = settings.SENSOR_API_KEY
    provided_key = request.headers.get("X-Api-Key", "")
    if not expected_key or not hmac.compare_digest(provided_key, expected_key):
        return JsonResponse({"error": "unauthorized"}, status=401)

    try:
        payload = json.loads(request.body)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({"error": "invalid JSON body"}, status=400)

    missing = [field for field in SPS30_READING_FIELDS if field not in payload]
    if missing:
        return JsonResponse(
            {"error": f"missing fields: {', '.join(missing)}"}, status=400
        )

    try:
        values = {field: int(payload[field]) for field in SPS30_READING_FIELDS}
    except (TypeError, ValueError):
        return JsonResponse({"error": "fields must be integers"}, status=400)

    timestamp = timezone.now()

    try:
        sps30_record = Sps30Data.objects.create(timestamp=timestamp, **values)
    except Exception as e:
        return JsonResponse({"error": f"could not save reading: {e}"}, status=500)

    cache_line = ",".join(str(values[field]) for field in SPS30_READING_FIELDS)
    cache.set(
        "sps30_latest_reading",
        {"value": f"{DATA_PREFIX}{cache_line}", "timestamp": time.time()},
        timeout=None,
    )

    weather_payload = get_weather_data()
    if weather_payload:
        try:
            WeatherData.objects.create(
                timestamp=timestamp,
                sps30_data=sps30_record,
                **weather_payload,
            )
            weather_line = ",".join(
                str(weather_payload.get(field))
                for field in [
                    "temperature", "humidity", "pressure",
                    "wind_direction", "wind_speed", "latitude", "longitude",
                ]
            )
            cache.set(
                "weather_latest_reading",
                {
                    "value": f"{timestamp.isoformat()},{weather_line}",
                    "timestamp": time.time(),
                },
                timeout=None,
            )
        except Exception:
            pass

    return JsonResponse({"status": "ok", "id": sps30_record.pk}, status=201)
