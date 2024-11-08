#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Copyright 2023-2024 Allen Dema
from __future__ import annotations

import os
import sys
from pathlib import Path

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(PROJECT_DIR))

from rewe import STORE
from parser import Parser
from postprocessor.sql import SqlPP


def main():
    search_results = STORE().get_new_products()

    all_products = Parser().parse_search_results_products(search_results)

    this_file = Path(__file__).stem

    SqlPP.save_to_sql(all_products, file_name=f"{this_file}.sqlite3")


if __name__ == "__main__":
    main()
