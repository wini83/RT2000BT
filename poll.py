import rt2000BT

import config
import poller

valve = rt2000BT.Valve(config.mac, None)

poller.poll_valve(valve)
