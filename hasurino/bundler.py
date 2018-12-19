# -*- coding: utf-8 -*-
"""Bundle messages together."""


def create_bundler(config):
    """Create a bundler."""

    max_length = config["max_messages_in_bundle"]
    messages = []

    def bundle(message):
        nonlocal messages
        while True:
            output = None
            messages.append(message)
            if len(messages) >= max_length:
                output = messages
                messages = []
            return output

    return bundle
