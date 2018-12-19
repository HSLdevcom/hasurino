# -*- coding: utf-8 -*-
"""Subscribe with an MQTT topic filter."""

from datetime import datetime
import logging

import paho.mqtt.client as mqtt


LOG = logging.getLogger(__name__)
PAHO_LOG = logging.getLogger("paho.mqtt.client")


def create_mqtt_subscriber(config, queue):
    """Create an MQTT subscriber."""

    log_match = {
        mqtt.MQTT_LOG_DEBUG: logging.DEBUG,
        mqtt.MQTT_LOG_INFO: logging.INFO,
        mqtt.MQTT_LOG_NOTICE: logging.INFO,
        mqtt.MQTT_LOG_WARNING: logging.WARNING,
        mqtt.MQTT_LOG_ERR: logging.ERROR,
    }

    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            LOG.info("MQTT connection attempt succeeded")
            LOG.info("MQTT subscription attempt starting")
            client.subscribe(config["topic"], qos=config["qos"])
        else:
            LOG.warning(
                "MQTT connection attempt failed: %s", mqtt.connack_string(rc)
            )

    def on_subscribe(client, userdata, mid, granted_qos):
        LOG.info("MQTT subscription succeeded with QoS %s", granted_qos[0])

    def on_disconnect(client, userdata, rc):
        if rc == 0:
            LOG.info("MQTT disconnection succeeded")
        else:
            LOG.warning("MQTT connection lost")

    def on_log(client, userdata, level, buf):
        log_level = log_match[level]
        PAHO_LOG.log(log_level, buf)

    def on_message(client, userdata, message):
        received_at = datetime.utcnow().isoformat(sep="T", timespec="auto")
        queue.put((received_at, message.topic, message.payload))

    client = mqtt.Client(
        client_id=config["client_id"],
        clean_session=config["clean_session"],
        userdata=None,
        protocol=mqtt.MQTTv311,
        transport=config["transport"],
    )
    client.max_inflight_messages_set(config["max_inflight_messages"])
    tls_path = config.get("ca_certs_path", None)
    if tls_path is not None:
        client.tls_set(ca_certs=tls_path)
    client.enable_logger(logger=None)
    client.reconnect_delay_set(
        min_delay=config["reconnect_min_delay_in_s"],
        max_delay=config["reconnect_max_delay_in_s"],
    )
    username = config.get("username", None)
    password = config.get("password", None)
    if username is not None and password is not None:
        client.username_pw_set(username, password=password)

    client.on_connect = on_connect
    client.on_subscribe = on_subscribe
    client.on_disconnect = on_disconnect
    client.on_log = on_log
    client.on_message = on_message

    client.connect_async(config["host"], port=config["port"])

    return client
