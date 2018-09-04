'''
Created on 3 wrz 2018

@author: Mariusz Wincior
'''
import gatt
import struct
import sys
from enum import Enum

SERVICE_ID = "47e9ee00-47e9-11e4-8939-164230d1df67"

STATUS_ID = "47e9ee2a-47e9-11e4-8939-164230d1df67"

SETTINGS_ID = "47e9ee2b-47e9-11e4-8939-164230d1df67"

BATTERY_ID = "47e9ee2c-47e9-11e4-8939-164230d1df67"

PIN_ID = "47e9ee30-47e9-11e4-8939-164230d1df67"

Modus = Enum("unknown","poll","update_temp","set_mode")


class downloadDevice(gatt.Device):
    _is_settings_readed = False
    _is_status_readed = False
    _is_battery_readed = False
    battery = 255
    current_temp = 0
    setpoint_temp = 0
    mode_auto = -1
    desired_temp = 0
    desired_mode = False;
    is_polling_succesful = False
    modus = Modus.unknown
    
    def poll(self):
        self.modus = Modus.poll
        super.connect()
        super.manager.run()
        
    def set_mode(self, value = False):
        self.modus = Modus.set_mode
        self.desired_mode = value;
        super.connect()
        super.manager.run()
        
    
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
        print("dupa")
        print("[%s] Connection failed: %s" % (self.mac_address, str(error)))
        self.manager.stop()
        sys.exit()

    def disconnect_succeeded(self):
        super().disconnect_succeeded()
        print("[%s] Disconnected" % (self.mac_address))
        self.manager.stop()  
         

    def characteristic_value_updated(self, characteristic, value):
        if(characteristic.uuid == SETTINGS_ID):
            print("characteristic SETTINGS received!")
            liczby = struct.unpack('bbbbbbb', value)
            self.current_temp = liczby[0]/2
            self.setpoint_temp= liczby[1]/2
            self._is_settings_readed = True
            device_information_service = next(
            s for s in self.services
            if s.uuid == SERVICE_ID)
            actual = next(
            d for d in device_information_service.characteristics
                if d.uuid == STATUS_ID)        
            actual.read_value()
        if(characteristic.uuid == STATUS_ID):
            print("characteristic STATUS received!")
            bytes_data = struct.unpack('bbb', value)
            self._is_status_readed = True
            self.mode_auto = bytes_data[0]
            device_information_service = next(
            s for s in self.services
            if s.uuid == SERVICE_ID)
            actual = next(
            d for d in device_information_service.characteristics
                if d.uuid == BATTERY_ID)        
            actual.read_value()
        if(characteristic.uuid == BATTERY_ID):
            print("characteristic BATTERY received!")
            bytes_data = struct.unpack('b', value)
            self._is_battery_readed = True
            self.battery = bytes_data[0]
        if(self._is_settings_readed == True and self._is_status_readed == True and self._is_battery_readed == True):
            self.is_polling_succesful = True
            self.disconnect()
            
    def write_value_succeeded_poll(self,characteristic):
        device_information_service = next(
            s for s in self.services
            if s.uuid == SERVICE_ID)
        actual = next(
        d for d in device_information_service.characteristics
            if d.uuid == SETTINGS_ID)           
        actual.read_value()
        
    def write_value_succeeded_setmode(self, characteristic):

        if(characteristic.uuid == PIN_ID):
            device_information_service = next(
                s for s in self.services
                if s.uuid == SERVICE_ID)
            actual = next(
            d for d in device_information_service.characteristics
                if d.uuid == STATUS_ID)
            if(self.desired_mode):
                print("Trying to set manual..")
                actual.write_value(bytearray(b'\x01'))
            else:
                print("Trying to set auto..")
                actual.write_value(bytearray(b'\x00'))
        elif(characteristic.uuid == STATUS_ID):
            print("Status updated!")
            self.disconnect()
            self.manager.stop()
        
    
        
    def characteristic_write_value_succeeded(self, characteristic):
        print("Write successful.")
        if(self.modus == Modus.poll):
            self.write_value_succeeded_poll(characteristic)
        elif(self.modus == Modus.set_mode):
            self.write_value_succeeded_setmode(characteristic)

    def characteristic_write_value_failed(self, characteristic, error):
        print("Write failed. "+str(error))
        self.manager.stop()
