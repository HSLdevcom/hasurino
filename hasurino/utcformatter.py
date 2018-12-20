# -*- coding: utf-8 -*-
"""UTC timestamps for logging."""

import logging
import time


class UTCFormatter(logging.Formatter):
    """Use UTC time instead of local time."""

    converter = time.gmtime
