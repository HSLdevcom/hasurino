# -*- coding: utf-8 -*-
"""Process HFP MQTT messages into GraphQL mutations."""

import logging

from hasurino import bundler
from hasurino import duplicatechecker
from hasurino import parser
from hasurino import poisonpill
from hasurino import serializer


LOG = logging.getLogger(__name__)


def create_processor(config, in_queue, out_queue, err_queue):
    """Create a processor."""

    is_duplicate = duplicatechecker.create_duplicate_checker(config)
    parse = parser.create_parser(config)
    bundle = bundler.create_bundler(config)
    serialize = serializer.create_serializer(config)

    def keep_processing():
        try:
            LOG.info("Processor started")
            while True:
                try:
                    if in_queue.full():
                        LOG.warning(
                            "Currently hasurino might not be able to handle the MQTT volume as in_queue is full"
                        )
                    message = in_queue.get(block=True, timeout=None)
                    if message is poisonpill.POISON_PILL:
                        LOG.info("Processor is shutting down")
                        break
                    if not is_duplicate(message):
                        parsed = parse(message)
                        bundled = bundle(parsed)
                        if bundled is not None:
                            serialized = serialize(bundled)
                            out_queue.put(serialized, block=True, timeout=None)
                except ValueError as err:
                    LOG.warning("Processing error: %s", str(err))
        except Exception as err:
            err_queue.put(err, block=True, timeout=None)

    return keep_processing
