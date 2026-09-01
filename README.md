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

## Running with Docker on your own server

The repo ships a `Dockerfile` (gunicorn + WhiteNoise) and a `docker-compose.yml`
that also starts the Redis the sensors app needs.

### 1. Get the code onto the server

```bash
git clone <your-repo-url> 2048
cd 2048
```

### 2. Create the environment file

```bash
cp .env.docker.example .env.docker
python3 -c "import secrets; print(secrets.token_urlsafe(50))"   # paste as SECRET_KEY
```

Edit `.env.docker` and set at least `SECRET_KEY`, `ALLOWED_HOSTS` (your domain or
server IP) and, if you use the HTTP ingest endpoint, `SENSOR_API_KEY`.
`.env.docker` is gitignored — keep it that way.

### 3. Build and start

```bash
docker compose up -d --build
```

The entrypoint runs `migrate` and `collectstatic` on every start, so a fresh
server comes up with an empty database ready to use. The app listens on port
8000.

### 4. Create your admin user

```bash
docker compose exec web python manage.py createsuperuser
```

### Bringing your existing data along (optional)

The database and uploaded images live in the `app-data` volume at `/data`, not in
the image. To move your current local data over:

```bash
docker compose cp db.sqlite3 web:/data/db.sqlite3
docker compose cp articles web:/data/media/articles    # existing article images
docker compose restart web
```

### Day-to-day commands

```bash
docker compose logs -f web       # follow logs
docker compose up -d --build     # deploy after a git pull
docker compose down              # stop (the app-data volume is kept)
```

### Configuration reference (Docker)

| Variable               | Default                     | Purpose |
|------------------------|-----------------------------|---------|
| `DB_NAME`              | —                           | `production` or `development`, as before. |
| `SECRET_KEY`           | insecure dev key            | Must be set to a random value in production. |
| `DEBUG`                | `True`                      | Set to `False` on the server. |
| `ALLOWED_HOSTS`        | `*`                         | Comma-separated hostnames/IPs. |
| `CSRF_TRUSTED_ORIGINS` | empty                       | Comma-separated `https://…` origins, needed for admin logins over HTTPS. |
| `BEHIND_HTTPS_PROXY`   | `False`                     | Set to `True` when a proxy terminates TLS. |
| `REDIS_URL`            | `redis://127.0.0.1:6379/1`  | Compose sets this to `redis://redis:6379/1`. |
| `DATA_DIR`             | project root                | Where the SQLite file lives; `/data` in Docker. |
| `MEDIA_ROOT`           | `$DATA_DIR/media`           | Uploaded article images. |
| `STATIC_ROOT`          | `./staticfiles`             | Target of `collectstatic`. |

All of these keep their old behaviour when unset, so local development still
works with just `DB_NAME` in `.env`.

### Restricting access (Tailscale, LAN)

The published port is bound to a single address via `BIND_ADDR`, set in a
`.env` file next to `docker-compose.yml`. This is separate from `.env.docker`:
Compose reads `.env` for variable substitution in the compose file itself,
while `.env.docker` sets the application's environment.

```bash
echo "BIND_ADDR=$(tailscale ip -4)" > .env
docker compose up -d
```

Binding is what actually restricts access. `ufw` rules do **not** cover Docker
published ports: Docker writes its own iptables rules in the `DOCKER` chain,
which are evaluated before ufw's `INPUT` chain, so a port published on
`0.0.0.0` stays reachable from the LAN even when `ufw status` suggests
otherwise.

Add the address to `ALLOWED_HOSTS` in `.env.docker` as well, since that
filters the `Host` header:

```
ALLOWED_HOSTS=100.x.y.z,debian13.your-tailnet.ts.net
```

Leaving `BIND_ADDR` unset falls back to `127.0.0.1`, which fails closed: the
app is then reachable only from the server itself.

### Putting it behind HTTPS

Gunicorn serves plain HTTP. For a public server, run nginx or Caddy in front,
change the port mapping in `docker-compose.yml` to `"127.0.0.1:8000:8000"`, and
set `CSRF_TRUSTED_ORIGINS=https://your-domain` and `BEHIND_HTTPS_PROXY=True`.

### The serial reader in Docker

`read_serial` needs a physically attached Arduino, so it is commented out in
`docker-compose.yml`. Uncomment the `serial-reader` service (and adjust the
device path) only if the sensor is plugged into the server itself. Remote
devices posting to `/sensors/ingest/sps30` need nothing extra.

## GitHub upload advice

- Do not upload the virtual environment folder (`.venv`) to GitHub.
- Use `requirements.txt` so other people can recreate the environment with the same package versions.
- Keep `.env`, real secrets, local ports, and hardware-specific paths out of the repository.
