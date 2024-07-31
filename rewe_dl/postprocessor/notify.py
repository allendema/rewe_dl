#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2023-2024 Allen Dema
from __future__ import annotations

import os
import sys
import logging
from os import path
from json import dumps

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(PROJECT_DIR))

from postprocessor.common import PostProcessor

import httpx

log = logging.getLogger(__name__)


class NotifyPP(PostProcessor):
    def __init__(self, md, options):
        PostProcessor.__init__(self, options)
        self.md = md

    @staticmethod
    def apprise(**kwargs):
        try:
            import apprise
        except Exception as e:
            return e

        current_user = os.environ.get("USER", os.environ.get("USERNAME"))
        APPRISE_CONFIG_PATH = f"/home/{current_user}/.config/apprise"

        # adopted from https://github.com/Hari-Nagarajan/fairgame/blob/cb79d40b5a91e969399a95048a700d57ec37071f/notifications/notifications.py#L40
        if path.exists(APPRISE_CONFIG_PATH):
            apb = apprise.Apprise()
            config = apprise.AppriseConfig()
            config.add(APPRISE_CONFIG_PATH)
            apb.add(config)

            def send(**kwargs):
                apb.notify(**kwargs)
                log.info("Notification sent!")

            send(**kwargs)

            """
            # Get the service names from the config, not the Apprise instance when reading from config file
            for server in config.servers():
                log.info(f"Found {server.service_name} configuration")
            """

        else:
            log.info(f"No Apprise config found at {APPRISE_CONFIG_PATH}.")
            config = None
            config.servers = []

    def matrix(self, **kwargs) -> None:
        from datetime import datetime

        headers = {
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/json;charset=utf-8",
        }

        timestamp = datetime.today().strftime("%Y-%m-%d_%H:%M:%S:%f")

        homeserver = self.config.get("matrix", {}).get("homeserver")
        room_id = self.config.get("matrix", {}).get("room_id")
        access_token = self.config.get("matrix", {}).get("access_token")
        txnId = timestamp
        message_plain = kwargs.get("title")
        message_html = f"<b><a href='{kwargs.get('url')}'>{kwargs.get('body')}\
            - {kwargs.get('title')}</a></b>"

        def send(**kwargs):
            endpoint = f"/_matrix/client/v3/rooms/{room_id}/send/m.room.message/{txnId}"

            headers.update({"Authorization": f"Bearer {access_token}"})

            r = httpx.put(
                homeserver + endpoint,
                content=dumps(
                    {
                        "format": "org.matrix.custom.html",
                        "body": message_plain,
                        "formatted_body": message_html,
                        "msgtype": "m.text",
                    },
                    # https://spec.matrix.org/v1.11/appendices/
                    # Encode code-points outside of ASCII as UTF-8 rather than \u escapes
                    ensure_ascii=False,
                    # Remove unnecessary white space.
                    separators=(",", ":"),
                    # Sort the keys of dictionaries.
                    sort_keys=True,
                    # Encode the resulting Unicode as UTF-8 bytes.
                ).encode("UTF-8"),
                headers=headers,
            )

            if r.status_code == 200:
                log.info("Notification sent!")
            else:
                log.error("Notification not sent! HTTP error {r.status_code}")

        if not homeserver:
            raise ValueError

        send(**kwargs)

    def telegram(self, text: str) -> None:
        token = self.config.get("telegram", {}).get("token")
        chat_id = self.config.get("telegram", {}).get("chat_id")

        base_api_url = "https://api.telegram.org"
        endpoint = f"/bot{token}/sendMessage"
        params = {"chat_id": chat_id, "text": text}

        httpx.get(base_api_url + endpoint, params=params)
