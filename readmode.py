import gatt
import time
import binascii
import struct

manager = gatt.DeviceManager(adapter_name='hci0')

class AnyDevice(gatt.Device):
	is_pin_seted = False 
	def services_resolved(self):
		super().services_resolved()

		device_information_service = next(
			s for s in self.services
			if s.uuid == '47e9ee00-47e9-11e4-8939-164230d1df67')

		firmware_version_characteristic = next(
			c for c in device_information_service.characteristics
			if c.uuid == '47e9ee30-47e9-11e4-8939-164230d1df67')

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
		liczby = struct.unpack('bbb', value)
		print (liczby[0])
		
		self.disconnect()
		self.manager.stop()
		
	def characteristic_write_value_succeeded(self, characteristic):
		print("Write successful.")
		device_information_service = next(
			s for s in self.services
			if s.uuid == '47e9ee00-47e9-11e4-8939-164230d1df67')
		actual = next(
		d for d in device_information_service.characteristics
			if d.uuid == '47e9ee2a-47e9-11e4-8939-164230d1df67')			
		actual.read_value()

	def characteristic_write_value_failed(self, characteristic, error):
		print("Write failed. "+str(error))


device = AnyDevice(mac_address='9E:5F:48:89:87:D5', manager=manager)
device.connect()

manager.run()


