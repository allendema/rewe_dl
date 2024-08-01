#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations

import os
import re
import sys
import json
import locale
import logging
from random import choice

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(PROJECT_DIR)

import exception

log = logging.getLogger(__name__)


def create_agents() -> dict:
    ua_table = {
        "firefox": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:97.0) Gecko/20100101 Firefox/128.0",
        "brave": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Brave Chrome/83.0.4103.116 Safari/537.36",
        "safari": "Mozilla/5.0 (Macintosh; Intel Mac OS X 12_2_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.2 Safari/605.1.15",
        # "ios": "Mozilla/5.0 (iPhone; CPU iPhone OS 15_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.4 Mobile/15E148 Safari/604.1",
        # "mozilla": "Mozilla/5.0",
    }

    browser_names = [browser for browser in ua_table.keys()]

    rand_browser = choice(browser_names)

    headers = {
        "User-Agent": ua_table.get(rand_browser),
        "Accept-Language": locale.getlocale()[0].replace("_", "-"),
        "DNT": "0",
    }

    return headers


def save_to_json(json_data: dict, file_name: str, indent=4, mode="w") -> None:
    """Save json to file.
    if given path doesn't exist - create it
    """
    # log.info(f"Saving JSON to file: {file_name}")

    new_dir = os.path.dirname(file_name)
    os.makedirs(new_dir, exist_ok=True)

    with open(file_name, mode) as file:
        try:
            if isinstance(json_data, dict):
                json_string = json.dumps(json_data, indent=indent)
                file.write(json_string)
            elif isinstance(json_data, list):
                for item in json_data:
                    json.dump(item, file, indent=indent)
                    file.write("\n")
            else:
                raise ValueError("json_data must be a dict or a list of dicts!")
        except (IOError, OSError) as e:
            log.error(str(e))


def save_to_jsonl(json_data: dict, file_name: str) -> None:
    new_dir = os.path.dirname(file_name)
    os.makedirs(new_dir, exist_ok=True)

    if isinstance(json_data, dict):
        json_string = json.dumps(json_data)

        append_to_file(json_string, file_name)

    elif isinstance(json_data, list):
        for item in json_data:
            json_string = json.dumps(item) + "\n"

            append_to_file(json_string, file_name)

    else:
        raise ValueError("json_data must be a dict or a list of dicts!")


def read_file(file_name: str) -> list:
    with open(file_name) as file:
        data = file.readlines()
        file.close()

    return data


def append_to_file(content, file_name: str) -> None:
    """append to a file,
    if given path doesn't exist - create it
    """

    if not os.path.exists(file_name):
        new_dir = os.path.dirname(file_name)

        os.makedirs(new_dir, exist_ok=True)

    with open(file_name, "a") as fp:
        fp.write(content)

    # log.info(f"Done appending to {file_name}")


def slugify(value):
    """
    Convert a string to a URL slug

    # https://github.com/mikf/gallery-dl/blob/master/gallery_dl/text.py#L42C1-L50C1
    Adapted from:
    https://github.com/django/django/blob/master/django/utils/text.py
    """
    value = re.sub(r"[^\w\s-]", "", str(value).lower())
    return re.sub(r"[-\s]+", "-", value).strip("-_")


@staticmethod
def load_config(config_path: str = None) -> dict:
    if not config_path:
        default = PROJECT_DIR + "/" + "config.json"
        config_path = default

    try:
        with open(config_path, "r", encoding="utf-8") as config_file:
            config_raw = config_file.read()
            return json.loads(config_raw)
    except (Exception, OSError) as error:
        raise exception.InputFileError(f"{error!s}")


@staticmethod
def json_compact(obj) -> dict:
    return json.dumps(obj, separators=(",", ":"), sort_keys=True)
