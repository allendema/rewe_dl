#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2023-2024 Allen Dema
from __future__ import annotations

import os
import sys
import logging
import unittest

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(PROJECT_DIR))

from rewe_dl.rewe import STORE
from rewe_dl.parser import Parser

from test_rewe import CustomTestCase

log = logging.getLogger(__name__)


class ParserTest(CustomTestCase):
    def get_products_list_of_dicts(self) -> list:
        products = []
        _product_dict = {}

        _product_dict["store"] = "rewe.de"

        _product_dict["title"] = "product_title"
        _product_dict["link"] = "product_link"

        _product_dict["product_id"] = "product_id"

        _product_dict["price"] = "10.0"
        _product_dict["old_price"] = "15.0"

        _product_dict["saved"] = "5.0"

        products.append(_product_dict)

        return products

    def test_calculate_savings_float(self):
        products = self.get_products_list_of_dicts()
        md = products[0]

        md.update({"old_price": 50.0, "price": 40.0})

        value = 10.0
        out = Parser.calculate_savings(md)

        self.assertIsInstance(value, float)
        self.assertIsInstance(out, float)

        self.assertEqual(value, out)

        bad_value = -10.0
        self.assertNotEqual(bad_value, out)

        bad_value = 20.0

        self.assertNotEqual(bad_value, out)

    def test_get_search_results_products(self):
        for search_results_page in self.my_search:
            self.ensure_is_dict(search_results_page)

            products = Parser().get_search_results_products(search_results_page)
            self.ensure_is_list(products)

            for product_raw_dict in products[2:]:
                self.ensure_is_dict(product_raw_dict)

    def test_parse_search_results_products(self):
        parsed = Parser().parse_search_results_products(self.my_search)
        self.ensure_is_generator(parsed)

        for idx, product_md in enumerate(parsed):
            self.ensure_is_product_md_dc(product_md)

            if idx == 2:
                break

    def test_product_md_from_offer(self):
        """Only if the product is on offer for this store_id.
        Use product id and NOT PRODUCT NAN"""

        search_result_from_discounted = list(STORE().get_discounted_products())[-1]

        discounted_products = Parser._from_emebedded(search_result_from_discounted, "products")

        pseudo_rand_product = discounted_products[:1:][0]

        result = Parser().product_md_from_product(pseudo_rand_product)
        self.ensure_is_dict(result)

    def test_parse_product_from_offers(self):
        """tests '_get_alternatives' and Parser().product_md_from_product
        similiar to test_rewe.test__get_alternatives
        """

        log.info("DEPENDING on search term and store_id no alts will be found!")
        my_search_with_alternatives = STORE().search(search_term="tuc")

        alternatives = STORE()._get_alternatives(my_search_with_alternatives)

        for alt in alternatives:
            products = alt.get("products", [])

            parsed = Parser().parse_product_from_offers(products)
            self.ensure_is_generator(parsed)

            for idx, product_md in enumerate(parsed):
                self.ensure_is_product_md_dc(product_md)

                if idx == 2:
                    break

    def test_parse_product_infos(self):
        """use product id and NOT PRODUCT NAN"""
        product_ids = ["265601", "16325695", "1763154"]

        products = STORE().product_infos(product_ids=product_ids)

        parsed = Parser().parse_product_infos(products)
        self.ensure_is_generator(parsed)

        for product_md in parsed:
            self.ensure_is_product_md_dc(product_md)


if __name__ == "__main__":
    unittest.main()
