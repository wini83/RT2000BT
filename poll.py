
import rt2000BT
import DomoticzAPI as dom

import config

valve = rt2000BT.Valve("9E:5F:48:89:87:D5", None)

valve.poll()

print("-------------------------------------------------")
if valve.is_polling_succesful:
    print("Battery = " + str(valve.battery))
    server = dom.Server(address=config.domoticz_ip, port=config.domoticz_port)
    dev_act = dom.Device(server,config.temp_current_idx)
    dev_set = dom.Device(server,config.setpoint_idx)
    dev_mode =  dom.Device(server,config.manual_idx)
    print("Current Temp: domoticz={}C; valve ={}C".format(dev_act.temp,valve.current_temp))
    if valve.current_temp != dev_act.temp:
        print("Updating Current Temp in domoticz...")
        dev_act.update(0, "{}&battery={}".format(valve.current_temp, valve.battery))
    print("Setpoint: domoticz={}C; valve ={}C".format(dev_set.temp, valve.setpoint_temp))
    if valve.setpoint_temp != dev_set.temp:
        print("Updating Setpoint in domoticz...")
        dev_set.update(0, "{}&battery={}".format(valve.setpoint_temp, valve.battery))
    if valve.mode_auto == 0:
        if dev_mode.data == "Off":
            print("MODE: domoticz=auto; valve=auto")
        else:
            print("MODE: domoticz=manual; valve=auto")
            print("Updating MODE in domoticz...")
            dev_mode.updateSwitch("Off")
    elif valve.mode_auto == 1:
        if dev_mode.data == "On":
            print("MODE: domoticz=manual; valve=manual")
        else:
            print("Mode: domoticz=auto; valve=manual")
            print("Updating Mode in domoticz...")
            dev_mode.updateSwitch("On")
    else:
        print("Wrong Mode")
else:
    print("Something went wrong...")