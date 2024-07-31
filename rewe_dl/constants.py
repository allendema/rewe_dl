#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2023-2024 Allen Dema

from __future__ import annotations

import logging
from dataclasses import asdict, dataclass

log = logging.getLogger(__name__)


@dataclass
class Product:
    store: str
    product: str
    link: str
    product_id: str
    price: float
    old_price: float
    saved: float
    brand: str
    picture: str

    # test
    def dict(self):
        return {k: str(v) for k, v in asdict(self).items()}


"""
@dataclass
class CssSelectors:
    TITLES = "button.spr-product-information__title-link"
    ADDIOTIONAL_INFOS = "span.spr-product-information__additional"
    PRICES = "div.spr-product-price__tag-price"
    AVAILIABLES = (
        "div.spr-product-availability__info spr-product-availability__info--available"
    )


def css_selectors() -> dict:
    return {
        # rewe
        "TITLES": "button.spr-product-information__title-link",
        "ADDIOTIONAL_INFOS": "span.spr-product-information__additional",
        "PRICES": "div.spr-product-price__tag-price",
        "AVAILIABLES": "div.spr-product-availability__info spr-product-availability__info--available",
    }
"""
