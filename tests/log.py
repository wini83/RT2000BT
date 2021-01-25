import logging.handlers
import sys

handlers = [logging.handlers.SysLogHandler(address=('192.168.2.102', 514)),
            logging.handlers.logging.StreamHandler(sys.stdout)]

logging.basicConfig(handlers=handlers, level=logging.DEBUG)

logging.info("ss")
