'''
Created on 17 mar 2018

@author: Mariusz Wincior
'''
import domobridge
ist = 17.0
soll = 23.0

SETTEMP_IDX = 1801
TEMPACT_IDX = 1802
BATTERY_IDX = 1803
MANUAL_IDX = 2132

#print(domobridge.set_value(SETTEMP_IDX, soll))
#print(domobridge.set_value(TEMPACT_IDX, ist))

#data = domobridge.domoticz_set_switch(MANUAL_IDX, 0)
#print(domobridge.print_raw_json(data))

#print(domobridge.set_switch(MANUAL_IDX, 0))

print(domobridge.set_value(BATTERY_IDX, 80))
