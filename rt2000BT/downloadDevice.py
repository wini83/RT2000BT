'''
Created on 3 wrz 2018

@author: Mariusz Wincior
'''
import gatt
import struct
import sys

SERVICE_ID = "47e9ee00-47e9-11e4-8939-164230d1df67"

STATUS_ID = "47e9ee2a-47e9-11e4-8939-164230d1df67"

SETTINGS_ID = "47e9ee2b-47e9-11e4-8939-164230d1df67"

BATTERY_ID = "47e9ee2c-47e9-11e4-8939-164230d1df67"

PIN_ID = "47e9ee30-47e9-11e4-8939-164230d1df67"

class downloadDevice(gatt.Device):
    _is_settings_readed = False
    _is_status_readed = False
    _is_battery_readed = False
    battery = 255
    current_temp = 0
    setpoint_temp = 0
    mode_auto = -1
    is_download_succesful = False
    
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
         

    def characteristic_value_updated(self, characteristic, value):
        if(characteristic.uuid == SETTINGS_ID):
            print("characteristic SETTINGS received!")
            liczby = struct.unpack('bbbbbbb', value)
            self.current_temp = str(liczby[0]/2)
            self.setpoint_temp= str(liczby[1]/2)
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
            self.is_download_succesful = True
            self.disconnect()
            self.manager.stop()
        
    def characteristic_write_value_succeeded(self, characteristic):
        print("Write successful.")
        device_information_service = next(
            s for s in self.services
            if s.uuid == SERVICE_ID)
        actual = next(
        d for d in device_information_service.characteristics
            if d.uuid == SETTINGS_ID)           
        actual.read_value()

    def characteristic_write_value_failed(self, characteristic, error):
        print("Write failed. "+str(error))
        self.manager.stop()
