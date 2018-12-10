#!/usr/bin/env python3
"""hasurino

hasurino forwards HFP MQTT messages into transitlog GraphQL API.

Usage:
  hasurino <config_path>
  hasurino (-h | --help)
  hasurino --version

Options:
  -h --help             Show this screen.
  --version             Show version.
"""

from docopt import docopt


def main():
    arguments = docopt(__doc__, version="hasurino 0.0.1")
    config_path = arguments["<config_path>"]
    # FIXME: Create the queue
    # FIXME: Create the forwarder
    # FIXME: Form the MQTT subscription


if __name__ == "__main__":
    main()
