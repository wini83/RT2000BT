import socket
import paho.mqtt.client as mqtt
import json

import config

def on_connect(client, userdata, flags, rc):
    print("error = " + str(rc))

    client.subscribe("domoticz/out")


def on_message(client, userdata, msg):
    my_json = msg.payload.decode('utf8')
    data = json.loads(my_json)
    idx = int(data["idx"])
    if idx == config.thermostat_idx:
        print("New value: {}C".format(data["svalue1"]))


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.username_pw_set(config.mqtt_user, password=config.mqtt_pass)
client.connect(config.mqtt_server_ip, config.mqtt_server_port, 60)

client.loop_forever()