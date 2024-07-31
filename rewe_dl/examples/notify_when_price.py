#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Copyright 2023-2024 Allen Dema
from __future__ import annotations

import os
import sys
import logging
import operator
from typing import Iterator

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(PROJECT_DIR))

from rewe import Cli
from postprocessor.notify import NotifyPP

log = logging.getLogger(__name__)


def compare(my_basket: Iterator = [], type: str = None, limit_price: float = 2.3) -> None:
    """Notify using 'apprise' when the price of products in 'my_basket'
    is below /above 'limit_price'"""

    if type.lower() not in ("above", "below"):
        return

    product_mds = Cli().from_links(my_basket)

    for product_md in product_mds:
        current_price = product_md.get("price", float())

        if type.lower() == "below":
            op = operator.lt
        elif type.lower() == "above":
            op = operator.gt

        if op(current_price, limit_price):
            NotifyPP.apprise(
                title=product_md.get("product"),
                body=f"Price {type} {limit_price} euro: {current_price}",
            )

            """
            NotifyPP(product_md, {}).matrix(
                url=product_md.get("link"),
                title=product_md.get("product"),
                body=f"Price {type} {limit_price} euro: {current_price}"
            )
            """


def main():
    my_basket_cookies = [
        "https://www.rewe.de/produkte/schaer-choco-chip-cookies-glutenfrei-200g/1344325",
        "https://www.rewe.de/produkte/schaer-haferkeks-avena-glutenfrei-130g/2731396",
    ]

    hikes_watchlist = [
        "https://www.rewe.de/produkte/durstloescher-multivitamin-0-5l/8831846",
        "https://www.rewe.de/produkte/durstloescher-eistee-pfirsich-geschmack-0-5l/951490",
    ]

    compare(my_basket_cookies, type="below", limit_price=2.3)
    compare(hikes_watchlist, type="above", limit_price=0.65)


if __name__ == "__main__":
    main()
