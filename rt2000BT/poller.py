import json
import logging
import config


def _mode_label(mode_auto: int) -> str:
    if mode_auto == 0:
        return "auto"
    if mode_auto == 1:
        return "manual"
    return "unknown"


def poll_valve(valve, client, topic: str | None = None) -> bool:
    base_topic = topic or config.mqtt_topic

    payload = {
        "battery": valve.battery,
        "temp_current": valve.current_temp,
        "temp_setpoint": valve.set_point_temp,
        "mode": _mode_label(valve.mode_auto),
    }

    client.publish(f"{base_topic}/battery", payload=str(payload["battery"]), qos=0, retain=True)
    client.publish(f"{base_topic}/temp/current", payload=str(payload["temp_current"]), qos=0, retain=True)
    client.publish(f"{base_topic}/temp/setpoint", payload=str(payload["temp_setpoint"]), qos=0, retain=True)
    client.publish(f"{base_topic}/mode", payload=payload["mode"], qos=0, retain=True)
    client.publish(f"{base_topic}/telemetry", payload=json.dumps(payload), qos=0, retain=False)

    logging.info("Published telemetry: %s", payload)
    return True
