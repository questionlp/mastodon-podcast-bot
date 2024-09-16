# Copyright (c) 2022-2024 Linh Pham
# mastodon-podcast-bot is released under the terms of the MIT License
# SPDX-License-Identifier: MIT
#
# vim: set noai syntax=python ts=4 sw=4:
"""Podcast Feed Module."""
from typing import Any
from urllib import request

import podcastparser


class PodcastFeed:
    """Podcast Feed Fetcher."""

    def fetch(
        self,
        feed_url: str,
        max_episodes: int = 50,
        user_agent="Mozilla/5.0 (Linux x86_64; rv:122.0) Gecko/20100101 Firefox/122.0",
    ) -> list[dict[str, Any]]:
        """Fetch items from the requested podcast feed."""
        feed_request = request.Request(url=feed_url, headers={"User-Agent": user_agent})
        feed: dict[str, Any] = podcastparser.parse(
            url=feed_url,
            stream=request.urlopen(feed_request),
            max_episodes=max_episodes,
        )
        return feed["episodes"]

    def __str__(self):
        return self.__class__.__name__
