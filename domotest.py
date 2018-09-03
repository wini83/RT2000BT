'''
Created on 17 mar 2018

@author: Mariusz Wincior
'''
import domobridgeOld
ist = 17.0
soll = 23.0

SETTEMP_IDX = 1801
TEMPACT_IDX = 1802
BATTERY_IDX = 1803
MANUAL_IDX = 2132

#print(domobridgeOld.set_value(SETTEMP_IDX, soll))
#print(domobridgeOld.set_value(TEMPACT_IDX, ist))

#data = domobridgeOld.domoticz_set_switch(MANUAL_IDX, 0)
#print(domobridgeOld.print_raw_json(data))

#print(domobridgeOld.set_switch(MANUAL_IDX, 0))

#print(domobridgeOld.set_value(BATTERY_IDX, 80))

#print(domobridgeOld.is_Switch_On(MANUAL_IDX))

print(domobridgeOld.read_SetPoint(SETTEMP_IDX))
