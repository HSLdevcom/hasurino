# -*- coding: utf-8 -*-
"""Post GraphQL queries into some Hasura endpoint."""

import logging
import time

import requests

from hasurino import poisonpill

LOG = logging.getLogger(__name__)


def create_graphql_poster(config, queue):
    """Create a GraphQL poster."""

    headers = {
        "X-Hasura-Access-Key": config["hasura-access-key"],
        "Content-Type": "application/json",
    }

    def keep_posting():
        LOG.info("GraphQL poster started")
        while True:
            payload = queue.get(block=True, timeout=None)
            if payload is poisonpill.POISON_PILL:
                LOG.info("GraphQL poster is shutting down")
                break
            post_until_success(payload)

    def post_until_success(payload):
        is_success = False
        while not is_success:
            response = requests.post(
                config["endpoint"], data=payload, headers=headers
            )
            if response.ok:
                is_success = True
                result = response.json()
                if "data" in result and result["data"]:
                    mutation = result["data"].copy().popitem()[1]
                    if "affected_rows" in mutation:
                        LOG.debug(
                            "GraphQL mutation affected %s rows",
                            mutation["affected_rows"],
                        )
                    else:
                        LOG.warning(
                            "Unexpected but successful response for GraphQL mutation: %s",
                            str(response.json()),
                        )
                else:
                    LOG.warning(
                        "Unexpected but successful response for GraphQL mutation: %s",
                        str(response.json()),
                    )
            else:
                LOG.warning("POST request failed: %s", str(response.json()))
                time.sleep(1)

    return keep_posting
