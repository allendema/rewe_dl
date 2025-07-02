#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import re
import os.path


def read(fname):
    path = os.path.join(os.path.dirname(__file__), fname)
    with open(path, encoding="utf-8") as fp:
        return fp.read()


PROJECT_NAME = "rewe_dl"

# get version without importing the package
VERSION = re.search(
    r'__version__\s*=\s*"([^"]+)"',
    read(f"{PROJECT_NAME}/version.py"),
).group(1)


PACKAGES = [
    f"{PROJECT_NAME}",
    f"{PROJECT_NAME}.postprocessor",
    f"{PROJECT_NAME}.examples",
]

DESCRIPTION = (
    "Command-line program to interact with shopping APIs and save"
    "data in several formats such as sqlite3, json, jsonl or custom"
)

LONG_DESCRIPTION = DESCRIPTION


def build_setuptools():
    from setuptools import setup

    setup(
        name=PROJECT_NAME,
        version=VERSION,
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        url="https://github.com/allendema/rewe_dl",
        download_url="https://github.com/allendema/rewe_dl/releases/latest",
        author="Allen Dema",
        author_email="",
        maintainer="Allen Dema",
        maintainer_email="",
        license="",
        python_requires=">=3.8",
        install_requires=[
            "httpx",
        ],
        extras_require={},
        packages=PACKAGES,
        # data_files=FILES,
        test_suite="test",
        keywords="sql price downloader api shopping products inflation tracker",
        classifiers=[
            "Development Status :: 5 - Production/Stable",
            "Environment :: Console",
            "Operating System :: OS Independent",
            "Programming Language :: Python",
            "Programming Language :: Python :: 3",
            "Programming Language :: Python :: 3 :: Only",
            "Programming Language :: Python :: 3.8",
            "Programming Language :: Python :: 3.9",
            "Programming Language :: Python :: 3.10",
            "Programming Language :: Python :: 3.11",
            "Programming Language :: Python :: 3.12",
            "Programming Language :: Python :: Implementation :: CPython",
            "Programming Language :: Python :: Implementation :: PyPy",
            "Topic :: Internet :: WWW/HTTP",
            "Topic :: Multimedia :: Graphics",
            "Topic :: Utilities",
        ],
    )


build_setuptools()
