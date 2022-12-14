# -*- coding: utf-8 -*-
# vim: set noai syntax=python ts=4 sw=4:
# SPDX-License-Identifier: MIT
#
# Copyright (c) 2022 Linh Pham
# mastodon-podcast-bot is released under the terms of the MIT License

import sys

from dotenv import dotenv_values


class AppEnvironment:
    """Application environment variables."""

    def parse(self, dotenv_file: str = ".env") -> dict[str, str | int]:
        """Parse configuration values using .env file."""
        dotenv_config: dict[str, str | None] = dotenv_values(dotenv_file)

        # Check for required configuration settings. Immediate exit if any
        # of the required settings are not found.
        if "PODCAST_FEED_URL" not in dotenv_config:
            print(f"ERROR: PODCAST_FEED_URL is missing from {dotenv_file}.")
            sys.exit(1)

        if "MASTODON_SECRET" not in dotenv_config:
            print(f"ERROR: MASTODON_SECRET is missing from {dotenv_file}.")
            sys.exit(1)

        if "MASTODON_API_BASE_URL" not in dotenv_config:
            print(f"ERROR: MASTODON_API_BASE_URL is missing from {dotenv_file}.")
            sys.exit(1)

        # Create configuration dictionary objects
        config: dict[str, str | int] = {}
        config["mastodon"]: dict[str, str | int] = {}

        # Load values into the configuration dictionary
        config["db_file"]: str = dotenv_config.get("DB_FILE", "feed_info.sqlite3")
        config["db_clean_days"]: int = int(dotenv_config.get("DB_CLEAN_DAYS", 90))
        config["recent_days"]: int = int(dotenv_config.get("RECENT_DAYS", 5))
        config["max_episodes"]: int = int(dotenv_config.get("MAX_EPISODES", 50))
        config["podcast_feed"]: str = dotenv_config.get("PODCAST_FEED_URL")
        config["podcast_name"]: str = dotenv_config.get("PODCAST_NAME", None)
        config["post_template_dir"]: str = dotenv_config.get("POST_TEMPLATE_DIR", "templates")
        config["post_template"]: str = dotenv_config.get("POST_TEMPLATE", "post.txt.jinja")
        config["mastodon"]["secret_file"]: str = dotenv_config["MASTODON_SECRET"]
        config["mastodon"]["api_url"]: str = dotenv_config["MASTODON_API_BASE_URL"]

        return config
