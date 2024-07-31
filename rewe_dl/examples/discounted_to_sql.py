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
from postprocessor.sql import SqlPP

log = logging.getLogger(__name__)


def main():
    discounted_products = STORE().get_discounted_products()

    all_products = Parser().parse_search_results_products(discounted_products)

    this_file = Path(__file__).stem
    todays_date = datetime.today().strftime("%Y-%m-%d")

    file_name = f"{this_file}-{todays_date}.sqlite3"

    SqlPP.save_to_sql(all_products, file_name)


if __name__ == "__main__":
    main()
