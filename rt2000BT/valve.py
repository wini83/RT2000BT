import struct
import sys
from enum import Enum

SERVICE_ID = "47e9ee00-47e9-11e4-8939-164230d1df67"

STATUS_ID = "47e9ee2a-47e9-11e4-8939-164230d1df67"

SETTINGS_ID = "47e9ee2b-47e9-11e4-8939-164230d1df67"

BATTERY_ID = "01051304-4700-e9e4-8939-164230d1df67"

BATTERY_ID_ALt = "47e9ee2c-47e9-11e4-8939-164230d1df67"

PIN_ID = "47e9ee30-47e9-11e4-8939-164230d1df67"

Modus = Enum("Modus", "unknown poll update_temp set_mode")


class ValveAdapter:
    _is_settings_acquired = False
    _is_status_acquired = False
    _is_battery_acquired = False
    adapter = None
    mac = ""
    battery = 255
    current_temp = 0
    set_point_temp = 0
    mode_auto = -1
    desired_temp = 0
    desired_mode = False
    is_polling_successful = False
    mode = Modus.unknown



    def poll(self):
        self.mode = Modus.poll
        super().connect()
        self.manager.run()

    def set_mode(self, value=False):
        self.mode = Modus.set_mode
        self.desired_mode = value;
        super().connect()
        self.manager.run()