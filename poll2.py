import pygatt

adapter = pygatt.GATTToolBackend()

SERVICE_ID = "47e9ee00-47e9-11e4-8939-164230d1df67"

STATUS_ID = "47e9ee2a-47e9-11e4-8939-164230d1df67"

SETTINGS_ID = "47e9ee2b-47e9-11e4-8939-164230d1df67"

BATTERY_ID = "01051304-4700-e9e4-8939-164230d1df67"

BATTERY_ID_ALt = "47e9ee2c-47e9-11e4-8939-164230d1df67"

PIN_ID: str = "47e9ee30-47e9-11e4-8939-164230d1df67"

try:
    adapter.start()
    device = adapter.connect('9E:5F:48:89:87:D5')
    pin = [0, 0, 0, 0]
    pin_array = bytearray(pin)

    #print(device.discover_characteristics())

    device.char_write(PIN_ID, bytearray(b'\x00\x00\x00\x00'))

    settings = list(device.char_read(SETTINGS_ID))
    print(settings)

    current_temp = settings[0] / 2
    setpoint_temp = settings[1] / 2

    print("Current Temp: domoticz=N/A C; valve ={}C".format(current_temp))
    print("Set Temp: domoticz=N/A C; valve ={}C".format(setpoint_temp))

    battery = list(device.char_read(BATTERY_ID_ALt))[0]
    print("Battery: domoticz=N/A C; valve ={}%".format(battery))

    status = list(device.char_read(STATUS_ID))[0]
    print (status)
finally:
    adapter.stop()
