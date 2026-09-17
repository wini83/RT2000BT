import os
from dotenv import load_dotenv

load_dotenv()

log_level = os.getenv("LOG_LEVEL", "INFO").upper()
ble_lib_log_level = os.getenv("BLE_LIB_LOG_LEVEL", "WARNING").upper()

mqtt_server_ip = os.getenv("MQTT_HOST", "127.0.0.1")
mqtt_server_port = int(os.getenv("MQTT_PORT", "1883"))
mqtt_user = os.getenv("MQTT_USER", "")
mqtt_pass = os.getenv("MQTT_PASS", "")

mac = os.getenv("COMET_MAC", "9E:5F:48:89:87:D5")
mqtt_topic = os.getenv("MQTT_TOPIC", "rt2000bt/lv1")
poll_interval_seconds = int(os.getenv("POLL_INTERVAL_SECONDS", "300"))
retry_interval_seconds = int(os.getenv("RETRY_INTERVAL_SECONDS", "30"))
ble_timeout_seconds = float(os.getenv("BLE_TIMEOUT_SECONDS", "15"))

ha_discovery_prefix = os.getenv("HA_DISCOVERY_PREFIX", "homeassistant")
ha_device_id = os.getenv("HA_DEVICE_ID", "rt2000bt_lv1")
ha_device_name = os.getenv("HA_DEVICE_NAME", "RT2000BT LV1")
