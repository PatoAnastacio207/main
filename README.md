# 2048 Django Project

This repository contains a Django-based project with a blog app and a sensor dashboard that reads from an Arduino serial device.

## What you need

- Python 3.12+ recommended
- Redis server running locally for cache-backed dashboard features
- Optional: an Arduino device connected to the serial port `/dev/ttyACM0` for the sensor command

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

4. Apply database migrations:

   ```bash
   python manage.py migrate
   ```

5. Start the development server:

   ```bash
   python manage.py runserver
   ```

6. Open the site at `http://127.0.0.1:8000/`.

## Sensor dashboard notes

The `sensors` app depends on Redis and a serial stream. If you do not have the Arduino hardware attached, the dashboard still loads, but the live sensor command will not receive readings until the device is available.

To use the serial reader manually:

```bash
python manage.py read_serial
```

## Useful project commands

```bash
python manage.py check
python manage.py migrate
python manage.py runserver
```

## GitHub upload advice

- Do not upload the virtual environment folder (`.venv`, `bin`, `lib`, `include`, `lib64`) to GitHub.
- Use `requirements.txt` so other people can recreate the environment with the same package versions.
- Keep any real secrets, local ports, and hardware-specific paths out of the repository.
