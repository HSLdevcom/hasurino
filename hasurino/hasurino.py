#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""hasurino

hasurino forwards HFP MQTT messages into transitlog GraphQL API.

Usage:
  hasurino <config_path>
  hasurino (-h | --help)

Options:
  -h --help             Show this screen.
"""

import logging
import logging.config
import queue
import threading

import docopt
import yaml

from hasurino import graphqlposter
from hasurino import mqttsubscriber
from hasurino import poisonpill
from hasurino import processor


def main():
    """Main function."""
    arguments = docopt.docopt(__doc__)
    config_path = arguments["<config_path>"]
    config = read_config(config_path)

    logging.config.dictConfig(config["logging"])
    logger = logging.getLogger(__name__)
    logger.info("hasurino started")

    run(config, logger)


def read_config(config_path):
    """Read the config file."""
    with open(config_path, "rt", encoding="utf-8") as handle:
        return yaml.load(handle)


def run(config, logger):
    """Run the top-level functionality."""
    hfp_queue = queue.Queue(maxsize=config["queue_size"])
    graphql_queue = queue.Queue(maxsize=1)
    err_queue = queue.Queue(maxsize=2)

    poster_thread = threading.Thread(
        target=graphqlposter.create_graphql_poster(
            config=config["graphql"],
            payload_queue=graphql_queue,
            err_queue=err_queue,
        ),
        name="Thread-poster",
        daemon=True,
    )
    processor_thread = threading.Thread(
        target=processor.create_processor(
            config=config["processor"],
            in_queue=hfp_queue,
            out_queue=graphql_queue,
            err_queue=err_queue,
        ),
        name="Thread-processor",
        daemon=True,
    )
    subscriber = mqttsubscriber.create_mqtt_subscriber(
        config=config["mqtt"], queue=hfp_queue
    )

    logger.info("Starting GraphQL poster thread")
    poster_thread.start()
    logger.info("Starting processor thread")
    processor_thread.start()
    logger.info("Starting MQTT subscriber")
    subscriber.loop_start()

    err = err_queue.get(block=True, timeout=None)
    logger.error("Fatal error %s", err)

    logger.info("Stopping MQTT subscriber")
    subscriber.loop_stop()

    logger.info("Stopping processor")
    try:
        hfp_queue.put(
            poisonpill.POISON_PILL,
            block=True,
            timeout=config["poison_pill_timeout_in_seconds"],
        )
    except queue.Full:
        pass
    processor_thread.join(config["thread_join_timeout_in_seconds"])
    if processor_thread.is_alive():
        logger.warning("processor_thread did not terminate before timeout")

    logger.info("Stopping GraphQL poster")
    try:
        graphql_queue.put(
            poisonpill.POISON_PILL,
            block=True,
            timeout=config["poison_pill_timeout_in_seconds"],
        )
    except queue.Full:
        pass
    poster_thread.join(config["thread_join_timeout_in_seconds"])
    if poster_thread.is_alive():
        logger.warning("poster_thread did not terminate before timeout")


if __name__ == "__main__":
    main()
