# -*- coding: utf-8 -*-
"""Test transforming MQTT messages to GraphQL mutations."""

from hasurino import serializer


def test_serialize_object():
    input1 = {
        "received_at": "2018-10-01T10:56:43.422229Z",
        "topic_prefix": "/hfp/",
        "topic_version": "v1",
        "journey_type": "journey",
        "is_ongoing": True,
        "mode": "bus",
        "owner_operator_id": "0012",
        "vehicle_number": "01009",
        "unique_vehicle_id": "0012/01009",
        "route_id": "1037",
        "direction_id": "2",
        "headsign": "Kamppi",
        "journey_start_time": "13:36",
        "next_stop_id": "1320111",
        "geohash_level": "4",
        "topic_latitude": 60.245,
        "topic_longitude": 24.849,
        "desi": "37",
        "dir": "2",
        "oper": 12,
        "veh": 1009,
        "tst": "2018-10-01T10:56:43Z",
        "tsi": 1538391403,
        "spd": 5.12,
        "hdg": 237,
        "lat": 60.245656,
        "long": 24.84937,
        "acc": 0.59,
        "dl": -554,
        "odo": 4052,
        "drst": 0,
        "oday": "2018-10-01",
        "jrn": 220,
        "line": 830,
        "start": "13:36",
    }
    input2 = {
        "received_at": "2018-10-01T10:56:43.422240Z",
        "topic_prefix": "/hfp/",
        "topic_version": "v1",
        "journey_type": "deadrun",
        "is_ongoing": True,
        "mode": "bus",
        "owner_operator_id": "0022",
        "vehicle_number": "00993",
        "unique_vehicle_id": "0022/00993",
        "desi": None,
        "dir": None,
        "oper": None,
        "veh": 993,
        "tst": "2018-10-01T10:54:32Z",
        "tsi": 1538391272,
        "spd": 0.0,
        "hdg": 165,
        "lat": 60.177769,
        "long": 24.799109,
        "acc": 0.0,
        "dl": 0,
        "odo": 16060,
        "drst": 1,
        "oday": None,
        "jrn": None,
        "line": None,
        "start": None,
    }

    result1 = '{received_at:"2018-10-01T10:56:43.422229Z",topic_prefix:"/hfp/",topic_version:"v1",journey_type:"journey",is_ongoing:true,mode:"bus",owner_operator_id:"0012",vehicle_number:"01009",unique_vehicle_id:"0012/01009",route_id:"1037",direction_id:"2",headsign:"Kamppi",journey_start_time:"13:36",next_stop_id:"1320111",geohash_level:"4",topic_latitude:60.245,topic_longitude:24.849,desi:"37",dir:"2",oper:12,veh:1009,tst:"2018-10-01T10:56:43Z",tsi:1538391403,spd:5.12,hdg:237,lat:60.245656,long:24.84937,acc:0.59,dl:-554,odo:4052,drst:0,oday:"2018-10-01",jrn:220,line:830,start:"13:36"}'
    result2 = '{received_at:"2018-10-01T10:56:43.422240Z",topic_prefix:"/hfp/",topic_version:"v1",journey_type:"deadrun",is_ongoing:true,mode:"bus",owner_operator_id:"0022",vehicle_number:"00993",unique_vehicle_id:"0022/00993",veh:993,tst:"2018-10-01T10:54:32Z",tsi:1538391272,spd:0.0,hdg:165,lat:60.177769,long:24.799109,acc:0.0,dl:0,odo:16060,drst:1}'

    assert serializer.serialize_object(input1) == result1
    assert serializer.serialize_object(input2) == result2
