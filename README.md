# 2048 Django Project

This repository contains a Django project with a blog app and a `sensors` app that
serves an air-quality dashboard (SPS30 particulate sensor + Open-Meteo weather data).
Readings can come from a locally attached Arduino (read over serial) or be pushed
remotely over HTTP (e.g. from an ESP32).

## What you need

- Python 3.12+ recommended
- Redis server running locally (used to cache the latest sensor/weather reading)
- Optional: an Arduino running the SPS30 firmware (`sensors/arduino/sps30/`)
  connected over serial, for the `read_serial` command

## Quick start

1. Clone the repository.
2. Create and activate a virtual environment:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. Install the Python requirements:

   ```bash
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the project root (see [Environment variables](#environment-variables) below):

   ```bash
   echo "DB_NAME=development" > .env
   ```

5. Apply database migrations:

   ```bash
   python manage.py migrate
   ```

6. Start the development server:

   ```bash
   python manage.py runserver
   ```

7. Open the dashboard at `http://127.0.0.1:8000/sensors/`.

## Environment variables

Set these in a `.env` file at the project root (loaded automatically by `2048/settings.py`).

| Variable          | Required | Purpose                                                                 |
|--------------------|----------|--------------------------------------------------------------------------|
| `DB_NAME`          | Yes      | `development` (uses `test.db.sqlite3`) or `production` (uses `db.sqlite3`). The app raises an error at startup if this isn't set to one of the two. |
| `SENSOR_API_KEY`   | Only for HTTP ingest | Shared secret that remote devices must send to `POST /sensors/ingest/sps30`. Leave unset to keep that endpoint disabled (it always rejects requests without a matching key). |

## Sensor dashboard notes

The `sensors` app depends on Redis for the "latest reading" cache. If Redis or the
sensor device isn't available, the dashboard still loads — the historical graphs
(backed by the database) work regardless, but the live-reading cards and date range
filter will show "No hay datos disponibles" until a reading comes in.

There are two ways to feed the dashboard:

**1. Local serial reader** (Arduino attached over USB):

```bash
python manage.py read_serial
```

Reads from `/dev/ttyUSB0` at 115200 baud (see `SERIAL_PORT`/`BAUD_RATE` in
`sensors/management/commands/read_serial.py` if your device uses a different port).

**2. HTTP ingest endpoint** (for remote devices, e.g. an ESP32 over WiFi):

```
POST /sensors/ingest/sps30
X-Api-Key: <SENSOR_API_KEY>
Content-Type: application/json

{
  "pm1": 0, "pm25": 0, "pm4": 0, "pm10": 0,
  "nc0": 0, "nc1": 0, "nc25": 0, "nc4": 0, "nc10": 0,
  "typical_particle_size": 0
}
```

All fields are required integers. The endpoint also fetches current weather for the
station's configured coordinates (`sensors/weather.py`) and stores it alongside the
reading. Returns `201` with the created record id on success.

## Useful project commands

```bash
python manage.py check
python manage.py migrate
python manage.py runserver
python manage.py read_serial
```

## GitHub upload advice

- Do not upload the virtual environment folder (`.venv`) to GitHub.
- Use `requirements.txt` so other people can recreate the environment with the same package versions.
- Keep `.env`, real secrets, local ports, and hardware-specific paths out of the repository.
