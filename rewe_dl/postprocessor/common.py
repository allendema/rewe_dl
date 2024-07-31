# -*- coding: utf-8 -*-

# Copyright 2023-2024 Allen Dema

"""Common classes and constants used by postprocessor modules."""

from __future__ import annotations

import os
import sys
import logging

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(PROJECT_DIR))

from utils import load_config

log = logging.getLogger(__name__)


class PostProcessor:
    """Base class for postprocessors"""

    def __init__(self, options={}):
        self.name = self.__class__.__name__[:-2].lower()
        self.log = logging.getLogger("postprocessor." + self.name)

        self.options = options
        if options.get("config"):
            self.config = load_config(options.get("config"))
        else:
            self.config = load_config()

    def __repr__(self):
        return self.__class__.__name__
