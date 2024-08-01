#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Copyright 2023-2024 Allen Dema
from __future__ import annotations

import os
import json
from pathlib import Path
from datetime import datetime

from utils import save_to_json, save_to_jsonl, append_to_file
from postprocessor.common import PostProcessor

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_NAME = os.path.basename(os.path.dirname(PROJECT_DIR))
PROJECT_ROOT = os.path.dirname(os.path.dirname(PROJECT_DIR))

OUT_DIR = PROJECT_ROOT + "/data/"


class JsonPP(PostProcessor):
    def __init__(self, md_list, options):
        PostProcessor.__init__(self, md_list, options)
        self.log.warning("USE metadata.MetadataPP!")

    @staticmethod
    def to_json(md: dict = None, file_name: str = None):
        """save passed 'MD' to a json 'file_name'"""

        if not file_name:
            todays_date = datetime.today().strftime("%Y-%m-%d")

            file_name = f"{PROJECT_NAME}-jsonpp-{todays_date}.json"

        out_file = Path(OUT_DIR) / file_name

        save_to_json(md, out_file)

    @staticmethod
    def to_jsonl(md: dict = None, file_name: str = None):
        """append passed 'MD' to a jsonl 'file_name'"""

        if not file_name:
            todays_date = datetime.today().strftime("%Y-%m-%d")

            file_name = f"{PROJECT_NAME}-jsonlpp-{todays_date}.jsonl"

        out_file = Path(OUT_DIR) / file_name

        save_to_jsonl(md, out_file)


class AppendPP(PostProcessor):
    def __init__(self, md_list, options):
        PostProcessor.__init__(self, md_list, options)

    @staticmethod
    def append(md: dict = None, file_name: str = None, keys: list = ["description"]):
        """append passed MD to a file"""

        if not file_name:
            todays_date = datetime.today().strftime("%Y-%m-%d")

            file_name = f"{PROJECT_NAME}-appendpp-{todays_date}.txt"

        out_file = Path(OUT_DIR) / file_name

        append_to_file(md, out_file)
