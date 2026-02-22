# RT2000BT MVP (BLE -> MQTT)

Minimalna wersja bez Domoticza. Mostek publikuje dane zaworu RT2000BT do MQTT i przyjmuje komendy z Node-RED/Home Assistant.

## Wymagania

- Raspberry Pi Zero W (BlueZ + działające BLE)
- Python 3.11+
- `uv`

## Instalacja

```bash
uv sync
```

## Konfiguracja

Najprościej przez plik `.env`:

```bash
cp .env.example .env
```

Następnie uzupełnij wartości w `.env`.

Obsługiwane zmienne:

- `LOG_LEVEL` (`DEBUG`, `INFO`, `WARNING`, `ERROR`; domyślnie `INFO`)
- `MQTT_HOST` (domyślnie `127.0.0.1`)
- `MQTT_PORT` (domyślnie `1883`)
- `MQTT_USER`
- `MQTT_PASS`
- `COMET_MAC` (MAC głowicy)
- `MQTT_TOPIC` (domyślnie `comet/lv1`)
- `POLL_INTERVAL_SECONDS` (domyślnie `300`)
- `BLE_TIMEOUT_SECONDS` (domyślnie `15`)

## Start

```bash
uv run python comet.py
```

## MQTT: telemetry

Publikowane topici:

- `{MQTT_TOPIC}/state` -> `Online` / `Offline` (retained)
- `{MQTT_TOPIC}/battery`
- `{MQTT_TOPIC}/temp/current`
- `{MQTT_TOPIC}/temp/setpoint`
- `{MQTT_TOPIC}/mode` -> `auto` / `manual`
- `{MQTT_TOPIC}/telemetry` -> JSON

## MQTT: komendy

- `{MQTT_TOPIC}/cmd/poll` (payload dowolny)
- `{MQTT_TOPIC}/cmd/setpoint` (payload np. `21.5`)
- `{MQTT_TOPIC}/cmd/mode` (payload: `auto` / `manual`)

## Debug BLE

Jeśli chcesz widzieć surowe odczyty GATT i wartości po parsowaniu, ustaw w `.env`:

```bash
LOG_LEVEL=DEBUG
```
