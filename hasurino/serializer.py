# -*- coding: utf-8 -*-
"""Serialize dicts into GraphQL mutations of an implicit schema."""

import json
import logging


LOG = logging.getLogger(__name__)


def create_serializer(config):
    """Create a serializer."""

    del config

    mutation_prefix = "mutation{insert_vehicles(objects:["
    mutation_suffix = "]){affected_rows}}"

    def serialize(row_list):
        middle = ",".join((serialize_object(row) for row in row_list))
        body = json.dumps(
            {"query": mutation_prefix + middle + mutation_suffix}
        ).encode(encoding="utf-8", errors="strict")
        return body

    return serialize


def serialize_object(obj):
    """Serialize a dict into GraphQL arguments."""
    prefix = "{"
    suffix = "}"
    try:
        middle = ",".join(
            (
                key + ":" + stringify(value)
                for key, value in obj.items()
                if value is not None
            )
        )
        return prefix + middle + suffix
    except ValueError as err:
        LOG.warning(
            "Unknown primitive type in dict %s causes error: %s",
            str(obj),
            str(err),
        )
        # Effectively remove this message.
        return ""


def stringify(value):
    """Create a representation of a GraphQL value out of a Python value."""
    if value is True:
        return "true"
    if value is False:
        return "false"
    type_ = type(value)
    if type_ is int or type_ is float:
        return str(value)
    if type_ is str:
        return '"{}"'.format(value)
    raise ValueError(
        "Unknown primitive type {} for value {}".format(type_, value)
    )
