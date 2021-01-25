import paho.mqtt.client as mqtt
import json
import rt2000BT
import time
from rt2000BT import poller
import logging

import config


class Worker(object):
    def __init__(self):
        self.valve = rt2000BT.Valve(config.mac, None)

    # noinspection PyMethodMayBeStatic,PyUnusedLocal
    def on_connect(self, client, userdata, flags, rc):
        logging.info("Successfully connected to MQTT server")
        client.publish("{}/State".format(config.mqtt_topic), payload="Online", retain=True)
        logging.info("error = " + str(rc))
        poller.poll_valve(self.valve, client)
        client.subscribe("domoticz/out")

    # noinspection PyMethodMayBeStatic,PyUnusedLocal
    def on_message(self, client, userdata, msg):
        my_json = msg.payload.decode('utf8')
        data = json.loads(my_json)
        idx = int(data["idx"])
        if idx == config.thermostat_idx:
            new__temp = float(data["svalue1"])
            logging.info("New value: %sC", new__temp)
            logging.info("Valve last: %sC", self.valve.set_point_temp)
            self.valve.update_temperature(new__temp)

    def on_disconnect(self, client, userdata, rc):
        client.publish("{}/State".format(config.mqtt_topic), payload="Offline", retain=True)
        logging.info("Disconnected from MQTT client")

    # noinspection PyTypeChecker
    def run(self):
        client = mqtt.Client()
        client.on_connect = self.on_connect
        client.on_message = self.on_message
        client.on_disconnect = self.on_disconnect
        client.username_pw_set(config.mqtt_user, password=config.mqtt_pass)
        client.will_set("{}/State".format(config.mqtt_topic), payload="Offline", retain=True)
        client.connect(config.mqtt_server_ip, config.mqtt_server_port, 60)
        client.loop_start()

        while True:
            time.sleep(600)
            logging.info("New Loop")
            client.loop_stop()
            poller.poll_valve(self.valve, client)
            client.loop_start()
