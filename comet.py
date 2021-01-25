from worker import Worker
import logging.handlers
import sys

handlers = [logging.handlers.SysLogHandler(address=('192.168.2.102', 514)),
            logging.handlers.logging.StreamHandler(sys.stdout)]

# noinspection PyArgumentList
logging.basicConfig(handlers=handlers, level=logging.INFO)

logging.info("Start")

worker1 = Worker()

worker1.run()

