# -*- coding: utf-8 -*-
# vim: set noai syntax=python ts=4 sw=4:
# SPDX-License-Identifier: MIT
#
# Copyright (c) 2022 Linh Pham
# mastodon-podcast-bot is released under the terms of the MIT License

import urllib.request
from typing import Any

import podcastparser


class PodcastFeed:
    """Simple wrapper for podcastparser module used to fetch episodes
    from a podcast feed."""

    def fetch(self, feed_url: str, max_episodes: int = 50) -> list[dict[str, Any]]:
        """Fetch items from the requested podcast feed"""
        feed: dict[str, Any] = podcastparser.parse(
            url=feed_url,
            stream=urllib.request.urlopen(feed_url),
            max_episodes=max_episodes,
        )
        return feed["episodes"]
