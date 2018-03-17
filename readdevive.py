'''
Created on 17 mar 2018

@author: Mariusz Wincior
'''
import gatt
import time
import binascii
import struct
import domobridge

SERVICE_ID = "47e9ee00-47e9-11e4-8939-164230d1df67"

STATUS_ID = "47e9ee2a-47e9-11e4-8939-164230d1df67"

SETTINGS_ID = "47e9ee2b-47e9-11e4-8939-164230d1df67"

BATTERY_ID = "47e9ee2c-47e9-11e4-8939-164230d1df67"

PIN_ID = "47e9ee30-47e9-11e4-8939-164230d1df67"



manager = gatt.DeviceManager(adapter_name='hci0')

class AnyDevice(gatt.Device):
    is_pin_seted = False 
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

    def disconnect_succeeded(self):
        super().disconnect_succeeded()
        print("[%s] Disconnected" % (self.mac_address))    

    def characteristic_value_updated(self, characteristic, value):
        liczby = struct.unpack('bbbbbbb', value)
        ist = str(liczby[0]/2)
        soll =str(liczby[1]/2)
        print(domobridge.set_temp(1802, ist))
        print(domobridge.set_temp(1801, soll))
        
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


device = AnyDevice(mac_address='9E:5F:48:89:87:D5', manager=manager)
device.connect()

manager.run()


