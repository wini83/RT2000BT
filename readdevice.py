'''
Created on 17 mar 2018

@author: Mariusz Wincior
'''

import gatt
import rt2000BT
import domobridge as dom

SETPOINT_IDX = 4094
TEMPACT_IDX = 1802
BATTERY_IDX = 1803
MANUAL_IDX = 2132

DOMOTICZ_IP = "192.168.1.100"

DOMOTICZ_PORT = "8050"



manager = gatt.DeviceManager(adapter_name='hci0')
valve = rt2000BT.downloadDevice(mac_address='9E:5F:48:89:87:D5', manager=manager)
valve.connect()
manager.run()
print("-------------------------------------------------")
if(valve.is_download_succesful):
    print("Current Temp = " + str(valve.current_temp))
    print("Setpoint = " + str(valve.setpoint_temp))
    print("Battery = " + str(valve.battery))
    if(valve.mode_auto == 0):
        print("Auto Mode")
    elif(valve.mode_auto == 1):
        print("Manual Mode")
    else:
        print("Wrong Mode")
    server = dom.Server(address=DOMOTICZ_IP, port=DOMOTICZ_PORT)
    dev_act = dom.device(server,TEMPACT_IDX)
    dev_set = dom.device(server,SETPOINT_IDX)
    dev_mode =  dom.device(server,MANUAL_IDX)
    if(valve.current_temp != dev_act.temp):
        dev_act.update(0, str(valve.current_temp))