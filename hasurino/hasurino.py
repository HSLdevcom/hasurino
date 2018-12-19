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

    poster_thread = threading.Thread(
        target=graphqlposter.create_graphql_poster(
            config=config["graphql"], queue=graphql_queue
        ),
        name="Thread-poster",
    )
    processor_thread = threading.Thread(
        target=processor.create_processor(
            config=config["processor"],
            in_queue=hfp_queue,
            out_queue=graphql_queue,
        ),
        name="Thread-processor",
    )
    subscriber = mqttsubscriber.create_mqtt_subscriber(
        config=config["mqtt"], queue=hfp_queue
    )

    try:
        logger.info("Starting GraphQL poster thread")
        poster_thread.start()
        logger.info("Starting processor thread")
        processor_thread.start()
        logger.info("Starting MQTT subscriber")
        subscriber.loop_start()
    except RuntimeError as err:
        logger.error("Fatal failure: %s", str(err))
        logger.info("Stopping MQTT subscriber")
        subscriber.loop_stop()
        logger.info("Stopping processor")
        hfp_queue.put(poisonpill.POISON_PILL)
        processor_thread.join()
        logger.info("Stopping GraphQL poster")
        graphql_queue.put(poisonpill.POISON_PILL)
        poster_thread.join()


if __name__ == "__main__":
    main()
