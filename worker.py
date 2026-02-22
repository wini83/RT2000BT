import asyncio
import logging

import paho.mqtt.client as mqtt

import config
from rt2000BT import Valve, poll_valve


class Worker:
    def __init__(self):
        self.valve = Valve(config.mac, None, timeout=config.ble_timeout_seconds)
        self.loop = None
        self.ble_lock = asyncio.Lock()

    def _publish_state(self, client: mqtt.Client, payload: str) -> None:
        client.publish(f"{config.mqtt_topic}/state", payload=payload, retain=True)

    def _schedule(self, coro) -> None:
        future = asyncio.run_coroutine_threadsafe(coro, self.loop)

        def _log_result(done):
            try:
                done.result()
            except Exception:
                logging.exception("Async task failed")

        future.add_done_callback(_log_result)

    async def _poll_and_publish(self, client: mqtt.Client) -> None:
        async with self.ble_lock:
            if await self.valve.poll():
                poll_valve(self.valve, client)

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

    def on_connect(self, client, userdata, flags, reason_code, properties):
        logging.info("Connected to MQTT (%s)", reason_code)
        self._publish_state(client, "Online")
        client.subscribe(f"{config.mqtt_topic}/cmd/#")
        self._schedule(self._poll_and_publish(client))

    def on_message(self, client, userdata, msg):
        payload = msg.payload.decode("utf-8", errors="ignore")
        logging.info("MQTT command topic=%s payload=%s", msg.topic, payload)
        self._schedule(self._handle_command(client, msg.topic, payload))

    def on_disconnect(self, client, userdata, disconnect_flags, reason_code, properties):
        logging.info("Disconnected from MQTT (%s)", reason_code)

    async def run(self):
        self.loop = asyncio.get_running_loop()

        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
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
            self._publish_state(client, "Offline")
            client.loop_stop()
            client.disconnect()
