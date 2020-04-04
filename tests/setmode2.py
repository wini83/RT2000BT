import rt2000BT
import DomoticzAPI as dom

import config

valve = rt2000BT.Valve(config.mac, None)


print("-------------------------------------------------")

valve.update_mode(False)