# -*- coding: utf-8 -*-
"""Check for duplicate HFP messages due to MQTT QoS 1."""

import collections


def create_duplicate_checker(config):
    """Create a duplicate checker."""

    max_cache_length = config["max_cache_length_per_vehicle"]
    history = {}

    def is_duplicate(timed_message):
        is_dup = False
        received_at, topic, payload = timed_message
        unique_vehicle_id = get_unique_vehicle_id(topic)
        if unique_vehicle_id is not None:
            cached = history.get(unique_vehicle_id, None)
            message = (topic, payload)
            if cached:
                if message in cached:
                    is_dup = True
                else:
                    cached.append(message)
            else:
                deq = collections.deque(maxlen=max_cache_length)
                deq.append(message)
                history[unique_vehicle_id] = deq
        else:
            raise ValueError(
                "Unexpected HFP MQTT topic %s received at %s with payload %s"
                % received_at,
                topic,
                payload,
            )
        return is_dup

    return is_duplicate


def get_unique_vehicle_id(topic):
    """Get the unique vehicle ID from the topic of an HFP message."""
    splitted = topic.split(sep="/", maxsplit=8)
    if len(splitted) < 8:
        return None
    return "/".join(splitted[6:8])
