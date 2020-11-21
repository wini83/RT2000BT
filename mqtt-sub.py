import paho.mqtt.client as mqtt
import json
import rt2000BT
import time
from rt2000BT import poller

import config


class Worker(object):
    def __init__(self):
        self.valve = rt2000BT.Valve(config.mac, None)

    def on_connect(self, client, userdata, flags, rc):
        print("error = " + str(rc))

        client.subscribe("domoticz/out")

    def on_message(self, client, userdata, msg):
        my_json = msg.payload.decode('utf8')
        data = json.loads(my_json)
        idx = int(data["idx"])
        if idx == config.thermostat_idx:
            new__temp = float(data["svalue1"])
            print("New value: {}C".format(new__temp))
            print("Valve last: {}C".format(self.valve.set_point_temp))
            self.valve.update_temperature(new__temp)

    def run(self):
        valve = rt2000BT.Valve(config.mac, None)

        poller.poll_valve(valve)

        client = mqtt.Client()
        client.on_connect = self.on_connect
        client.on_message = self.on_message
        client.username_pw_set(config.mqtt_user, password=config.mqtt_pass)
        client.connect(config.mqtt_server_ip, config.mqtt_server_port, 60)

        client.loop_start()

        while True:
            time.sleep(600)
            print(time.ctime())
            client.loop_stop()
            poller.poll_valve(valve)
            client.loop_start()
