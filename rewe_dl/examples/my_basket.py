#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Copyright Allen Dema
from __future__ import annotations

import os
import sys
import logging

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(PROJECT_DIR))

log = logging.getLogger(__name__)

from rewe import Cli
from postprocessor.sql import SqlPP


def main():
    MY_STORE_ID: str = "8534540"
    # MY_STORE_ID: str = "8888888"

    my_basket = [
        "https://www.rewe.de/produkte/oro-di-parma-tomatenmark-mit-paprika-scharf-200g/265601",
        "https://www.rewe.de/produkte/tuc-cracker-original-100g/215147",
        "https://www.rewe.de/produkte/kerrygold-cheddar-scheiben-herzhaft-150g/2602784",
        "https://www.rewe.de/produkte/gouda-jung-80g/2621809",
        "https://www.rewe.de/produkte/maretti-bruschette-chips-tomato-olives-und-oregano-150g/2632965",
        "https://www.rewe.de/produkte/rauch-eistee-pfirsisch-0-5l/1091511",
        "https://www.rewe.de/produkte/schaer-choco-chip-cookies-glutenfrei-200g/1344325",
        "https://www.rewe.de/produkte/bauer-joghurt-vanille-250g/2559285",
        "https://www.rewe.de/produkte/baerenmarke-eiskaffee-cappuccino-1l/8008368",
    ]

    offers = Cli(store_id=MY_STORE_ID).from_links(my_basket)

    SqlPP.save_to_sql(offers, file_name="my_basket.sqlite3")


if __name__ == "__main__":
    main()
