#!/usr/bin/python3
'''
Created on 18 mar 2018

@author: Mariusz Wincior
'''

import gatt
import rt2000BT
import domobridge as dom

MANUAL_IDX = 2132
DOMOTICZ_IP = "192.168.1.100"
DOMOTICZ_PORT = "8050"

print("-------------------------------------------------")

manager = gatt.DeviceManager(adapter_name='hci0')
valve = rt2000BT.downloadDevice(mac_address='9E:5F:48:89:87:D5', manager=manager)

server = dom.Server(address=DOMOTICZ_IP, port=DOMOTICZ_PORT)
dev_mode =  dom.Device(server,MANUAL_IDX)
desired = False;
print(dev_mode.data) 

# if(valve.is_polling_succesful):
#       
# else:
#     print("Something went wrong...")

