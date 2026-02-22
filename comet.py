import asyncio
import logging
import sys

import config
from worker import Worker

level = getattr(logging, config.log_level, logging.INFO)
ble_lib_level = getattr(logging, config.ble_lib_log_level, logging.WARNING)
logging.basicConfig(
    level=level,
    handlers=[logging.StreamHandler(sys.stdout)],
    format="%(asctime)s %(levelname)s %(message)s",
)
if not hasattr(logging, config.log_level):
    logging.warning("Invalid LOG_LEVEL=%s, fallback to INFO", config.log_level)
if not hasattr(logging, config.ble_lib_log_level):
    logging.warning(
        "Invalid BLE_LIB_LOG_LEVEL=%s, fallback to WARNING",
        config.ble_lib_log_level,
    )

# Keep our app debug logs while muting noisy transport internals.
for logger_name in ("bleak", "dbus_fast"):
    logging.getLogger(logger_name).setLevel(ble_lib_level)


async def main():
    worker = Worker()
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
