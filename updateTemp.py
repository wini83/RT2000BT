#!/usr/bin/python3


import DomoticzAPI as dom
import config
import rt2000BT

print("---------Connect to DOMOTICZ---------------------")
server = dom.Server(address=config.domoticz_ip, port=config.domoticz_port)
dom_dev_setpoint = dom.Device(server, config.thermostat_idx)
print("Setpoint in Domoticz: {}°C".format(dom_dev_setpoint.temp))

print("---------Connect to Valve-------------------------")

valve = rt2000BT.Valve(config.mac, None)

result = valve.update_temperature(dom_dev_setpoint.temp)

print(result)