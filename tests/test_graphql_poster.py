# -*- coding: utf-8 -*-
"""Test posting to the GraphQL API."""

import queue
import logging
import logging.config
import unittest.mock

import requests
import requests_mock

from hasurino import graphqlposter
from hasurino import poisonpill


def test_exit_on_poison_pill():
    out_queue = queue.Queue()
    err_queue = queue.Queue()
    config = {
        "hasura_access_key": "bar",
        "endpoint": "https://foo.com",
        "request_timeout_in_seconds": 3,
        "repost_wait_in_seconds": 1,
    }
    keep_posting = graphqlposter.create_graphql_poster(
        config=config, payload_queue=out_queue, err_queue=err_queue
    )
    with requests_mock.mock() as m:
        m.post(requests_mock.ANY, json={}, status_code=200)

        out_queue.put(poisonpill.POISON_PILL)
        keep_posting()
        assert True

        out_queue.put("foo")
        out_queue.put(poisonpill.POISON_PILL)
        keep_posting()
        assert True


def test_log_warning_on_http_error():
    config = {
        "hasura_access_key": "bar",
        "endpoint": "https://foo.com",
        "request_timeout_in_seconds": 3,
        "repost_wait_in_seconds": 1,
    }
    headers = {
        "X-Hasura-Access-Key": config["hasura_access_key"],
        "Content-Type": "application/json",
    }
    logger = logging.getLogger("hasurino.graphqlposter")
    with unittest.mock.patch.object(logger, "warning") as mock_warning:
        with requests_mock.mock() as m:
            m.post(requests_mock.ANY, json={}, status_code=400)
            graphqlposter.post(
                endpoint=config["endpoint"],
                headers=headers,
                timeout=config["request_timeout_in_seconds"],
                payload="foo",
            )
            mock_warning.assert_called_once()


def test_log_warning_on_timeout():
    config = {
        "hasura_access_key": "bar",
        "endpoint": "https://foo.com",
        "request_timeout_in_seconds": 3,
        "repost_wait_in_seconds": 1,
    }
    headers = {
        "X-Hasura-Access-Key": config["hasura_access_key"],
        "Content-Type": "application/json",
    }
    exc = requests.exceptions.ReadTimeout
    logger = logging.getLogger("hasurino.graphqlposter")
    with unittest.mock.patch.object(logger, "warning") as mock_warning:
        with requests_mock.mock() as m:
            m.post(requests_mock.ANY, exc=exc)
            graphqlposter.post(
                endpoint=config["endpoint"],
                headers=headers,
                timeout=config["request_timeout_in_seconds"],
                payload="foo",
            )
            mock_warning.assert_called_once()


def test_log_warning_on_weird_response():
    config = {
        "hasura_access_key": "bar",
        "endpoint": "https://foo.com",
        "request_timeout_in_seconds": 3,
        "repost_wait_in_seconds": 1,
    }
    headers = {
        "X-Hasura-Access-Key": config["hasura_access_key"],
        "Content-Type": "application/json",
    }
    logger = logging.getLogger("hasurino.graphqlposter")
    with unittest.mock.patch.object(logger, "warning") as mock_warning:
        with requests_mock.mock() as m:
            m.post(requests_mock.ANY, json={}, status_code=200)
            graphqlposter.post(
                endpoint=config["endpoint"],
                headers=headers,
                timeout=config["request_timeout_in_seconds"],
                payload="foo",
            )
            mock_warning.assert_called_once()


def test_log_debug_on_expected_response():
    config = {
        "hasura_access_key": "bar",
        "endpoint": "https://foo.com",
        "request_timeout_in_seconds": 3,
        "repost_wait_in_seconds": 1,
    }
    headers = {
        "X-Hasura-Access-Key": config["hasura_access_key"],
        "Content-Type": "application/json",
    }
    logger = logging.getLogger("hasurino.graphqlposter")
    response = {"data": {"mutation": {"affected_rows": 1}}}
    with unittest.mock.patch.object(logger, "debug") as mock_debug:
        with requests_mock.mock() as m:
            m.post(requests_mock.ANY, json=response, status_code=200)
            graphqlposter.post(
                endpoint=config["endpoint"],
                headers=headers,
                timeout=config["request_timeout_in_seconds"],
                payload="foo",
            )
            mock_debug.assert_called_once()
