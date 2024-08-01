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
PROJECT_ROOT = os.path.dirname(PROJECT_DIR)
DATA_FOLDER = os.path.join(os.path.dirname(PROJECT_ROOT), "data")

sys.path.append(PROJECT_ROOT)

from rewe import STORE
from parser import Parser
from postprocessor.metadata import MetadataPP

log = logging.getLogger(__name__)


def main():
    my_store = STORE(store_id="8534540")
    query = "ja"

    todays_date = datetime.today().strftime("%Y-%m-%d")
    this_file = Path(__file__).stem

    paginated = list(my_store.search(query, max_page=1))

    for page, response in enumerate(paginated, 1):
        options = {
            "directory": DATA_FOLDER,
            "filename": f"{this_file}-{query}-{page:02}-{todays_date}.json",
            "mode": "json",
            "ident": 4,
        }

        MetadataPP(response, options=options).run()


if __name__ == "__main__":
    main()
