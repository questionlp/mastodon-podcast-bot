# Copyright (c) 2022-2024 Linh Pham
# mastodon-podcast-bot is released under the terms of the MIT License
# SPDX-License-Identifier: MIT
#
# vim: set noai syntax=python ts=4 sw=4:
"""Mastodon Client Module."""
from mastodon import Mastodon


class MastodonClient:
    """Simple Mastodon Client for connecting and publishing posts."""

    def __init__(
        self,
        api_url: str | None,
        client_secret: str | None = None,
        access_token: str | None = None,
    ) -> None:
        """Class initialization method."""
        if api_url and access_token:
            self.connection: Mastodon = self.connect(
                api_url=api_url, access_token=access_token
            )
        elif api_url and client_secret and access_token:
            self.connection: Mastodon = self.connect(
                api_url=api_url, client_secret=client_secret, access_token=access_token
            )

    def connect(
        self,
        api_url: str,
        client_secret: str | None = None,
        access_token: str | None = None,
    ) -> Mastodon | None:
        """Connect to and authenticate against a Mastodon instance."""
        if client_secret and access_token:
            return Mastodon(
                client_secret=client_secret,
                access_token=access_token,
                api_base_url=api_url,
            )
        elif access_token:
            return Mastodon(access_token=access_token, api_base_url=api_url)
        else:
            return None

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
