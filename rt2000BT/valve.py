import logging
from bleak import BleakClient

logger = logging.getLogger(__name__)

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
        logger.debug("BLE connect start mac=%s timeout=%s", self.mac, self.timeout)
        client = BleakClient(self.mac, timeout=self.timeout)
        await client.connect()
        logger.debug("BLE connect ok mac=%s", self.mac)
        return client

    async def _safe_disconnect(self, client: BleakClient | None) -> None:
        if not client:
            return
        try:
            await client.disconnect()
            logger.debug("BLE disconnect ok mac=%s", self.mac)
        except EOFError:
            logger.info("BLE disconnect EOF on BlueZ; ignored")
        except Exception:
            logger.warning("BLE disconnect failed; continuing", exc_info=True)

    async def poll(self) -> bool:
        client = None
        try:
            client = await self._connect()
            await client.write_gatt_char(PIN_ID, b"\x00\x00\x00\x00")
            settings_raw = bytes(await client.read_gatt_char(SETTINGS_ID))
            settings = list(settings_raw)
            self.current_temp = settings[0] / 2
            self.set_point_temp = settings[1] / 2
            battery_raw = bytes(await client.read_gatt_char(BATTERY_ID_ALT))
            status_raw = bytes(await client.read_gatt_char(STATUS_ID))
            self.battery = list(battery_raw)[0]
            self.mode_auto = list(status_raw)[0]
            logger.debug(
                "BLE poll raw settings=%s battery=%s status=%s",
                settings_raw.hex(),
                battery_raw.hex(),
                status_raw.hex(),
            )
            logger.debug(
                "BLE poll parsed current_temp=%.1f setpoint=%.1f battery=%s mode_auto=%s",
                self.current_temp,
                self.set_point_temp,
                self.battery,
                self.mode_auto,
            )
            return True
        except TimeoutError:
            logger.warning("BLE poll timeout for mac=%s", self.mac)
            return False
        except Exception:
            logger.exception("BLE poll failed")
            return False
        finally:
            await self._safe_disconnect(client)

    # True = manual, False = auto
    async def update_mode(self, value: bool) -> bool:
        client = None
        try:
            client = await self._connect()
            await client.write_gatt_char(PIN_ID, b"\x00\x00\x00\x00")
            status_raw = bytes(await client.read_gatt_char(STATUS_ID))
            current_mode = list(status_raw)[0]
            payload = int(value)
            logger.debug(
                "BLE mode read raw=%s parsed=%s requested=%s",
                status_raw.hex(),
                current_mode,
                payload,
            )
            if payload != current_mode:
                await client.write_gatt_char(STATUS_ID, bytes([payload]))
                logger.debug("BLE mode write raw=%s", bytes([payload]).hex())
            return True
        except TimeoutError:
            logger.warning("BLE mode update timeout for mac=%s", self.mac)
            return False
        except Exception:
            logger.exception("BLE mode update failed")
            return False
        finally:
            await self._safe_disconnect(client)

    async def update_temperature(self, value: float) -> bool:
        client = None
        try:
            client = await self._connect()
            await client.write_gatt_char(PIN_ID, b"\x00\x00\x00\x00")
            settings_raw = bytes(await client.read_gatt_char(SETTINGS_ID))
            settings = list(settings_raw)
            current_setpoint = settings[1] / 2
            logger.debug(
                "BLE setpoint read raw=%s parsed_current_setpoint=%.1f requested=%.1f",
                settings_raw.hex(),
                current_setpoint,
                value,
            )
            if current_setpoint != value:
                settings[1] = int(value * 2)
                payload = bytes(settings)
                await client.write_gatt_char(SETTINGS_ID, payload)
                logger.debug("BLE setpoint write raw=%s", payload.hex())
            return True
        except TimeoutError:
            logger.warning("BLE temperature update timeout for mac=%s", self.mac)
            return False
        except Exception:
            logger.exception("BLE temperature update failed")
            return False
        finally:
            await self._safe_disconnect(client)
