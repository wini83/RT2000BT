import asyncio
import logging
import sys

from worker import Worker

logging.basicConfig(
    level=logging.INFO,
    handlers=[logging.StreamHandler(sys.stdout)],
    format="%(asctime)s %(levelname)s %(message)s",
)


async def main():
    worker = Worker()
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
