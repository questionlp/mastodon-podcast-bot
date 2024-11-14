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

_DEFAULT_USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64; rv:130.0) Gecko/20100101 Firefox/130.0"


class FeedSettings(NamedTuple):
    """Podcast Feed Settings."""

    name: str
    podcast_name: str
    feed_url: str
    mastodon_use_secrets_file: bool
    mastodon_api_base_url: str
    mastodon_secrets_file: str = None
    mastodon_client_secret: str = None
    mastodon_access_token: str = None
    database_file: str = "feed_info.sqlite3"
    database_clean_days: int = 90
    log_file: str = "logs/podcast_bot.log"
    recent_days: int = 5
    max_episodes: int = 50
    max_description_length: int = 275
    guid_filter: str = None
    user_agent: str = _DEFAULT_USER_AGENT
    template_directory: str = "templates"
    template_file: str = "post.txt.jinja"
    enabled: bool = True


class AppConfig:
    """Application podcast feeds settings."""

    def parse(self, feeds_file: str = "feeds.json") -> list[FeedSettings]:
        """Parse podcast feeds settings."""
        feeds_path = Path.cwd() / feeds_file
        with feeds_path.open(mode="r", encoding="utf-8") as _feeds_file:
            feeds = json.load(_feeds_file)
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

            if "mastodon_api_base_url" not in feed:
                print("ERROR: Feed settings does not contain a Mastodon API base URL.")
                sys.exit(1)

            if "mastodon_use_secrets_file" in feed:
                use_secrets_file = bool(feed["mastodon_use_secrets_file"])
            else:
                use_secrets_file = True

            secrets_file = None
            if use_secrets_file and "mastodon_secret" in feed:
                secrets_file = feed["mastodon_secret"].strip()
            elif use_secrets_file and "mastodon_secrets_file" in feed:
                secrets_file = feed["mastodon_secrets_file"].strip()

            if use_secrets_file and not secrets_file:
                print("ERROR: Mastodon secrets file path setting not found.")
                sys.exit(1)

            if not use_secrets_file and (
                "mastodon_client_secret" not in feed or "mastodon_access_token" not in feed
            ):
                print("ERROR: Mastodon client secret or access token setting not found.")

            feed_settings = FeedSettings(
                name=feed["feed_name"].strip(),
                podcast_name=feed["podcast_name"].strip(),
                enabled=bool(feed.get("enabled", True)),
                feed_url=feed["podcast_feed_url"].strip(),
                mastodon_use_secrets_file=use_secrets_file,
                mastodon_secrets_file=(secrets_file if use_secrets_file and secrets_file else None),
                mastodon_client_secret=feed.get("mastodon_client_secret", "").strip(),
                mastodon_access_token=feed.get("mastodon_access_token", "").strip(),
                mastodon_api_base_url=feed.get("mastodon_api_base_url", "").strip(),
                database_file=feed.get("database_file", "feed_info.sqlite3").strip(),
                database_clean_days=int(feed.get("database_clean_days", 90)),
                log_file=feed.get("log_file", "logs/podcast_bot.log").strip(),
                recent_days=int(feed.get("recent_days", 90)),
                max_episodes=int(feed.get("max_episodes", 50)),
                max_description_length=int(feed.get("max_description_length", 275)),
                guid_filter=feed.get("podcast_guid_filter", "").strip(),
                user_agent=feed.get("user_agent", _DEFAULT_USER_AGENT).strip(),
                template_directory=feed.get("template_directory", "templates").strip(),
                template_file=feed.get("template_file", "post.txt.jinja").strip(),
            )
            feeds_settings.append(feed_settings)

        return feeds_settings

    def __str__(self) -> str:
        return self.__class__.__name__


class AppEnvironment:
    """Application environment variables."""

    def parse(self, dotenv_file: str = ".env") -> list[FeedSettings]:
        """Parse configuration values using .env file."""
        dotenv_config: dict[str, str | None] = dotenv_values(dotenv_file)

        # Check for required configuration settings. Immediate exit if any
        # of the required settings are not found.
        if "PODCAST_NAME" not in dotenv_config or "PODCAST_FEED_URL" not in dotenv_config:
            print("ERROR: Podcast feed information is not valid.")
            sys.exit(1)

        if "MASTODON_API_BASE_URL" not in dotenv_config:
            print("ERROR: Feed settings does not contain a Mastodon API base URL.")
            sys.exit(1)

        if "MASTODON_USE_SECRETS_FILE" in dotenv_config:
            use_secrets_file = bool(dotenv_config.get("MASTODON_USER_SECRETS_FILE", True))
        else:
            use_secrets_file = True

        if use_secrets_file and "MASTODON_SECRET" in dotenv_config:
            secrets_file = dotenv_config["MASTODON_SECRET"].strip()
        elif use_secrets_file and "MASTODON_SECRETS_FILE" in dotenv_config:
            secrets_file = dotenv_config["MASTODON_SECRETS_FILE"].strip()
        else:
            print("ERROR: Mastodon secrets file path setting not found.")
            sys.exit(1)

        if not use_secrets_file and (
            "MASTODON_CLIENT_SECRET" not in dotenv_config
            or "MASTODON_ACCESS_TOKEN" not in dotenv_config
        ):
            print("ERROR: Mastodon client secret or access token not found.")
            sys.exit(1)

        feed_settings = FeedSettings(
            name=dotenv_config.get("PODCAST_NAME").strip(),
            podcast_name=dotenv_config.get("PODCAST_NAME").strip(),
            enabled=bool(dotenv_config.get("enabled", True)),
            feed_url=dotenv_config.get("PODCAST_FEED_URL").strip(),
            mastodon_use_secrets_file=use_secrets_file,
            mastodon_secret=secrets_file if use_secrets_file and secrets_file else None,
            mastodon_client_secret=dotenv_config.get("MASTODON_CLIENT_SECRET", "").strip(),
            mastodon_access_token=dotenv_config.get("MASTODON_ACCESS_CLIENT", "").strip(),
            mastodon_api_base_url=dotenv_config.get("MASTODON_API_BASE_URL", "").strip(),
            database_file=dotenv_config.get("DB_FILE", "feed_info.sqlite3").strip(),
            database_clean_days=int(dotenv_config.get("DB_CLEAN_DAYS", 90)),
            log_file=dotenv_config.get("LOG_FILE", "logs/podcast_bot.log").strip(),
            recent_days=int(dotenv_config.get("RECENT_DAYS", 5)),
            max_episodes=int(dotenv_config.get("MAX_EPISODES", 50)),
            max_description_length=int(dotenv_config.get("MAX_DESCRIPTION_LENGTH", 275)),
            guid_filter=dotenv_config.get("PODCAST_GUID_FILTER", "").strip(),
            user_agent=dotenv_config.get("USER_AGENT", _DEFAULT_USER_AGENT).strip(),
            template_directory=dotenv_config.get("POST_TEMPLATE_DIR", "templates").strip(),
            template_file=dotenv_config.get("POST_TEMPLATE", "post.txt.jinja").strip(),
        )

        return [feed_settings]

    def __str__(self) -> str:
        return self.__class__.__name__
