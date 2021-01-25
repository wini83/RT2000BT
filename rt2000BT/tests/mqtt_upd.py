import paho.mqtt.client as mqtt
import json


def dom_update_temp(client: mqtt.Client, idx, temp, battery, rrsi=12, qos=0, retain=False):
    json_payload = {
        "command": "udevice",
        "idx": idx,
        "nvalue": 0,
        "svalue": str(temp),
        "Battery": battery,
        "RSSI": rrsi
    }
    json_string = json.dumps(json_payload)
    print(json_string)
    client.publish("domoticz/in", payload=json_string, qos=qos, retain=retain)


client_mqtt = mqtt.Client()
client_mqtt.username_pw_set("wini", password="dupa")

client_mqtt.connect("192.168.2.100", 1883, 60)

dom_update_temp(client_mqtt, 1802, 17, 90)
