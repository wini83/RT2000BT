import os


mqtt_server_ip = os.getenv("MQTT_HOST", "127.0.0.1")
mqtt_server_port = int(os.getenv("MQTT_PORT", "1883"))
mqtt_user = os.getenv("MQTT_USER", "")
mqtt_pass = os.getenv("MQTT_PASS", "")

mac = os.getenv("COMET_MAC", "9E:5F:48:89:87:D5")
mqtt_topic = os.getenv("MQTT_TOPIC", "comet/lv1")
poll_interval_seconds = int(os.getenv("POLL_INTERVAL_SECONDS", "300"))
ble_timeout_seconds = float(os.getenv("BLE_TIMEOUT_SECONDS", "15"))
