import pygatt

SERVICE_ID = "47e9ee00-47e9-11e4-8939-164230d1df67"

STATUS_ID = "47e9ee2a-47e9-11e4-8939-164230d1df67"

SETTINGS_ID = "47e9ee2b-47e9-11e4-8939-164230d1df67"

BATTERY_ID = "01051304-4700-e9e4-8939-164230d1df67"

BATTERY_ID_ALt = "47e9ee2c-47e9-11e4-8939-164230d1df67"

PIN_ID = "47e9ee30-47e9-11e4-8939-164230d1df67"


class Valve:
    is_polling_successful: bool

    def __init__(self, mac, pin):
        self.adapter = pygatt.GATTToolBackend()
        self._is_settings_acquired = False
        self._is_status_acquired = False
        self._is_battery_acquired = False
        self.mac = mac
        self.pin = pin
        self.battery = 255
        self.current_temp = 0
        self.set_point_temp = 0
        self.mode_auto = -1
        self.desired_temp = 0
        self.is_polling_successful = False

    def poll(self):
        result = False
        try:
            self.adapter.start()
            device = self.adapter.connect(self.mac)
            device.char_write(PIN_ID, bytearray(b'\x00\x00\x00\x00'))
            settings = list(device.char_read(SETTINGS_ID))
            self.current_temp = settings[0] / 2
            self.set_point_temp = settings[1] / 2
            self.battery = list(device.char_read(BATTERY_ID_ALt))[0]
            self.mode_auto = list(device.char_read(STATUS_ID))[0]
            result = True
        finally:
            self.adapter.stop()
        return result

    # value true = manual; false = auto
    def update_mode(self, value):
        try:
            result = False
            self.adapter.start()
            device = self.adapter.connect(self.mac)
            device.char_write(PIN_ID, bytearray(b'\x00\x00\x00\x00'))
            current_mode = list(device.char_read(STATUS_ID))[0]
            payload = int(value == True)
            if payload != current_mode:
                print("Update is possible")
                if (value):
                    print("Trying to set manual..")
                    device.char_write(STATUS_ID, bytearray(b'\x01'))
                else:
                    print("Trying to set auto..")
                    device.char_write(STATUS_ID, bytearray(b'\x00'))
            result = True
        finally:
            self.adapter.stop()
        return

    def update_temperature(self, value):
        try:
            result = False
            self.adapter.start()
            device = self.adapter.connect(self.mac)
            device.char_write(PIN_ID, bytearray(b'\x00\x00\x00\x00'))
            settings = list(device.char_read(SETTINGS_ID))
            print(settings)
            current_setpoint = settings[1] / 2
            print("current:{} payload{}".format(current_setpoint, value))
            if current_setpoint != value:
                print("Update is possible")
                settings[1] = value*2
                print(settings)
                device.char_write(SETTINGS_ID, bytearray(settings))
            result = True
        finally:
            self.adapter.stop()
        return
