# -*- coding: utf-8 -*-
# vim: set noai syntax=python ts=4 sw=4:
# SPDX-License-Identifier: MIT
#
# Copyright (c) 2022 Linh Pham
# mastodon-podcast-bot is released under the terms of the MIT License

from mastodon import Mastodon


class MastodonClient:
    """Simple Mastodon Client that is a wrapper for Mastodon.py used
    to connect and publish posts."""

    def __init__(self, api_url: str | None, access_token: str | None) -> None:
        """Class initialization method."""
        if api_url and access_token:
            self.connection: Mastodon = self.connect(
                api_url=api_url, access_token=access_token
            )

    def connect(self, api_url: str, access_token: str) -> Mastodon:
        """Connect and authenticate against a Mastodon instance API
        using OAuth2."""

        return Mastodon(access_token=access_token, api_base_url=api_url)

    def post(
        self,
        content: str,
        sensitive: bool = False,
        visibility: str = "public",
        spoiler_text: str = None,
    ) -> None:
        """Post content to a connected Mastodon account."""
        self.connection.status_post(
            status=content,
            sensitive=sensitive,
            visibility=visibility,
            spoiler_text=spoiler_text,
        )
