# Copyright (c) 2022-2024 Linh Pham
# mastodon-podcast-bot is released under the terms of the MIT License
# SPDX-License-Identifier: MIT
#
# vim: set noai syntax=python ts=4 sw=4:
"""Application Configuration Module."""
import json
import sys
from pathlib import Path
from typing import NamedTuple

from dotenv import dotenv_values


class FeedSettings(NamedTuple):
    """Podcast Feed Settings."""

    name: str
    podcast_name: str
    feed_url: str
    mastodon_secret: str
    mastodon_api_base_url: str
    database_file: str = "feed_info.sqlite3"
    database_clean_days: int = 90
    log_file: str = "logs/podcast_bot.log"
    recent_days: int = 5
    max_episodes: int = 50
    max_description_length: int = 275
    guid_filter: str = None
    user_agent: str = (
        "Mozilla/5.0 (Linux x86_64; rv:122.0) Gecko/20100101 Firefox/122.0"
    )
    template_directory: str = "templates"
    template_file: str = "post.txt.jinja"


class AppConfig:
    """Application podcast feeds settings."""

    def parse(self, feeds_file: str = "feeds.json") -> list[FeedSettings]:
        """Parse podcast feeds settings."""
        feeds_path = Path.cwd() / feeds_file
        with feeds_path.open(mode="r", encoding="utf-8") as feeds_file:
            feeds = json.load(feeds_file)
            if not feeds:
                print("ERROR: Podcast Feeds Settings JSON file could not be parsed.")
                sys.exit(1)

            if not isinstance(feeds, list):
                print("ERROR: Podcast Feeds Settings JSON file is not valid.")
                sys.exit(1)

        feeds_settings: list[FeedSettings] = []
        for podcast_feed in feeds:
            feed = dict(podcast_feed)
            if (
                "feed_name" not in feed
                or "podcast_name" not in feed
                or "podcast_feed_url" not in feed
            ):
                print("ERROR: Podcast feed information is not valid.")
                sys.exit(1)

            if "mastodon_secret" not in feed or "mastodon_api_base_url" not in feed:
                print("ERROR: Feed settings does not contain valid Mastodon settings.")
                sys.exit(1)

            feed_settings = FeedSettings(
                name=feed["feed_name"].strip(),
                podcast_name=feed["podcast_name"].strip(),
                feed_url=feed["podcast_feed_url"].strip(),
                mastodon_secret=feed["mastodon_secret"].strip(),
                mastodon_api_base_url=feed["mastodon_api_base_url"].strip(),
                database_file=feed.get("database_file", "feed_info.sqlite3").strip(),
                database_clean_days=int(feed.get("database_clean_days", 90)),
                log_file=feed.get("log_file", "logs/podcast_bot.log").strip(),
                recent_days=int(feed.get("recent_days", 90)),
                max_episodes=int(feed.get("max_episodes", 50)),
                max_description_length=int(feed.get("max_description_length", 275)),
                guid_filter=feed.get("podcast_guid_filter", "").strip(),
                user_agent=feed.get(
                    "user_agent",
                    "Mozilla/5.0 (Linux x86_64; rv:122.0) Gecko/20100101 Firefox/122.0",
                ).strip(),
                template_directory=feed.get("template_directory", "templates").strip(),
                template_file=feed.get("template_file", "post.txt.jinja").strip(),
            )
            feeds_settings.append(feed_settings)

        return feeds_settings


class AppEnvironment:
    """Application environment variables."""

    def parse(self, dotenv_file: str = ".env") -> list[FeedSettings]:
        """Parse configuration values using .env file."""
        dotenv_config: dict[str, str | None] = dotenv_values(dotenv_file)

        # Check for required configuration settings. Immediate exit if any
        # of the required settings are not found.
        if (
            "PODCAST_NAME" not in dotenv_config
            or "PODCAST_FEED_URL" not in dotenv_config
        ):
            print("ERROR: Podcast feed information is not valid.")
            sys.exit(1)

        if (
            "MASTODON_SECRET" not in dotenv_config
            or "MASTODON_API_BASE_URL" not in dotenv_config
        ):
            print("ERROR: Feed settings does not contain valid Mastodon settings.")
            sys.exit(1)

        feed_settings = FeedSettings(
            name=dotenv_config.get("PODCAST_NAME").strip(),
            podcast_name=dotenv_config.get("PODCAST_NAME").strip(),
            feed_url=dotenv_config.get("PODCAST_FEED_URL").strip(),
            mastodon_secret=dotenv_config["MASTODON_SECRET"].strip(),
            mastodon_api_base_url=dotenv_config["MASTODON_API_BASE_URL"].strip(),
            database_file=dotenv_config.get("DB_FILE", "feed_info.sqlite3").strip(),
            database_clean_days=int(dotenv_config.get("DB_CLEAN_DAYS", 90)),
            log_file=dotenv_config.get("LOG_FILE", "logs/podcast_bot.log").strip(),
            recent_days=int(dotenv_config.get("RECENT_DAYS", 5)),
            max_episodes=int(dotenv_config.get("MAX_EPISODES", 50)),
            max_description_length=int(
                dotenv_config.get("MAX_DESCRIPTION_LENGTH", 275)
            ),
            guid_filter=dotenv_config.get("PODCAST_GUID_FILTER", "").strip(),
            user_agent=dotenv_config.get(
                "USER_AGENT",
                "Mozilla/5.0 (Linux x86_64; rv:122.0) Gecko/20100101 Firefox/122.0",
            ).strip(),
            template_directory=dotenv_config.get(
                "POST_TEMPLATE_DIR", "templates"
            ).strip(),
            template_file=dotenv_config.get("POST_TEMPLATE", "post.txt.jinja").strip(),
        )

        return [feed_settings]
