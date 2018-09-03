#!/usr/bin/python3
'''
Created on 18 mar 2018

@author: Mariusz Wincior
'''

import gatt
import struct
import domobridgeOld
import sys

SETTEMP_IDX = 1801
TEMPACT_IDX = 1802
BATTERY_IDX = 1803
MANUAL_IDX = 2132

SERVICE_ID = "47e9ee00-47e9-11e4-8939-164230d1df67"

STATUS_ID = "47e9ee2a-47e9-11e4-8939-164230d1df67"

SETTINGS_ID = "47e9ee2b-47e9-11e4-8939-164230d1df67"

BATTERY_ID = "47e9ee2c-47e9-11e4-8939-164230d1df67"

PIN_ID = "47e9ee30-47e9-11e4-8939-164230d1df67"



manager = gatt.DeviceManager(adapter_name='hci0')

class AnyDevice(gatt.Device):
    _is_settings_readed = False
    _is_status_readed = False
    _is_battery_readed = False
    battery = 255
    current_temp = 0
    setpoint_temp = 0
    mode_auto = -1
    def services_resolved(self):
        super().services_resolved()

        device_information_service = next(
            s for s in self.services
            if s.uuid == SERVICE_ID)


        firmware_version_characteristic = next(
            c for c in device_information_service.characteristics
            if c.uuid == PIN_ID)

        firmware_version_characteristic.write_value(bytearray(b'\x00\x00\x00\x00'))
    def connect_succeeded(self):
        super().connect_succeeded()
        print("[%s] Connected" % (self.mac_address))

    def connect_failed(self, error):
        super().connect_failed(error)
        print("[%s] Connection failed: %s" % (self.mac_address, str(error)))
        sys.exit()

    def disconnect_succeeded(self):
        super().disconnect_succeeded()
        print("[%s] Disconnected" % (self.mac_address))    

    def characteristic_value_updated(self, characteristic, value):
        print("begin loop")
        self.disconnect()
        self.manager.stop()
        
    def characteristic_write_value_succeeded(self, characteristic):

        if(characteristic.uuid == PIN_ID):
            print("Write PIN successful.")
            device_information_service = next(
                s for s in self.services
                if s.uuid == SERVICE_ID)
            actual = next(
            d for d in device_information_service.characteristics
                if d.uuid == STATUS_ID)
            if(domobridgeOld.is_Switch_On(MANUAL_IDX)):
                print("Trying to set manual..")
                actual.write_value(bytearray(b'\x01'))
            else:
                print("Trying to set auto..")
                actual.write_value(bytearray(b'\x00'))
        elif(characteristic.uuid == STATUS_ID):
            print("Status updated!")
            self.disconnect()
            self.manager.stop()

    def characteristic_write_value_failed(self, characteristic, error):
        print("Write failed. "+str(error))
        self.disconnect()
        self.manager.stop()


device = AnyDevice(mac_address='9E:5F:48:89:87:D5', manager=manager)
device.connect()

manager.run()