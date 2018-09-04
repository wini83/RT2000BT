'''
Created on 17 mar 2018

@author: Mariusz Wincior
'''

import gatt
import rt2000BT
import domobridge as dom

SETPOINT_IDX = 4094
TEMPACT_IDX = 1802
MANUAL_IDX = 2132

DOMOTICZ_IP = "192.168.1.100"
DOMOTICZ_PORT = "8050"


manager = gatt.DeviceManager(adapter_name='hci0')
valve = rt2000BT.downloadDevice(mac_address='9E:5F:48:89:87:D5', manager=manager)
valve.pool()
print("-------------------------------------------------")
if(valve.is_polling_succesful):    
    print("Battery = " + str(valve.battery))
    server = dom.Server(address=DOMOTICZ_IP, port=DOMOTICZ_PORT)
    dev_act = dom.Device(server,TEMPACT_IDX)
    dev_set = dom.Device(server,SETPOINT_IDX)
    dev_mode =  dom.Device(server,MANUAL_IDX)
    print("Current Temp: domoticz={}C; valve ={}C".format(dev_act.temp,valve.current_temp))
    if(valve.current_temp != dev_act.temp):
        print("Updating Current Temp in domoticz...")
        dev_act.update(0, "{}&battery={}".format(valve.current_temp,valve.battery))
    print("Setpoint: domoticz={}C; valve ={}C".format(dev_set.temp,valve.setpoint_temp))
    if(valve.setpoint_temp != dev_set.temp):
        print("Updating Setpoint in domoticz...")
        dev_set.update(0, "{}&battery={}".format(valve.setpoint_temp,valve.battery))
    if(valve.mode_auto == 0):
        if(dev_mode.data == "Off"):
            print("MODE: domoticz=auto; valve=auto")
        else:
            print("MODE: domoticz=manual; valve=auto")
            print("Updating MODE in domoticz...")
            dev_mode.updateSwitch("Off")
    elif(valve.mode_auto == 1):
        if(dev_mode.data == "On"):
            print("MODE: domoticz=manual; valve=manual")
        else:
            print("Mode: domoticz=auto; valve=manual")
            print("Updating Mode in domoticz...")
            dev_mode.updateSwitch("On")
    else:
        print("Wrong Mode")