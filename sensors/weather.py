import json
from decimal import Decimal
from typing import Any
from urllib.parse import urlencode
from urllib.request import urlopen

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"
STATION_LATITUDE = -26.8223056
STATION_LONGITUDE = -65.2018056


def get_weather_data(latitude: float | None = None, longitude: float | None = None) -> dict[str, Any] | None:
    """Fetch a current weather snapshot from Open-Meteo.

    The returned payload is shaped for creation of a WeatherData record.
    """
    latitude = float(latitude if latitude is not None else STATION_LATITUDE)
    longitude = float(longitude if longitude is not None else STATION_LONGITUDE)

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": "temperature_2m,relative_humidity_2m,pressure_msl,wind_speed_10m,wind_direction_10m",
        "timezone": "auto",
    }

    request_url = f"{OPEN_METEO_URL}?{urlencode(params)}"

    try:
        with urlopen(request_url, timeout=5) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except Exception:
        return None

    current = payload.get("current", {})
    if not current:
        return None

    return {
        "temperature": Decimal(str(current.get("temperature_2m"))) if current.get("temperature_2m") is not None else None,
        "humidity": Decimal(str(current.get("relative_humidity_2m"))) if current.get("relative_humidity_2m") is not None else None,
        "pressure": Decimal(str(current.get("pressure_msl"))) if current.get("pressure_msl") is not None else None,
        "wind_direction": int(current.get("wind_direction_10m")) if current.get("wind_direction_10m") is not None else None,
        "wind_speed": Decimal(str(current.get("wind_speed_10m"))) if current.get("wind_speed_10m") is not None else None,
        "latitude": Decimal(str(latitude)),
        "longitude": Decimal(str(longitude)),
    }
