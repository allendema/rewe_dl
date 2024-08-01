#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations

import os
import sys
import json
import types
import logging
from pathlib import Path

from postprocessor.common import PostProcessor

log = logging.getLogger(__name__)


class MetadataPP(PostProcessor):
    """stripped down and modified from gallery-dl"""

    def __init__(self, kwdict, options):
        self.kwdict = kwdict
        self.options = options
        self.mode = options.get("mode", "json")
        self.content_format = options.get("content-format", options.get("format"))
        self.directory = options.get("directory")
        self.filename = options.get("filename", "metadata")
        self.events = options.get("event", ["file"])
        self.open_mode = options.get("open", "w")
        self.encoding = options.get("encoding", "utf-8")

        self._initialize_formatter()

    def _initialize_formatter(self):
        if self.mode == "custom":
            self.writer = self._write_custom
            self.content_format = self.content_format or ""
        elif self.mode in ["json", "jsonl"]:
            self.writer = self._write_json
            self._json_encode = self._make_encoder().encode
            self.open_mode = "a" if self.mode == "jsonl" else "w"
        else:
            raise ValueError(f"Unsupported mode: {self.mode}")

        if self.directory:
            self.directory = Path(self.directory).resolve().absolute()
            self.directory.mkdir(parents=True, exist_ok=True)

        if self.filename:
            # avoid using '.resolve().absolute()' here - wrong 'join' in '_run()'
            if self.filename and not self.directory:
                self.directory = os.path.dirname(self.filename)
                os.makedirs(self.directory, exist_ok=True)

    def json_default(self, obj):
        if isinstance(obj, types.NoneType):
            return None

        if isinstance(obj, types.GeneratorType):
            return list(obj)

        return str(obj)

    def _make_encoder(self):
        return json.JSONEncoder(
            ensure_ascii=self.options.get("ascii", False),
            sort_keys=self.options.get("sort", False),
            separators=self.options.get("separators"),
            indent=self.options.get("indent"),
            check_circular=False,
            default=self.json_default,
        )

    def _write_custom(self, fp, kwdict):
        fp.write(self.content_format.format(**kwdict))

    def _write_json(self, fp, kwdict):
        fp.write(self._json_encode(kwdict) + "\n")

    def _run(self, kwdict):
        path = Path(self.directory) / self.filename
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, self.open_mode, encoding=self.encoding) as fp:
            self.writer(fp, kwdict)

        log.info(f"Wrote to file: {path}")

    def run(self):
        return self._run(self.kwdict)
