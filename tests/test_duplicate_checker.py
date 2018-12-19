# -*- coding: utf-8 -*-
"""Test checking for duplicate MQTT messages."""

import queue

from hasurino import duplicatechecker


def test_get_unique_vehicle_id():
    topic1 = "/hfp/v1/journey/ongoing/bus/0022/00888/1095/2/Itäkeskus(M)/13:42/1471155/5/60;25/20/37/61"
    topic2 = "/hfp/v1/deadrun/ongoing/bus/0017/00039"
    topic3 = "/hfp/v1/journey/ongoing/bus/0022/01001/2136/1/Tuomarila/13:39/2314212/0////"
    topic4 = "/foo/bar/baz/xyzzy/alpha/omega"

    result1 = "0022/00888"
    result2 = "0017/00039"
    result3 = "0022/01001"
    result4 = None

    assert duplicatechecker.get_unique_vehicle_id(topic1) == result1
    assert duplicatechecker.get_unique_vehicle_id(topic2) == result2
    assert duplicatechecker.get_unique_vehicle_id(topic3) == result3
    assert duplicatechecker.get_unique_vehicle_id(topic4) == result4


def test_duplicate_checker():
    config = {"max_cache_length_per_vehicle": 60 * 30}
    is_duplicate = duplicatechecker.create_duplicate_checker(config)

    timed_messages = [
        (
            "2018-10-01T10:56:43.422229Z",
            "/hfp/v1/journey/ongoing/bus/0012/01009/1037/2/Kamppi/13:36/1320111/4/60;24/28/44/59",
            '{"VP":{"desi":"37","dir":"2","oper":12,"veh":1009,"tst":"2018-10-01T10:56:43Z","tsi":1538391403,"spd":5.12,"hdg":237,"lat":60.245656,"long":24.849370,"acc":0.59,"dl":-554,"odo":4052,"drst":0,"oday":"2018-10-01","jrn":220,"line":830,"start":"13:36"}}',
        ),
        (
            "2018-10-01T10:56:43.422240Z",
            "/hfp/v1/deadrun/ongoing/bus/0022/00993",
            '{"VP":{"desi":null,"dir":null,"oper":null,"veh":993,"tst":"2018-10-01T10:54:32Z","tsi":1538391272,"spd":0.00,"hdg":165,"lat":60.177769,"long":24.799109,"acc":0.00,"dl":0,"odo":16060,"drst":1,"oday":null,"jrn":null,"line":null,"start":null}}',
        ),
        (
            "2018-10-01T10:56:43.422250Z",
            "/hfp/v1/deadrun/ongoing/bus/0022/00993",
            '{"VP":{"desi":null,"dir":null,"oper":null,"veh":993,"tst":"2018-10-01T10:54:33Z","tsi":1538391273,"spd":0.00,"hdg":165,"lat":60.177769,"long":24.799109,"acc":0.00,"dl":0,"odo":16060,"drst":1,"oday":null,"jrn":null,"line":null,"start":null}}',
        ),
        (
            "2018-10-01T10:56:43.422263Z",
            "/hfp/v1/deadrun/ongoing/bus/0022/00993",
            '{"VP":{"desi":null,"dir":null,"oper":null,"veh":993,"tst":"2018-10-01T10:54:34Z","tsi":1538391274,"spd":0.00,"hdg":165,"lat":60.177769,"long":24.799109,"acc":0.00,"dl":0,"odo":16060,"drst":1,"oday":null,"jrn":null,"line":null,"start":null}}',
        ),
        (
            "2018-10-01T10:56:43.422274Z",
            "/hfp/v1/deadrun/ongoing/bus/0022/00993",
            '{"VP":{"desi":null,"dir":null,"oper":null,"veh":993,"tst":"2018-10-01T10:54:34Z","tsi":1538391274,"spd":0.00,"hdg":165,"lat":60.177769,"long":24.799109,"acc":0.00,"dl":0,"odo":16060,"drst":1,"oday":null,"jrn":null,"line":null,"start":null}}',
        ),
        (
            "2018-10-01T10:56:43.422285Z",
            "/hfp/v1/journey/ongoing/bus/0012/00729/1017/2/Kallio/14:12/1204105/5/60;24/19/53/41",
            '{"VP":{"desi":"17","dir":"2","oper":12,"veh":729,"tst":"2018-10-01T10:56:43Z","tsi":1538391403,"spd":0.00,"hdg":337,"lat":60.154847,"long":24.931211,"acc":0.00,"dl":960,"odo":16,"drst":1,"oday":"2018-10-01","jrn":104,"line":46,"start":"14:12"}}',
        ),
    ]

    results = [False, False, False, False, True, False]

    for (timed_message, result) in zip(timed_messages, results):
        assert is_duplicate(timed_message) == result
