# -*- coding: utf-8 -*-
"""Post GraphQL queries into some Hasura endpoint."""

import logging
import time

import requests

from hasurino import poisonpill

LOG = logging.getLogger(__name__)


def create_graphql_poster(config, payload_queue, err_queue):
    """Create a GraphQL poster."""

    headers = {
        "X-Hasura-Access-Key": config["hasura_access_key"],
        "Content-Type": "application/json",
    }

    def keep_posting():
        try:
            LOG.info("GraphQL poster started")
            while True:
                payload = payload_queue.get(block=True, timeout=None)
                if payload is poisonpill.POISON_PILL:
                    LOG.info("GraphQL poster is shutting down")
                    break
                post_until_success(payload)
        except Exception as err:
            err_queue.put(err, block=True, timeout=None)

    def post_until_success(payload):
        while True:
            if post(
                config["endpoint"],
                headers,
                config["request_timeout_in_seconds"],
                payload,
            ):
                break
            time.sleep(config["repost_wait_in_seconds"])

    return keep_posting


def post(endpoint, headers, timeout, payload):
    """Post once."""
    is_success = False
    response = None
    try:
        response = requests.post(
            endpoint, data=payload, headers=headers, timeout=timeout
        )
        response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        LOG.warning(
            "POST request failed with HTTP error %s and response content %s",
            str(err),
            str(response.content),
        )
    except requests.exceptions.RequestException as err:
        LOG.warning("POST request failed with exception %s", str(err))
    else:
        is_success = True
        try:
            LOG.debug(
                "GraphQL mutation affected %s rows",
                response.json()["data"].copy().popitem()[1]["affected_rows"],
            )
        except (ValueError, KeyError, AttributeError):
            LOG.warning(
                "Unexpected but successful response for GraphQL mutation: %s",
                str(response.content),
            )
    return is_success
