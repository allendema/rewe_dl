#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2023-2024 Allen Dema
from __future__ import annotations

import os
import sys
import types
import inspect
import logging
import unittest
from time import sleep
from dataclasses import asdict

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(PROJECT_DIR)

sys.path.insert(0, PROJECT_ROOT)

from rewe_dl import exception
from rewe_dl.rewe import STORE, Cli, Config
from rewe_dl.constants import Product

log = logging.getLogger(__name__)


class CustomTestCase(unittest.TestCase):
    store_id = "8534540"
    product_url = "https://www.rewe.de/produkte/gouda-jung-80g/2621809"
    store = STORE()
    my_search = store.search(search_term="ja")

    def ensure_is_str(self, result):
        self.assertIsInstance(result, str)

        self.assertNotIsInstance(result, (dict, list, tuple, types.GeneratorType))

        self.assertFalse(inspect.isgeneratorfunction(result))

    def ensure_is_dict(self, result):
        self.assertIsInstance(result, dict)

        self.assertNotIsInstance(result, (str, list, tuple, types.GeneratorType))

        self.assertFalse(inspect.isgeneratorfunction(result))

        self.assertNotEqual(type(result), isinstance(result, types.GeneratorType))

    def ensure_is_list(self, result):
        self.assertIsInstance(result, list)

        self.assertNotIsInstance(result, (str, dict, tuple))

    def ensure_is_generator(self, result):
        self.assertIsInstance(result, types.GeneratorType)

        self.assertNotIsInstance(result, (str, dict, tuple, list))

    def ensure_is_paginated(self, paginated):
        self.ensure_is_generator(paginated)

        for result in paginated:
            self.ensure_is_dict(result)

    def ensure_is_product_md_dc(self, product_md):
        self.ensure_is_dict(product_md)

        dict_from_dc = asdict(Product(**product_md))
        self.assertDictEqual(product_md, dict_from_dc)


class TestSTORE(CustomTestCase):
    def test_product_infos(self):
        result = self.store.product_infos(product_ids=["2621809"])

        self.ensure_is_list(result)
        for product_json in result[:2:]:
            self.ensure_is_dict(product_json)

    def test__yield_from_key(self):
        result = self.store._yield_from_key(self.my_search, key="toggles")
        self.ensure_is_generator(result)

    def test__get_alternatives(self):
        result = self.store._get_alternatives(self.my_search)

        self.ensure_is_generator(result)
        for alt in result:
            self.ensure_is_dict(alt)

    def test_paginate_bad_arguments(self):
        url = self.product_url
        params = {"page": 1}

        # bad url
        result = self.store.paginate("file://https://example.org", params)
        with self.assertRaises((ValueError)):
            # because 'result' is a generator
            for res in result:
                pass

        # bad method
        result = self.store.paginate(url, params=params, method="aaaa")
        with self.assertRaises((AttributeError)):
            for res in result:
                pass

        # bad params
        result = self.store.paginate(url, params=None, method="get")
        with self.assertRaises((AttributeError)):
            for res in result:
                pass

    def test_search(self):
        paginated = self.store.search(search_term="ja")

        self.ensure_is_generator(paginated)

        for result in paginated:
            self.ensure_is_dict(result)

            self.assertIn(
                result.get("type").lower(),
                ("search_result", "corrected_term"),
            )

    def test_search_max_page(self):
        paginated = self.store.search(search_term="ja", max_page=2)

        self.ensure_is_generator(paginated)

        for result in paginated:
            self.ensure_is_dict(result)

            self.assertEqual(result.get("type").lower(), "search_result")

    def test_search_error(self):
        paginated = self.store.search(search_term="pericombobulation", max_page=2)

        self.ensure_is_generator(paginated)

        for result in paginated:
            self.ensure_is_dict(result)
            self.assertEqual(result.get("type").lower(), "no_hit")

    def test_search_category(self):
        paginated = self.store.search_category(category_slug="ace-saft")

        self.ensure_is_generator(paginated)

        for result in paginated:
            self.ensure_is_dict(result)
            self.assertTrue(result.get("type").lower(), "search_result")

    def test_categories(self):
        result = self.store.categories(self.my_search)
        self.ensure_is_list(result)

        for md in result[:2:]:
            self.ensure_is_dict(md)

    def test_subcategory_names(self):
        result = self.store.category_names(self.my_search)

        self.ensure_is_list(result)

    def test_product_ids(self):
        result = self.store.product_ids(self.my_search)
        self.ensure_is_generator(result)

        for idx, product_id in result:
            if product_id is None or product_id == "":
                msg = "Make sure the cookies are copied from the browser"
                log.error(msg)

    def test_product_urls(self):
        result = self.store.product_urls([self.my_search])

        self.ensure_is_generator(result)

        for product_url in result:
            self.ensure_is_str(product_url)
            self.assertTrue(product_url.startswith("https://"))
            self.assertNotIn("generator", product_url)

    def test_products_by_attribute(self):
        paginated = self.store.products_by_attribute()

        self.ensure_is_generator(paginated)

        for result in paginated:
            self.ensure_is_dict(result)

            self.assertTrue(result.get("type").lower() == "search_result")

    def test_get_new_products(self):
        paginated = self.store.get_new_products()

        self.ensure_is_paginated(paginated)

    def test_get_discounted_products(self):
        paginated = self.store.get_discounted_products()

        self.ensure_is_paginated(paginated)

        for product_md in paginated:
            self.ensure_is_product_md_dc(product_md)

    def test_get_vegetarian_products(self):
        paginated = self.store.get_vegetarian_products()

        self.ensure_is_paginated(paginated)

    def test_get_lactosefree_products(self):
        paginated = self.store.get_lactosefree_products()

        self.ensure_is_paginated(paginated)

    def test_get_glutenfree_products(self):
        paginated = self.store.get_glutenfree_products()

        self.ensure_is_paginated(paginated)

    def test_search_brand(self):
        paginated = self.store.search_brand(brand_name="REWE Bio")

        for result in paginated:
            self.ensure_is_dict(result)

            self.assertIn(result.get("type").lower(), ("search_result", "no_hit", "corrected_term"))

    def test_search_brand_no_hit(self):
        paginated = self.store.search_brand(brand_name="BranDdOesNoteXiSt")

        for result in paginated:
            self.ensure_is_dict(result)

            self.assertEqual(result.get("type").lower(), "no_hit")

    def test_recommendations(self):
        product_ids = ["3231481"]  # actually returns lsitingsIds
        result = self.store.recommendations(product_ids)
        self.ensure_is_dict(result)

        self.assertIn("listingIds", result.keys())
        self.ensure_is_list(result.get("listingIds"))

    def test_suggestions(self):
        result = self.store.suggestions("milch")

        self.ensure_is_dict(result)

    def test_get_listings_ids_from_suggestions(self):
        suggestions = self.store.suggestions("milch")
        result = self.store.get_listings_ids(suggestions=suggestions)

        self.ensure_is_list(result)

    def test_get_listings_ids_from_search(self):
        result = self.store.get_listings_ids(search_result=self.my_search)

        self.ensure_is_list(result)

    def test_get_listings_ids_from_recommandations(self):
        recommendations = self.store.recommendations(["3231481"])

        result = self.store.get_listings_ids(recommendations=recommendations)

        self.ensure_is_list(result)

    def test_get_listings_ids_empty(self):
        result = self.store.get_listings_ids()

        self.ensure_is_list(result)
        self.assertEqual(result, [])


class TestConfig(CustomTestCase):
    def test_from_file(self):
        NotImplemented

    def test_user_data_from_web(self):
        with self.assertRaises((NotImplementedError)):
            result = Config(store_id="1940440").user_data_from_web()

    def test_from_web(self):
        result = Config(store_id="1940440").from_web()
        self.ensure_is_dict(result)

    def test_from_web_bad_zipcode(self):
        with self.assertRaises((ValueError)):
            result = Config(store_id="1940440").from_web(zipcode="000000")
            self.assertNotIn("marketsCookie", result)


class TestCli(CustomTestCase):
    def test_id_from_url(self):
        product_id = Cli.id_from_url(self.product_url)

        self.assertIsInstance(product_id, str)
        self.assertEqual(product_id, "2621809")

        # with 'p' prefix
        product_id = Cli.id_from_url("https://www.rewe.de/produkte/gouda-jung-80g/p2621809")

        self.assertIsInstance(product_id, str)
        self.assertEqual(product_id, "2621809")

    def test_id_from_url_category_slug(self):
        category_slug = Cli.id_from_url("https://www.rewe.de/c/kochen-backen")

        self.assertIsInstance(category_slug, str)
        self.assertEqual(category_slug, "kochen-backen")

    def test_id_from_url_bad_url(self):
        product_id = Cli.id_from_url("https://www.rewe.de/produkte/gouda-jung-80g/")

        self.assertEqual(product_id, "")

    def test_from_links(self):
        product_mds = Cli().from_links([self.product_url])

        self.ensure_is_list(product_mds)
        for product_md in product_mds[:2:]:
            self.ensure_is_product_md_dc(product_md)

    def test_from_links_of_categories(self):
        category_link = "https://shop.rewe.de/c/kochen-backen"

        result = Cli().from_links_of_categories(urls=[category_link], max_page=2)

        self.ensure_is_generator(result)

        for product_md in result:
            self.ensure_is_product_md_dc(product_md)


class TestBranch(CustomTestCase):
    """ """


class TestBasket(CustomTestCase):
    """ """


if __name__ == "__main__":
    unittest.main()
