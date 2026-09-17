import json
from unittest.mock import MagicMock, patch

import config
from worker import Worker


def make_worker():
    with patch("worker.Valve"):
        return Worker()


def test_poll_success_publishes_online_and_last_seen():
    worker = make_worker()
    client = MagicMock()
    worker.consecutive_poll_failures = 2

    worker._record_poll_success(client)

    assert worker.consecutive_poll_failures == 0
    client.publish.assert_any_call(
        f"{config.mqtt_topic}/availability",
        payload="online",
        qos=0,
        retain=True,
    )
    last_seen_calls = [
        call
        for call in client.publish.call_args_list
        if call.args and call.args[0] == f"{config.mqtt_topic}/last_seen"
    ]
    assert len(last_seen_calls) == 1
    assert last_seen_calls[0].kwargs["retain"] is True


def test_first_failure_uses_retry_interval_without_publishing_offline():
    worker = make_worker()
    client = MagicMock()

    worker._record_poll_failure(client)

    assert worker.consecutive_poll_failures == 1
    assert worker._next_poll_interval() == config.retry_interval_seconds
    assert not any(
        call.args
        and call.args[0] == f"{config.mqtt_topic}/availability"
        and call.kwargs.get("payload") == "offline"
        for call in client.publish.call_args_list
    )


def test_second_failure_still_uses_retry_interval():
    worker = make_worker()
    client = MagicMock()

    worker._record_poll_failure(client)
    worker._record_poll_failure(client)

    assert worker.consecutive_poll_failures == 2
    assert worker._next_poll_interval() == config.retry_interval_seconds


def test_third_failure_publishes_offline_and_returns_to_normal_interval():
    worker = make_worker()
    client = MagicMock()

    for _ in range(3):
        worker._record_poll_failure(client)

    assert worker.consecutive_poll_failures == 3
    assert worker._next_poll_interval() == config.poll_interval_seconds
    client.publish.assert_any_call(
        f"{config.mqtt_topic}/availability",
        payload="offline",
        qos=0,
        retain=True,
    )


def test_fourth_failure_does_not_publish_offline_again():
    worker = make_worker()
    client = MagicMock()

    for _ in range(4):
        worker._record_poll_failure(client)

    offline_calls = [
        call
        for call in client.publish.call_args_list
        if call.args
        and call.args[0] == f"{config.mqtt_topic}/availability"
        and call.kwargs.get("payload") == "offline"
    ]
    assert len(offline_calls) == 1
    assert worker._next_poll_interval() == config.poll_interval_seconds


def test_success_after_failures_resets_retry_state():
    worker = make_worker()
    client = MagicMock()

    worker._record_poll_failure(client)
    worker._record_poll_failure(client)
    assert worker._next_poll_interval() == config.retry_interval_seconds

    worker._record_poll_success(client)

    assert worker.consecutive_poll_failures == 0
    assert worker._next_poll_interval() == config.poll_interval_seconds


def test_discovery_publishes_climate_battery_and_last_seen():
    worker = make_worker()
    client = MagicMock()

    worker._publish_discovery(client)

    published = {call.args[0]: json.loads(call.kwargs["payload"]) for call in client.publish.call_args_list}
    climate_topic = f"{config.ha_discovery_prefix}/climate/{config.ha_device_id}/config"
    battery_topic = f"{config.ha_discovery_prefix}/sensor/{config.ha_device_id}_battery/config"
    last_seen_topic = f"{config.ha_discovery_prefix}/sensor/{config.ha_device_id}_last_seen/config"

    assert {climate_topic, battery_topic, last_seen_topic} <= published.keys()
    climate = published[climate_topic]
    assert climate["temperature_command_topic"] == f"{config.mqtt_topic}/setpoint/set"
    assert climate["temperature_state_topic"] == f"{config.mqtt_topic}/setpoint"
    assert climate["mode_command_topic"] == f"{config.mqtt_topic}/mode/set"
    assert climate["mode_state_topic"] == f"{config.mqtt_topic}/mode"
    assert climate["modes"] == ["heat", "auto"]
    assert climate["availability_topic"] == f"{config.mqtt_topic}/availability"


def test_home_assistant_birth_republishes_discovery():
    worker = make_worker()
    client = MagicMock()
    msg = MagicMock()
    msg.topic = "homeassistant/status"
    msg.payload = b"online"

    worker.on_message(client, None, msg)

    discovery_topics = [call.args[0] for call in client.publish.call_args_list]
    assert f"{config.ha_discovery_prefix}/climate/{config.ha_device_id}/config" in discovery_topics
