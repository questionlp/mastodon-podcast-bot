# Copyright (c) 2022-2024 Linh Pham
# mastodon-podcast-bot is released under the terms of the MIT License
# SPDX-License-Identifier: MIT
#
# vim: set noai syntax=python ts=4 sw=4:
"""Mastodon Podcast Feed Bot."""
import logging
import sys
from argparse import Namespace
from datetime import datetime, timedelta
from pprint import pformat
from typing import Any

from html2text import HTML2Text
from jinja2 import Environment, FileSystemLoader, Template, select_autoescape

from command import AppCommand
from config import AppConfig, AppEnvironment, FeedSettings
from db import FeedDatabase
from feed import PodcastFeed
from mastodon_client import MastodonClient

APP_VERSION: str = "1.1.0"
logger: logging.Logger = logging.getLogger(__name__)


def retrieve_new_episodes(
    feed_episodes: list[dict[str, Any]],
    feed_database: FeedDatabase,
    feed_name: str = None,
    guid_filter: str = "",
    days: int = 7,
    dry_run: bool = False,
) -> list[dict[str, Any]]:
    """Retrieve new episodes from a podcast feed."""
    seen_guids: list[str] = feed_database.retrieve_guids(feed_name=feed_name)
    seen_enclosure_urls: list[str] = feed_database.retrieve_enclosure_urls(
        feed_name=feed_name
    )

    logger.debug(f"Seen GUIDs:\n{pformat(seen_guids, compact=True)}")
    logger.debug(f"Seen Enclosure URLs:\n{pformat(seen_enclosure_urls, compact=True)}")

    episodes: list[dict[str, Any]] = []

    for episode in feed_episodes:
        guid: str = episode["guid"]
        enclosure_url: str = episode["enclosures"][0]["url"].strip()
        publish_date: datetime = datetime.fromtimestamp(episode["published"])

        if datetime.now() - publish_date <= timedelta(days=days):
            # Only process episodes in which the GUID or the enclosure URL are
            # not in the episodes database table
            if guid not in seen_guids or enclosure_url not in seen_enclosure_urls:
                # Use guid_filter to match against the episode GUID to filter
                # out any random or incorrect GUIDs. This is a workaround to
                # reduce issues encountered with American Public Media feeds
                if guid_filter is not None and guid_filter.lower() in guid.lower():
                    info: dict[str, Any] = {
                        "guid": guid,
                        "published": publish_date,
                        "title": episode["title"].strip(),
                        "duration": timedelta(seconds=episode["total_time"]),
                        "url": enclosure_url,
                    }

                    if "description_html" in episode:
                        info["description"] = episode["description_html"].strip()
                    else:
                        info["description"] = episode["description"].strip()

                    episodes.append(info)
                    logger.debug(
                        f"Episode Info for GUID {guid}:\n{pformat(info, sort_dicts=False, compact=True)}"
                    )

                    if not dry_run:
                        # Only add the enclosure URL if it's not already in
                        # the episodes table to prevent duplicate entries.
                        if enclosure_url not in seen_enclosure_urls:
                            feed_database.insert(
                                guid=guid,
                                enclosure_url=enclosure_url,
                                feed_name=feed_name,
                                timestamp=datetime.now(),
                            )
                        else:
                            feed_database.insert(
                                guid=guid,
                                feed_name=feed_name,
                                timestamp=datetime.now(),
                            )

    return episodes


def unsmart_quotes(text: str) -> str:
    """Replaces "smart" quotes with normal quotes."""
    text: str = text.replace("’", "'")
    text = text.replace("”", '"')
    text = text.replace("“", '"')
    return text


def format_post(
    episode: dict[str, Any],
    podcast_name: str = None,
    max_description_length: int = 275,
    template_path: str = "templates",
    template_file: str = "post.txt.jinja",
) -> str:
    """Returns a formatted post with episode information."""
    formatter: HTML2Text = HTML2Text()
    formatter.ignore_emphasis = True
    formatter.ignore_images = True
    formatter.ignore_links = True
    formatter.ignore_tables = True
    formatter.body_width = 0

    env: Environment = Environment(
        loader=FileSystemLoader(template_path),
        autoescape=select_autoescape(),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    template: Template = env.get_template(template_file)

    # Replace "smart" quotes with regular quotes
    title: str = unsmart_quotes(text=episode["title"])
    description: str = unsmart_quotes(text=episode["description"])
    formatted_description: str = formatter.handle(description)

    # Fix issue with HTML2Text causing + to be rendered as \+
    formatted_description = formatted_description.replace(r"\+", "+")

    if len(formatted_description) > max_description_length:
        formatted_description = (
            f"{formatted_description[:max_description_length].strip()}...\n"
        )
    else:
        formatted_description = f"{formatted_description.strip()}\n"

    return template.render(
        podcast_name=podcast_name,
        title=title,
        description=formatted_description,
        url=episode["url"],
    )


def main() -> None:
    """Fetch podcast episodes and post new episodes."""
    arguments: Namespace = AppCommand().parse()
    if arguments.version:
        print(f"Version {APP_VERSION}")
        return

    if arguments.multiple_feeds:
        feeds: list[FeedSettings] = AppConfig().parse()
    else:
        feeds: list[FeedSettings] = AppEnvironment().parse()

    if not feeds or not isinstance(feeds, list):
        print("ERROR: No podcast feed(s) defined.")
        sys.exit(1)

    dry_run: bool = arguments.dry_run

    for feed in feeds:
        if feed.log_file:
            log_handler: logging.FileHandler = logging.FileHandler(feed.log_file)
            log_format: logging.Formatter = logging.Formatter(
                fmt="%(asctime)s %(levelname)s %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
            )
            log_handler.setFormatter(log_format)
            if arguments.debug:
                logger.setLevel(logging.DEBUG)
            else:
                logger.setLevel(logging.INFO)

            logger.addHandler(log_handler)

        logger.debug("Starting")
        logger.debug(f"Podcast Name: {feed.podcast_name}")

        # Check to see if the feed database file exists. Create file if
        # the file does not exist
        feed_database: FeedDatabase = FeedDatabase(feed.database_file)

        # Pull episodes from the configured podcast feed
        podcast: PodcastFeed = PodcastFeed()
        episodes: list[dict[str, Any]] = podcast.fetch(
            feed_url=feed.feed_url,
            max_episodes=feed.max_episodes,
            user_agent=feed.user_agent,
        )
        logger.debug(f"Feed URL: {feed.feed_url}")

        # Connect to Mastodon Client
        logger.debug(f"Mastodon URL: {feed.mastodon_api_base_url}")
        mastodon_client: MastodonClient = MastodonClient(
            api_url=feed.mastodon_api_base_url,
            access_token=feed.mastodon_secret,
        )

        if episodes:
            new_episodes: list[dict[str, Any]] = retrieve_new_episodes(
                feed_episodes=episodes,
                feed_database=feed_database,
                feed_name=feed.name,
                guid_filter=feed.guid_filter,
                days=feed.recent_days,
                dry_run=dry_run,
            )
            new_episodes.reverse()

            logger.debug(f"New Episodes:\n{pformat(new_episodes)}")

            for episode in new_episodes:
                episode["title"] = unsmart_quotes(text=episode["title"])
                post_text: str = format_post(
                    podcast_name=feed.podcast_name,
                    episode=episode,
                    max_description_length=feed.max_description_length,
                    template_path=feed.template_directory,
                    template_file=feed.template_file,
                )
                if not dry_run:
                    logger.info(f"Posting {episode}.")
                    mastodon_client.post(content=post_text)

        if not dry_run or not arguments.skip_clean:
            feed_database.clean(days_to_keep=feed.database_clean_days)

        logger.debug("Finished")
        log_handler.close()
        logger.removeHandler(log_handler)


if __name__ == "__main__":
    main()
