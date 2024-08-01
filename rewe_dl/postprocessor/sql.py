#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Copyright 2023-2024 Allen Dema
from __future__ import annotations

import os
import logging
import sqlite3
from pathlib import Path
from datetime import datetime

from postprocessor.common import PostProcessor

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_NAME = os.path.basename(os.path.dirname(PROJECT_DIR))
PROJECT_ROOT = os.path.dirname(os.path.dirname(PROJECT_DIR))

OUT_DIR = PROJECT_ROOT + "/data/"

log = logging.getLogger(__name__)


class SqlPP(PostProcessor):
    def __init__(self, md_list, options):
        """ Do not use this for very important stuff """
        PostProcessor.__init__(self, md_list)

    @staticmethod
    def sql_insert(databank_file: str, md_list: list):
        # log.debug(f"sqlite3 Metadata: {sqlite3.version}, {sqlite3.sqlite_version}")

        connector = sqlite3.connect(databank_file, timeout=10, check_same_thread=False)
        cursor = connector.cursor()

        sql_query = """
        CREATE TABLE IF NOT EXISTS deals  (
        store TEXT,
        product TEXT,
        link TEXT,
        product_id TEXT,
        price REAL,
        old_price REAL,
        saved REAL,
        brand TEXT,
        picture TEXT,
        date TEXT,
        PRIMARY KEY ("product_id", "date")
        )
        WITHOUT ROWID;
        """

        cursor.execute(sql_query)

        time = datetime.today().strftime("%Y-%m-%d %H:%M:%S")

        replaced_fields = False
        for product in md_list:
            #
            product["time"] = time
            #
            values = list(product.values())

            try:
                cursor.execute(
                    "INSERT INTO deals VALUES ({0})".format(", ".join("?" for _ in product.keys())),
                    (values),
                )

            except Exception:
                # log.info(e)
                replaced_fields = True
                cursor.execute(
                    "INSERT or REPLACE INTO deals VALUES ({0})".format(
                        ", ".join("?" for _ in product.keys())
                    ),
                    (values),
                )

        connector.commit()
        connector.close()
        log.info(f"Replaced fields: {replaced_fields}")

    def save_to_sql(md: list = [], file_name: str = None):
        if not file_name:
            todays_date = datetime.today().strftime("%Y-%m-%d")

            file_name = f"{PROJECT_NAME}-{todays_date}.sqlite3"

        os.makedirs(OUT_DIR, exist_ok=True)
        out_file = Path(OUT_DIR) / file_name

        SqlPP.sql_insert(out_file, md)
