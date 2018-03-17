import gatt
import time
import binascii

manager = gatt.DeviceManager(adapter_name='hci0')

class AnyDevice(gatt.Device):
    def services_resolved(self):
        super().services_resolved()

        device_information_service = next(
            s for s in self.services
            if s.uuid == '47e9ee00-47e9-11e4-8939-164230d1df67')

        firmware_version_characteristic = next(
            c for c in device_information_service.characteristics
            if c.uuid == '47e9ee30-47e9-11e4-8939-164230d1df67')

        firmware_version_characteristic.write_value(bytearray(b'\x00\x00\x00\x00'))
			

    def characteristic_value_updated(self, characteristic, value):
        print("Firmware version:", binascii.hexlify(value))# value.decode("utf-8"))
		
    def characteristic_write_value_succeeded(self, characteristic):
        print("Write successful.")
        device_information_service = next(
            s for s in self.services
            if s.uuid == '47e9ee00-47e9-11e4-8939-164230d1df67')
        actual = next(
        d for d in device_information_service.characteristics
            if d.uuid == '47e9ee2b-47e9-11e4-8939-164230d1df67')
			
        actual.read_value()

    def characteristic_write_value_failed(self, characteristic, error):
        print("Write failed. "+str(error))


device = AnyDevice(mac_address='9E:5F:48:89:87:D5', manager=manager)
device.connect()

manager.run()