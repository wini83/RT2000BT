import asyncio
import json
from unittest.mock import AsyncMock, MagicMock, patch

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


def test_command_retry_succeeds_after_transient_failure():
    worker = make_worker()
    operation = AsyncMock(side_effect=[False, True])

    with patch("worker.asyncio.sleep", new=AsyncMock()) as sleep:
        result = asyncio.run(worker._run_command_with_retry(operation, "temperature update"))

    assert result is True
    assert operation.await_count == 2
    sleep.assert_awaited_once_with(worker.COMMAND_RETRY_DELAY_SECONDS)


def test_command_retry_stops_after_max_attempts():
    worker = make_worker()
    operation = AsyncMock(return_value=False)

    with patch("worker.asyncio.sleep", new=AsyncMock()) as sleep:
        result = asyncio.run(worker._run_command_with_retry(operation, "temperature update"))

    assert result is False
    assert operation.await_count == worker.COMMAND_ATTEMPTS
    assert sleep.await_count == worker.COMMAND_ATTEMPTS - 1


def test_setpoint_command_retries_then_polls_confirmation():
    worker = make_worker()
    client = MagicMock()
    worker.valve.update_temperature = AsyncMock(side_effect=[False, True])
    worker.valve.poll = AsyncMock(return_value=True)

    with patch("worker.asyncio.sleep", new=AsyncMock()):
        asyncio.run(
            worker._handle_command(
                client, f"{config.mqtt_topic}/setpoint/set", "22.5"
            )
        )

    assert worker.valve.update_temperature.await_count == 2
    worker.valve.update_temperature.assert_awaited_with(22.5)
    worker.valve.poll.assert_awaited_once()


def test_mode_command_retries_then_polls_confirmation():
    worker = make_worker()
    client = MagicMock()
    worker.valve.update_mode = AsyncMock(side_effect=[False, True])
    worker.valve.poll = AsyncMock(return_value=True)

    with patch("worker.asyncio.sleep", new=AsyncMock()):
        asyncio.run(
            worker._handle_command(client, f"{config.mqtt_topic}/mode/set", "auto")
        )

    assert worker.valve.update_mode.await_count == 2
    worker.valve.update_mode.assert_awaited_with(False)
    worker.valve.poll.assert_awaited_once()
