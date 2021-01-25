# noinspection PyPep8Naming
import DomoticzAPI as dom
import config
import paho.mqtt.client as mqtt
import json
import logging


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


def poll_valve(valve, client: mqtt.Client):
    is_polling_ok = valve.poll()

    print(is_polling_ok)

    if is_polling_ok:
        logging.info("Battery = %s", valve.battery)
        client.publish("{}/Battery".format(config.mqtt_topic), payload=valve.battery, qos=0, retain=False)

        server = dom.Server(address=config.domoticz_ip, port=config.domoticz_port)
        dev_mode = dom.Device(server, config.manual_idx)

        logging.info("Current Temp: %s C", valve.current_temp)
        client.publish("{}/Temp-current".format(config.mqtt_topic), payload=valve.current_temp, qos=0, retain=False)
        dom_update_temp(client, config.temp_current_idx, valve.current_temp, valve.battery)

        logging.info("Setpoint: %s C", valve.set_point_temp)
        client.publish("{}/Temp-setpoint".format(config.mqtt_topic), payload=valve.set_point_temp, qos=0, retain=False)
        dom_update_temp(client, config.setpoint_idx, valve.set_point_temp, valve.battery)

        client.publish("{}/Auto-Mode".format(config.mqtt_topic), payload=valve.mode_auto, qos=0, retain=False)
        logging.info("Mode-Auto: %s", valve.mode_auto)
        if valve.mode_auto == 0:
            if dev_mode.data == "Off":
                print("MODE: domoticz=auto; valve=auto")
            else:
                print("MODE: domoticz=manual; valve=auto")
                print("Updating MODE in domoticz...")
                dev_mode.update_switch("Off")
        elif valve.mode_auto == 1:
            if dev_mode.data == "On":
                print("MODE: domoticz=manual; valve=manual")
            else:
                print("Mode: domoticz=auto; valve=manual")
                print("Updating Mode in domoticz...")
                dev_mode.update_switch("On")
                return
        else:
            print("Wrong Mode")
    else:
        print("Something went wrong...")
