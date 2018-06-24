#!/usr/bin/python3
'''
Created on 20 mar 2018

@author: Mariusz Wincior
'''
#!/usr/bin/python3
'''
Created on 18 mar 2018

@author: Mariusz Wincior
'''

import gatt
import struct
import domobridge
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
	bajty = []
	is_settings_readed = False
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
		if(characteristic.uuid == SETTINGS_ID):
			self.bajty = struct.unpack('bbbbbbb', value)
			self.is_settings_readed = True
			print("Temperatures readed, actual values are:")
			print(self.bajty, end=" ")
			self.bajty = list(self.bajty)
			settemp = domobridge.read_SetPoint(SETTEMP_IDX)
			print("sasa"+str(settemp))
			if(settemp != -255):
				if(settemp>15 and settemp < 30):
					if(settemp*2 != self.bajty[1]):
						self.bajty[1]=settemp*2
						print("new values:")
						print(self.bajty, end=" ")
						device_information_service = next(
						s for s in self.services
						if s.uuid == SERVICE_ID)
						actual = next(
						d for d in device_information_service.characteristics
							if d.uuid == SETTINGS_ID)
						actual.write_value(struct.pack('bbbbbbb', self.bajty[0],self.bajty[1],self.bajty[2],self.bajty[3],self.bajty[4],self.bajty[5],self.bajty[6]))
					else:
						print("Values are identical, nothing to change!")
				else:
					print("Wrong domoticz value!")
			else:
				print("Error reading domoticz value!")
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
				if d.uuid == SETTINGS_ID)		   
			actual.read_value()
		if(characteristic.uuid == SETTINGS_ID):
			print("temp zapisana")
			self.disconnect()
			self.manager.stop()
		

	def characteristic_write_value_failed(self, characteristic, error):
		print("Write failed. "+str(error))
		self.disconnect()
		self.manager.stop()


device = AnyDevice(mac_address='9E:5F:48:89:87:D5', manager=manager)
device.connect()
manager.run()