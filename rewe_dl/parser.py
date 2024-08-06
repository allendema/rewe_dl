#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2023-2024 Allen Dema
from __future__ import annotations

import logging
from typing import Iterator
from dataclasses import asdict

from constants import Product
from formatter import price_cent_to_numeric

log = logging.getLogger(__name__)


class Parser:
    def __init__(self, *args, **kwargs) -> None:
        """Pass '*args' and '**kwargs' to Config class
        so that self.STORE_ID, self.SLEEP_REQUEST etc will be set/re-set
        """
        from rewe import Config

        Config().__init__(*args, **kwargs)

    def __repr__(self):
        return f'Parser(f"{self.BASE_URL!s}, {self.STORE_ID!s}")'

    def calculate_savings(md: dict) -> float:
        """return a float of 'you would save' amount"""

        saved = float(md.get("old_price")) - float(md.get("price"))

        # return float(saved)
        return float(f"{saved:.2f}")

    def parse_website_links(self, found_links: Iterator[str] = None) -> Iterator[Product]:
        """run 'Cli().from_links' with given 'found_links'"""
        from rewe import Cli

        product_links = set()
        for link in found_links:
            if "/p" in link or "produkt" in link:
                product_links.add(link)

        return Cli().from_links(urls=product_links)

    @staticmethod
    def _from_emebedded(data: dict, key: str, default=[]):
        return data.get("_embedded", {}).get(key, default)

    def _get_picture(self, media: dict) -> str:
        picture_url = media.get("images", [])[0].get("_links").get("self", {}).get("href", "")

        return picture_url

    def product_md_from_product(self, product: dict) -> Product:
        """return a dict parsed from e.x 'alternatives' > 'products'"""

        media = product.get("media", {})
        article = product.get("_embedded", {}).get("articles")[0]  # only one article in fact

        listing = article.get("_embedded", {}).get("listing", {})
        pricing = listing.get("pricing", {})

        product_description = product.get("productName", "")
        product_id = product.get("id", "")
        nan = product.get("nan", "")
        brand = product.get("brand", {}).get("name", "")

        old_price = pricing.get("discount", {}).get("regularPrice", 0)
        price = pricing.get("currentRetailPrice", 0)
        picture = self._get_picture(media)

        price = price_cent_to_numeric(price)

        old_price = price_cent_to_numeric(old_price)
        if old_price == 0.0:
            old_price = price

        _product_dict = {}

        _product_dict["store"] = "rewe.de"

        _product_dict["product"] = product_description

        _product_dict["link"] = f"https://rewe.de/produkte/{nan}"

        _product_dict["product_id"] = product_id

        _product_dict["price"] = price
        _product_dict["old_price"] = old_price

        _product_dict["saved"] = Parser.calculate_savings(md=_product_dict)

        _product_dict["brand"] = brand
        _product_dict["picture"] = picture

        return asdict(Product(**_product_dict))

    def parse_product_infos(self, product_infos: list[dict]) -> Iterator[Product]:
        for product in product_infos:
            # fmt: off
            product_description = product.get("productName", "")
            product_id          = product.get("productId", product.get("id", ""))
            nan                 = product.get("nan", "")
            brand               = product.get("brandKey", product.get("manufacturer", {}).get("name", ""))
            old_price           = product.get("pricing", {}).get("regularPrice", 0)
            price               = product.get("pricing", {}).get("price", 0)
            picture             = product.get("mediaInformation", [])[0].get("mediaUrl", "")
            # fmt: on

            price = price_cent_to_numeric(price)

            old_price = price_cent_to_numeric(old_price)
            if old_price == 0.0:
                old_price = price

            _product_dict = {}

            _product_dict["store"] = "rewe.de"

            _product_dict["product"] = product_description

            _product_dict["link"] = f"https://rewe.de/produkte/{nan}"

            _product_dict["product_id"] = product_id

            _product_dict["price"] = price
            _product_dict["old_price"] = old_price

            _product_dict["saved"] = Parser.calculate_savings(md=_product_dict)

            _product_dict["brand"] = brand
            _product_dict["picture"] = picture

            yield asdict(Product(**_product_dict))

    def parse_product_from_offers(self, products: Iterator[dict]) -> Iterator:
        for product in products:
            parsed = self.product_md_from_product(product)

            yield parsed

    def get_search_results_products(self, response: dict) -> list[dict]:
        """returns 'products' key from search result"""
        return Parser._from_emebedded(response, "products")

    def _parse_search_results_products(self, products: Iterator) -> list[dict]:
        """returns product_infos for every product in 'products'"""
        msg = "Use 'parse_search_results_products' to avoid http requests!"
        log.warning(msg)
        # raise DeprecationWarning(msg)

        import STORE

        product_ids = STORE().product_ids(response)

        return STORE().product_infos(product_ids=product_ids)

    def parse_search_results_products(self, search_result: Iterator[dict]):
        """returns 'Product' asdict for every product in 'search_result'"""
        for search_results_page in search_result:
            products = Parser().get_search_results_products(search_results_page)

            parsed = Parser().parse_product_from_offers(products)

            # sort by 'saved' amount - high-to-low
            parsed = sorted(parsed, key=self._sort_by_saved, reverse=True)

            yield from parsed

    def parse_search_category(self, search_result: Iterator[dict]):
        """convinience function for better naming"""
        return self.parse_search_results_products(search_result)

    def _sort_by_key(self, item, key: str):
        return item.get(key, "")

    def _sort_by_saved(self, item):
        return self._sort_by_key(item, key="saved")
