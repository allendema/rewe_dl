#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2017-2023 Mike Fährmann / Allen Dema
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.
from __future__ import annotations

import sys

if not __package__ and not hasattr(sys, "frozen"):
    import os.path

    path = os.path.realpath(os.path.abspath(__file__))
    sys.path.insert(0, os.path.dirname(os.path.dirname(path)))

import rewe

"""
if __name__ == "__main__":
    raise SystemExit(rewe.main())
"""
