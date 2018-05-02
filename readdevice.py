'''
Created on 17 mar 2018

@author: Mariusz Wincior
'''
import gatt
import struct
import domobridge

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
    is_settings_readed = False
    is_status_readed = False
    is_battery_readed = False
    battery = 255
    ist_wert = 0
    soll_wert = 0
    mode = -1
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
        self.manager.stop()

    def disconnect_succeeded(self):
        super().disconnect_succeeded()
        print("[%s] Disconnected" % (self.mac_address))    

    def characteristic_value_updated(self, characteristic, value):
        print("begin loop")
        if(characteristic.uuid == SETTINGS_ID):
            liczby = struct.unpack('bbbbbbb', value)
            self.ist_wert = str(liczby[0]/2)
            self.soll_wert= str(liczby[1]/2)
            self.is_settings_readed = True
            print("Temperatures readed")
            device_information_service = next(
            s for s in self.services
            if s.uuid == SERVICE_ID)
            actual = next(
            d for d in device_information_service.characteristics
                if d.uuid == STATUS_ID)        
            actual.read_value()
            print("read")
        if(characteristic.uuid == STATUS_ID):
            print("status loop!")
            bytes_data = struct.unpack('bbb', value)
            self.is_status_readed = True
            self.mode = bytes_data[0]
            print(str(self.mode))
            device_information_service = next(
            s for s in self.services
            if s.uuid == SERVICE_ID)
            actual = next(
            d for d in device_information_service.characteristics
                if d.uuid == BATTERY_ID)        
            actual.read_value()
        if(characteristic.uuid == BATTERY_ID):
            print("battery loop")
            bytes_data = struct.unpack('b', value)
            print (bytes_data[0])
            self.is_battery_readed = True
            self.battery = bytes_data[0]
            print("Battery:"+str(self.battery))
        if(self.is_settings_readed == True and self.is_status_readed == True and self.is_battery_readed == True):
            print(domobridge.set_value(TEMPACT_IDX, self.ist_wert))
            print(domobridge.set_value(SETTEMP_IDX, self.soll_wert))
            print(domobridge.set_value(BATTERY_IDX, self.battery))
            print(domobridge.set_switch(MANUAL_IDX, self.mode))
            print("alles ok! disconnecting...")
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


device = AnyDevice(mac_address='9E:5F:48:89:87:D5', manager=manager)
device.connect()

manager.run()