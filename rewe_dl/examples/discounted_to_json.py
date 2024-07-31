#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Copyright 2023-2024 Allen Dema
from __future__ import annotations

import os
import sys
import logging
from pathlib import Path
from datetime import datetime

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(PROJECT_DIR))

from rewe import STORE
from parser import Parser
from postprocessor.output import JsonPP

log = logging.getLogger(__name__)


def main():
    my_store = STORE(store_id="8534540")

    discounted = my_store.get_discounted_products()

    product_infos = my_store.product_infos(product_ids=my_store.product_ids(discounted))

    all_products = [product_md for product_md in Parser().parse_product_infos(product_infos)]

    todays_date = datetime.today().strftime("%Y-%m-%d")
    this_file = Path(__file__).stem

    file_name = f"{this_file}-{todays_date}.json"

    JsonPP.savings_to_json(all_products, file_name)


if __name__ == "__main__":
    main()
