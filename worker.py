import asyncio
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

    def _record_poll_success(self, client: mqtt.Client) -> None:
        self.consecutive_poll_failures = 0
        self._publish_valve_availability(client, True)
        self._publish_last_seen(client)

    def _record_poll_failure(self, client: mqtt.Client) -> None:
        self.consecutive_poll_failures += 1
        logging.warning(
            "Valve poll failed (%s/%s)",
            self.consecutive_poll_failures,
            self.AVAILABILITY_FAILURE_THRESHOLD,
        )
        if self.consecutive_poll_failures >= self.AVAILABILITY_FAILURE_THRESHOLD:
            self._publish_valve_availability(client, False)
            logging.warning(
                "Valve unavailable after %s consecutive failed polls",
                self.consecutive_poll_failures,
            )

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

        if topic == f"{config.mqtt_topic}/cmd/poll":
            await self._poll_and_publish(client)
            return

        if topic == f"{config.mqtt_topic}/cmd/setpoint":
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

        if topic == f"{config.mqtt_topic}/cmd/mode":
            desired = None
            if payload in {"manual", "1", "true", "on"}:
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
        client.subscribe(f"{config.mqtt_topic}/cmd/#")
        self._schedule(self._poll_and_publish(client))

    def on_message(self, client, userdata, msg):
        payload = msg.payload.decode("utf-8", errors="ignore")
        logging.info("MQTT command topic=%s payload=%s", msg.topic, payload)
        self._schedule(self._handle_command(client, msg.topic, payload))

    def on_disconnect(self, client, userdata, rc):
        logging.info("Disconnected from MQTT (%s)", rc)

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
            while True:
                await asyncio.sleep(config.poll_interval_seconds)
                try:
                    await self._poll_and_publish(client)
                except Exception:
                    logging.exception("Polling loop failed; continuing")
        finally:
            self._publish_valve_availability(client, False)
            self._publish_bridge_state(client, "Offline")
            client.loop_stop()
            client.disconnect()
