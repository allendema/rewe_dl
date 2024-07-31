#!/usr/bin/python3
# -*- coding: utf-8 -*-
from __future__ import annotations


def price_cent_to_numeric(price: int) -> float:
    """
    if isinstance(price, str):
        price = int(price)
    """

    price = f"{price // 100}.{price % 100}"

    return float(price)
