import asyncio
import json
import logging
from datetime import datetime, timezone

import paho.mqtt.client as mqtt

import config
from rt2000BT import Valve, poll_valve


class Worker:
    AVAILABILITY_FAILURE_THRESHOLD = 3

    def __init__(self):
        self.valve = Valve(config.mac, None, timeout=config.ble_timeout_seconds)
        self.loop: asyncio.AbstractEventLoop | None = None
        self.ble_lock = asyncio.Lock()
        self.consecutive_poll_failures = 0
        self.mqtt_connected = asyncio.Event()

    def _publish_bridge_state(self, client: mqtt.Client, payload: str) -> None:
        client.publish(f"{config.mqtt_topic}/state", payload=payload, retain=True)

    def _publish_valve_availability(self, client: mqtt.Client, available: bool) -> None:
        payload = "online" if available else "offline"
        client.publish(
            f"{config.mqtt_topic}/availability",
            payload=payload,
            qos=0,
            retain=True,
        )

    def _publish_last_seen(self, client: mqtt.Client) -> None:
        client.publish(
            f"{config.mqtt_topic}/last_seen",
            payload=datetime.now(timezone.utc).isoformat(),
            qos=0,
            retain=True,
        )

    def _publish_discovery(self, client: mqtt.Client) -> None:
        device = {
            "identifiers": [config.ha_device_id],
            "name": config.ha_device_name,
            "manufacturer": "Eurotronic",
            "model": "Comet Blue / RT2000BT",
        }
        availability_topic = f"{config.mqtt_topic}/availability"

        climate = {
            "name": None,
            "unique_id": f"{config.ha_device_id}_climate",
            "default_entity_id": f"climate.{config.ha_device_id}",
            "device": device,
            "availability_topic": availability_topic,
            "current_temperature_topic": f"{config.mqtt_topic}/temperature",
            "temperature_state_topic": f"{config.mqtt_topic}/setpoint",
            "temperature_command_topic": f"{config.mqtt_topic}/setpoint/set",
            "mode_state_topic": f"{config.mqtt_topic}/mode",
            "mode_command_topic": f"{config.mqtt_topic}/mode/set",
            "modes": ["heat", "auto"],
            "min_temp": 8,
            "max_temp": 28,
            "temp_step": 0.5,
            "temperature_unit": "C",
        }
        battery = {
            "name": "Battery",
            "unique_id": f"{config.ha_device_id}_battery",
            "default_entity_id": f"sensor.{config.ha_device_id}_battery",
            "device": device,
            "availability_topic": availability_topic,
            "state_topic": f"{config.mqtt_topic}/battery",
            "device_class": "battery",
            "state_class": "measurement",
            "unit_of_measurement": "%",
        }
        last_seen = {
            "name": "Last seen",
            "unique_id": f"{config.ha_device_id}_last_seen",
            "default_entity_id": f"sensor.{config.ha_device_id}_last_seen",
            "device": device,
            "state_topic": f"{config.mqtt_topic}/last_seen",
            "device_class": "timestamp",
            "entity_category": "diagnostic",
        }

        configs = {
            f"{config.ha_discovery_prefix}/climate/{config.ha_device_id}/config": climate,
            f"{config.ha_discovery_prefix}/sensor/{config.ha_device_id}_battery/config": battery,
            f"{config.ha_discovery_prefix}/sensor/{config.ha_device_id}_last_seen/config": last_seen,
        }
        for topic, payload in configs.items():
            client.publish(topic, payload=json.dumps(payload), qos=0, retain=True)
        logging.info("Published Home Assistant MQTT discovery")

    def _record_poll_success(self, client: mqtt.Client) -> None:
        self.consecutive_poll_failures = 0
        self._publish_valve_availability(client, True)
        self._publish_last_seen(client)

    def _record_poll_failure(self, client: mqtt.Client) -> None:
        self.consecutive_poll_failures += 1
        if self.consecutive_poll_failures <= self.AVAILABILITY_FAILURE_THRESHOLD:
            logging.warning(
                "Valve poll failed (%s/%s)",
                self.consecutive_poll_failures,
                self.AVAILABILITY_FAILURE_THRESHOLD,
            )
        else:
            logging.warning(
                "Valve poll failed (%s consecutive failures)",
                self.consecutive_poll_failures,
            )

        if self.consecutive_poll_failures == self.AVAILABILITY_FAILURE_THRESHOLD:
            self._publish_valve_availability(client, False)
            logging.warning(
                "Valve unavailable after %s consecutive failed polls",
                self.consecutive_poll_failures,
            )

    def _next_poll_interval(self) -> int:
        if 0 < self.consecutive_poll_failures < self.AVAILABILITY_FAILURE_THRESHOLD:
            return config.retry_interval_seconds
        return config.poll_interval_seconds

    def _schedule(self, coro) -> None:
        if self.loop is None:
            logging.warning("Event loop is not ready; dropping scheduled task")
            return
        future = asyncio.run_coroutine_threadsafe(coro, self.loop)

        def _log_result(done):
            try:
                done.result()
            except Exception:
                logging.exception("Async task failed")

        future.add_done_callback(_log_result)

    async def _poll_and_publish(self, client: mqtt.Client) -> bool:
        async with self.ble_lock:
            if await self.valve.poll():
                poll_valve(self.valve, client)
                self._record_poll_success(client)
                return True

            self._record_poll_failure(client)
            return False

    async def _handle_command(self, client: mqtt.Client, topic: str, payload: str) -> None:
        payload = payload.strip().lower()

        if topic == f"{config.mqtt_topic}/poll/set":
            await self._poll_and_publish(client)
            return

        if topic == f"{config.mqtt_topic}/setpoint/set":
            try:
                value = float(payload)
            except ValueError:
                logging.warning("Invalid setpoint payload: %s", payload)
                return
            async with self.ble_lock:
                if await self.valve.update_temperature(value):
                    if await self.valve.poll():
                        poll_valve(self.valve, client)
                        self._record_poll_success(client)
                    else:
                        self._record_poll_failure(client)
            return

        if topic == f"{config.mqtt_topic}/mode/set":
            desired = None
            if payload in {"heat", "manual", "1", "true", "on"}:
                desired = True
            if payload in {"auto", "0", "false", "off"}:
                desired = False
            if desired is None:
                logging.warning("Invalid mode payload: %s", payload)
                return
            async with self.ble_lock:
                if await self.valve.update_mode(desired):
                    if await self.valve.poll():
                        poll_valve(self.valve, client)
                        self._record_poll_success(client)
                    else:
                        self._record_poll_failure(client)

    def on_connect(self, client, userdata, flags, rc):
        logging.info("Connected to MQTT (%s)", rc)
        self._publish_bridge_state(client, "Online")
        self._publish_discovery(client)
        client.subscribe(f"{config.mqtt_topic}/+/set")
        client.subscribe("homeassistant/status")
        if self.loop is not None:
            self.loop.call_soon_threadsafe(self.mqtt_connected.set)

    def on_message(self, client, userdata, msg):
        payload = msg.payload.decode("utf-8", errors="ignore")
        logging.info("MQTT command topic=%s payload=%s", msg.topic, payload)
        if msg.topic == "homeassistant/status":
            if payload.strip().lower() == "online":
                self._publish_discovery(client)
            return
        self._schedule(self._handle_command(client, msg.topic, payload))

    def on_disconnect(self, client, userdata, rc):
        logging.info("Disconnected from MQTT (%s)", rc)
        if self.loop is not None:
            self.loop.call_soon_threadsafe(self.mqtt_connected.clear)

    async def run(self):
        self.loop = asyncio.get_running_loop()

        client = mqtt.Client()
        client.on_connect = self.on_connect
        client.on_message = self.on_message
        client.on_disconnect = self.on_disconnect
        if config.mqtt_user:
            client.username_pw_set(config.mqtt_user, password=config.mqtt_pass)

        client.will_set(f"{config.mqtt_topic}/state", payload="Offline", retain=True)
        client.connect(config.mqtt_server_ip, config.mqtt_server_port, 60)
        client.loop_start()

        try:
            await self.mqtt_connected.wait()
            while True:
                try:
                    await self._poll_and_publish(client)
                except Exception:
                    logging.exception("Polling loop failed; continuing")
                await asyncio.sleep(self._next_poll_interval())
        finally:
            self._publish_valve_availability(client, False)
            self._publish_bridge_state(client, "Offline")
            client.loop_stop()
            client.disconnect()
