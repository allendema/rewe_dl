#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2023-2024 Allen Dema
from __future__ import annotations

import os
import sys
import json
import logging
import tempfile
import unittest

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_NAME = os.path.basename(os.path.dirname(PROJECT_DIR))
PROJECT_ROOT = os.path.dirname(PROJECT_DIR + "/../rewe_dl/")

sys.path.insert(0, os.path.dirname(PROJECT_DIR))

from rewe_dl.utils import read_file
from rewe_dl.postprocessor.notify import NotifyPP
from rewe_dl.postprocessor.output import JsonPP
from rewe_dl.postprocessor.metadata import MetadataPP


class NotifyTest(unittest.TestCase):
    body = "This is product body_example!"
    title = "This is product title"

    # don run NotifyTest by default - add 'test_' prefix to run tests

    def apprise(self):
        self.assertIsNone(NotifyPP.apprise(body=self.body, title=self.title))

    def matrix(self):
        product_md = {"link": "https://example.org", "product": self.title}

        options = {"config": f"{PROJECT_ROOT}/config.json"}

        self.assertIsNone(
            NotifyPP(product_md, options).matrix(
                url=product_md.get("link"),
                title=product_md.get("product"),
                body=self.body,
            )
        )

    def matrix_default_config(self):
        product_md = {"link": "https://example.org", "product": self.title}

        self.assertIsNone(
            NotifyPP(product_md, {}).matrix(
                url=product_md.get("link"),
                title=product_md.get("product"),
                body=self.body,
            )
        )


class MdBaseTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dir = tempfile.TemporaryDirectory()
        _number_json, cls.temp_file_json = tempfile.mkstemp(suffix=".json")
        _number_jsonl, cls.temp_file_jsonl = tempfile.mkstemp(suffix=".jsonl")

    @classmethod
    def tearDownClass(cls):
        cls.dir.cleanup()
        # pass

    def example_products():
        products = []
        _product_dict = {}

        _product_dict["store"] = PROJECT_NAME

        _product_dict["title"] = "This is product title"
        _product_dict["link"] = "https://example.org/777333777/product-link"

        _product_dict["product_id"] = "777333777"

        _product_dict["price"] = "20.0"
        _product_dict["old_price"] = "25.0"

        _product_dict["saved"] = "5.0"

        _product_dict["brand"] = "sOmE bRanD"
        _product_dict["picture"] = "https://example.org/pic.ext"

        products.append(_product_dict)

        return products

    products = example_products()


class MetadataTest(MdBaseTest):
    @classmethod
    def setUpClass(cls):
        cls.dir = tempfile.TemporaryDirectory()
        _number_json, cls.temp_file_json = tempfile.mkstemp(suffix=".json")
        _number_jsonl, cls.temp_file_jsonl = tempfile.mkstemp(suffix=".jsonl")
        _, cls.temp_file_custom_format = tempfile.mkstemp(prefix="custom_format", suffix=".txt")
        __, cls.temp_file_custom_filename = tempfile.mkstemp(prefix="custom_filename", suffix=".json")

    @classmethod
    def tearDownClass(cls):
        # cls.dir.cleanup()
        pass

    def example_products():
        products = []
        _product_dict = {}

        _product_dict["store"] = PROJECT_NAME

        _product_dict["title"] = "This is product title"
        _product_dict["link"] = "https://example.org/777333777/product-link"

        _product_dict["product_id"] = "777333777"

        _product_dict["price"] = "20.0"
        _product_dict["old_price"] = "25.0"

        _product_dict["saved"] = "5.0"

        _product_dict["brand"] = "sOmE bRanD"
        _product_dict["picture"] = "https://example.org/pic.ext"

        products.append(_product_dict)

        return products

    products = example_products()

    def test_metadata_to_json(self):
        options = {
            "filename": self.temp_file_json,
            "directory": os.path.dirname(self.temp_file_json),
            "mode": "json",
        }

        for product_md in self.products:
            MetadataPP(kwdict=product_md, options=options).run()

            with open(self.temp_file_json, "r") as file:
                data = file.read()
                data = json.loads(data)

                self.assertIsNotNone(data)
                self.assertIsInstance(data, dict)

    def test_metadata_to_json_custom_file_name(self):
        options = {
            "filename": self.temp_file_custom_filename,
            "directory": os.path.dirname(self.temp_file_custom_filename),
            "mode": "json",
        }

        for product_md in self.products:
            MetadataPP(kwdict=product_md, options=options).run()

            with open(self.temp_file_custom_filename, "r") as file:
                data = file.read()
                data = json.loads(data)

                self.assertIsNotNone(data)
                self.assertIsInstance(data, dict)

    def test_metadata_to_jsonl(self):
        options = {
            "filename": self.temp_file_jsonl,
            "directory": os.path.dirname(self.temp_file_jsonl),
            "mode": "jsonl",
        }

        # create two product_md's for testing jsonl
        for product_md in self.products + self.products:
            MetadataPP(kwdict=product_md, options=options).run()

            with open(self.temp_file_jsonl, "r") as file:
                lines = file.readlines()

                for line in lines:
                    data = json.loads(line)

                    self.assertIsNotNone(data)
                    self.assertIsInstance(data, dict)

    def test_metadata_to_custom_format(self):
        options = {
            "filename": self.temp_file_custom_format,
            "directory": os.path.dirname(self.temp_file_custom_format),
            "mode": "custom",
            "content-format": "Price for Product {title} is: {price}\n",
        }

        for product_md in self.products:
            MetadataPP(kwdict=product_md, options=options).run()

            with open(self.temp_file_custom_format, "r") as file:
                data = file.read()
                self.assertIn(product_md.get("title"), data)
                self.assertIn(product_md.get("price"), data)

    def test_metadata_no_dir(self):
        options = {"filename": "/tmp/no_standalone_dir_passed.json", "mode": "json"}

        for product_md in self.products:
            MetadataPP(kwdict=product_md, options=options).run()

            with open(options.get("filename"), "r") as file:
                data = file.read()
                data = json.loads(data)

                self.assertIsNotNone(data)
                self.assertIsInstance(data, dict)


class OutputTest(MdBaseTest):
    def test_to_json(self):
        self.assertIsNone(JsonPP.to_json(self.products, self.temp_file_json))

        with open(self.temp_file_json, "r") as file:
            out = json.load(file)
            self.assertIsInstance(out, dict)

    def test_to_jsonl(self):
        # create two product_md dicts
        self.assertIsNone(JsonPP.to_jsonl(self.products, self.temp_file_jsonl))
        self.assertIsNone(JsonPP.to_jsonl(self.products, self.temp_file_jsonl))

        out = read_file(self.temp_file_jsonl)

        for line in out:
            self.assertIsNotNone(line)

            product_md = json.loads(line)

            self.assertIsInstance(product_md, dict)
            self.assertIsNotNone(product_md)


if __name__ == "__main__":
    unittest.main()
