import logging
from bleak import BleakClient

STATUS_ID = "47e9ee2a-47e9-11e4-8939-164230d1df67"
SETTINGS_ID = "47e9ee2b-47e9-11e4-8939-164230d1df67"
BATTERY_ID_ALT = "47e9ee2c-47e9-11e4-8939-164230d1df67"
PIN_ID = "47e9ee30-47e9-11e4-8939-164230d1df67"


class Valve:
    def __init__(self, mac: str, pin: str | None = None, timeout: float = 15.0):
        self.mac = mac
        self.pin = pin
        self.timeout = timeout
        self.battery = 255
        self.current_temp = 0.0
        self.set_point_temp = 0.0
        self.mode_auto = -1

    async def _connect(self) -> BleakClient:
        client = BleakClient(self.mac, timeout=self.timeout)
        await client.connect()
        return client

    async def _safe_disconnect(self, client: BleakClient | None) -> None:
        if not client:
            return
        try:
            await client.disconnect()
        except Exception:
            logging.warning("BLE disconnect failed; continuing", exc_info=True)

    async def poll(self) -> bool:
        client = None
        try:
            client = await self._connect()
            await client.write_gatt_char(PIN_ID, b"\x00\x00\x00\x00")
            settings = list(await client.read_gatt_char(SETTINGS_ID))
            self.current_temp = settings[0] / 2
            self.set_point_temp = settings[1] / 2
            self.battery = list(await client.read_gatt_char(BATTERY_ID_ALT))[0]
            self.mode_auto = list(await client.read_gatt_char(STATUS_ID))[0]
            return True
        except Exception:
            logging.exception("BLE poll failed")
            return False
        finally:
            await self._safe_disconnect(client)

    # True = manual, False = auto
    async def update_mode(self, value: bool) -> bool:
        client = None
        try:
            client = await self._connect()
            await client.write_gatt_char(PIN_ID, b"\x00\x00\x00\x00")
            current_mode = list(await client.read_gatt_char(STATUS_ID))[0]
            payload = int(value)
            if payload != current_mode:
                await client.write_gatt_char(STATUS_ID, bytes([payload]))
            return True
        except Exception:
            logging.exception("BLE mode update failed")
            return False
        finally:
            await self._safe_disconnect(client)

    async def update_temperature(self, value: float) -> bool:
        client = None
        try:
            client = await self._connect()
            await client.write_gatt_char(PIN_ID, b"\x00\x00\x00\x00")
            settings = list(await client.read_gatt_char(SETTINGS_ID))
            current_setpoint = settings[1] / 2
            if current_setpoint != value:
                settings[1] = int(value * 2)
                await client.write_gatt_char(SETTINGS_ID, bytes(settings))
            return True
        except Exception:
            logging.exception("BLE temperature update failed")
            return False
        finally:
            await self._safe_disconnect(client)
