#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import os
import sys
import logging
import unittest
from time import sleep

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(PROJECT_DIR))

from rewe_dl import formatter

from test_rewe import CustomTestCase

log = logging.getLogger(__name__)


class TesFormatter(CustomTestCase):
    def test_price_cent_to_numeric(self):
        # euros in cent passed as 'int' to return 'float'

        prices_from_site = [99, 125, 299, 25, 1025, 100025]
        expected = [0.99, 1.25, 2.99, 0.25, 10.25, 1000.25]
        outs = []

        for raw_price in prices_from_site:
            outs.append(formatter.price_cent_to_numeric(raw_price))

        self.assertEqual(expected, outs)


if __name__ == "__main__":
    unittest.main()
