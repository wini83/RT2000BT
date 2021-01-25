# noinspection PyPep8Naming
import DomoticzAPI as dom
import config
import paho.mqtt.client as mqtt
import logging


def poll_valve(valve, client: mqtt.Client):
    is_polling_ok = valve.poll()

    print(is_polling_ok)

    if is_polling_ok:
        logging.info("Battery = %s", valve.battery)
        client.publish("{}/State".format(config.mqtt_topic), payload=valve.battery, qos=0, retain=False)
        server = dom.Server(address=config.domoticz_ip, port=config.domoticz_port)
        dev_act = dom.Device(server, config.temp_current_idx)
        dev_set = dom.Device(server, config.setpoint_idx)
        dev_mode = dom.Device(server, config.manual_idx)
        print("Current Temp: domoticz={}C; valve ={}C".format(dev_act.temp, valve.current_temp))
        if valve.current_temp != dev_act.temp:
            print("Updating Current Temp in domoticz...")
            dev_act.update(0, valve.current_temp, valve.battery, None)
        print("Setpoint: domoticz={}C; valve ={}C".format(dev_set.temp, valve.set_point_temp))
        if valve.set_point_temp != dev_set.temp:
            print('Updating Setpoint in domoticz...')
            dev_set.update(0, valve.set_point_temp, valve.battery, None)
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
