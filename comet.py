import asyncio
import logging
import sys

import config
from worker import Worker

level = getattr(logging, config.log_level, logging.INFO)
logging.basicConfig(
    level=level,
    handlers=[logging.StreamHandler(sys.stdout)],
    format="%(asctime)s %(levelname)s %(message)s",
)
if not hasattr(logging, config.log_level):
    logging.warning("Invalid LOG_LEVEL=%s, fallback to INFO", config.log_level)


async def main():
    worker = Worker()
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
