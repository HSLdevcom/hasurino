# -*- coding: utf-8 -*-
"""Parse HFP messages into dicts."""

import json
import re


def create_parser(config):
    """Create a parser."""

    del config

    topic_version_reo = re.compile(r"(^v\d+|dev)\Z")

    def parse(message):
        received_at, topic, payload = message
        try:
            topic_dict = parse_topic(topic)
            payload_dict = parse_payload(payload)
            parsed = {
                **{"received_at": received_at},
                **topic_dict,
                **payload_dict,
            }
        except ValueError as err:
            raise ValueError(
                "Got ValueError {err} for message received at {received_at} with topic {topic} and payload {payload}".format(
                    err=err,
                    received_at=received_at,
                    topic=topic,
                    payload=payload,
                )
            )
        return parsed

    def parse_topic(topic):
        parts = topic.split("/")
        version_index = get_version_index(parts)
        if version_index is None:
            raise ValueError("No version was found from topic.")
        topic_prefix = "/".join(parts[:version_index]) + "/"
        common_end_index = version_index + 6
        [
            topic_version,
            journey_type,
            temporal_type,
            mode,
            owner_operator_id,
            vehicle_number,
        ] = parts[version_index:common_end_index]
        unique_vehicle_id = owner_operator_id + "/" + vehicle_number
        is_ongoing = False
        if temporal_type == "ongoing":
            is_ongoing = True
        result = {
            "topic_prefix": topic_prefix,
            "topic_version": topic_version,
            "journey_type": journey_type,
            "is_ongoing": is_ongoing,
            "mode": mode,
            "owner_operator_id": owner_operator_id,
            "vehicle_number": vehicle_number,
            "unique_vehicle_id": unique_vehicle_id,
        }
        if len(parts) > common_end_index:
            coordinate_index = common_end_index + 6
            [
                route_id,
                direction_id,
                headsign,
                journey_start_time,
                next_stop_id,
                geohash_level,
            ] = parts[common_end_index:coordinate_index]
            result = {
                **result,
                **{
                    "route_id": route_id,
                    "direction_id": direction_id,
                    "headsign": headsign,
                    "journey_start_time": journey_start_time,
                    "next_stop_id": next_stop_id,
                    "geohash_level": geohash_level,
                },
            }
            # Handle the Fara VPC bug where some messages do not have all
            # the coordinate levels.
            topic_latitude = ""
            topic_longitude = ""
            if len(parts) > coordinate_index:
                [latlong0, latlong1, latlong2, latlong3] = parts[
                    coordinate_index:
                ]
                if latlong0 != "":
                    [lat0, long0] = latlong0.split(";")
                    [lat1, long1] = latlong1
                    [lat2, long2] = latlong2
                    [lat3, long3] = latlong3
                    topic_latitude = lat0 + "." + lat1 + lat2 + lat3
                    topic_longitude = long0 + "." + long1 + long2 + long3
                    result = {
                        **result,
                        **{
                            "topic_latitude": float(topic_latitude),
                            "topic_longitude": float(topic_longitude),
                        },
                    }
        return result

    def get_version_index(parts):
        for i, part in enumerate(parts):
            if topic_version_reo.fullmatch(part):
                return i
        return None

    def parse_payload(payload):
        parsed = json.loads(payload)
        if "VP" not in parsed:
            raise ValueError('Key "VP" is missing from the MQTT payload.')

        # Switch to bool
        vehicle_position = parsed["VP"]
        drst = vehicle_position["drst"]
        if drst is not None:
            vehicle_position["drst"] = drst != 0

        return parsed["VP"]

    return parse
