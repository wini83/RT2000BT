import rt2000BT
import DomoticzAPI as dom
import config

valve = rt2000BT.Valve(config.mac, None)

print("-------------------------------------------------")
server = dom.Server(address=config.domoticz_ip, port=config.domoticz_port)
dev_mode = dom.Device(server, config.manual_idx)
print("-------------------------------------------------")

desired = False

if (dev_mode.data == "On"):
    desired = True
    print("Status in Domoticz = manual")
elif (dev_mode.data == "Off"):
    desired = False
    print("Status in Domoticz = auto")
else:
    print("Wrong Domoticz Device state")
    exit()
result_ok = valve.update_mode(desired)
if (result_ok):
    print("Everything went fine!")
else:
    print("Something went wrong...")
