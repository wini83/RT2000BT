import rt2000BT

import config

valve = rt2000BT.Valve(config.mac, None)


print("-------------------------------------------------")

valve.update_temperature(25)