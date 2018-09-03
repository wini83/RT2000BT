'''
Created on 17 mar 2018

@author: Mariusz Wincior
'''

import domobridge
import gatt
import rt2000BT as valve

SETTEMP_IDX = 4094
TEMPACT_IDX = 1802
BATTERY_IDX = 1803
MANUAL_IDX = 2132

DOMOTICZ_IP = "192.168.1.100"

DOMOTICZ_PORT = "8050"



manager = gatt.DeviceManager(adapter_name='hci0')
device = valve.DownloadDevice(mac_address='9E:5F:48:89:87:D5', manager=manager)
device.connect()
manager.run()
print ("dupa")
print(device.battery)