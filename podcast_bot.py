# -*- coding: utf-8 -*-
# vim: set noai syntax=python ts=4 sw=4:
# SPDX-License-Identifier: MIT
#
# Copyright (c) 2022 Linh Pham
# mastodon-podcast-bot is released under the terms of the MIT License

from argparse import Namespace
from datetime import datetime, timedelta
from pprint import pprint
from typing import Any

from html2text import HTML2Text
from jinja2 import Environment, FileSystemLoader, select_autoescape, Template

from command import AppCommand
from config import AppEnvironment
from db import FeedDatabase
from feed import PodcastFeed
from mastodon_client import MastodonClient

APP_VERSION: str = "0.1.6"


def retrieve_new_episodes(
    feed_episodes: list[dict[str, Any]],
    feed_database: FeedDatabase,
    guid_filter: str = "",
    days: int = 7,
    dry_run: bool = False,
    debug: bool = False,
) -> list[dict[str, Any]]:
    """Iterate through the episodes retrieved from a podcast feed and
    return any new or unseen episodes that have been posted recently."""
    seen_guids: list[str] = feed_database.retrieve_guids()
    seen_enclosure_urls: list[str] = feed_database.retrieve_enclosure_urls()
    if debug:
        print("Seen GUIDs:")
        pprint(seen_guids)
        print("Seen Enclosure URLs:")
        pprint(seen_enclosure_urls)

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
                        "description": episode["description_html"].strip(),
                        "duration": timedelta(seconds=episode["total_time"]),
                        "url": enclosure_url,
                    }
                    episodes.append(info)
                    if debug:
                        print(f"Episode Info for GUID {guid}:")
                        pprint(info)
                    if not dry_run:
                        # Only add the enclosure URL if it's not already in
                        # the episodes table to prevent duplicate entries.
                        if enclosure_url not in seen_enclosure_urls:
                            feed_database.insert(
                                guid=guid,
                                enclosure_url=enclosure_url,
                                timestamp=datetime.now(),
                            )
                        else:
                            feed_database.insert(
                                guid=guid,
                                timestamp=datetime.now(),
                            )

    return episodes


def unsmart_quotes(text: str) -> str:
    """Replaces "smart" quotes with normal single and double quote
    marks."""
    text: str = text.replace("’", "'")
    text = text.replace("”", '"')
    text = text.replace("“", '"')
    return text


def format_post(
    episode: dict[str, Any],
    podcast_name: str = None,
    description_max_length: int = 275,
    template_path: str = "templates",
    template_file: str = "post.txt.jinja",
) -> str:
    """Returns a formatted string based on the episode metadata,
    including: title, description and episode URL."""
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

    if len(formatted_description) > description_max_length:
        formatted_description = (
            f"{formatted_description[:description_max_length].strip()}...\n"
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
    """Main function used to pull and parse podcast feed and
    post any new items found in the podcast feed."""

    arguments: Namespace = AppCommand().parse()
    if arguments.version:
        print(f"Version {APP_VERSION}")
        return

    env: dict = AppEnvironment().parse()
    dry_run: bool = arguments.dry_run

    if arguments.debug:
        print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S %Z')}")
    # Check to see if the feed database file exists. Create file if
    # the file does not exist
    feed_database: FeedDatabase = FeedDatabase(env["db_file"])

    # Pull episodes from the configured podcast feed
    podcast: PodcastFeed = PodcastFeed()
    episodes: list[dict[str, Any]] = podcast.fetch(
        feed_url=env["podcast_feed"], max_episodes=env["max_episodes"]
    )

    # Connect to Mastodon Client
    mastodon_client: MastodonClient = MastodonClient(
        api_url=env["mastodon"]["api_url"], access_token=env["mastodon"]["secret_file"]
    )

    if episodes:
        new_episodes: list[dict[str, Any]] = retrieve_new_episodes(
            feed_episodes=episodes,
            feed_database=feed_database,
            guid_filter=env["podcast_guid_filter"],
            days=env["recent_days"],
            dry_run=dry_run,
            debug=arguments.debug,
        )
        new_episodes.reverse()
        if arguments.debug:
            print("New Episodes:")
            pprint(new_episodes)

        for episode in new_episodes:
            post_text: str = format_post(
                podcast_name=env["podcast_name"],
                episode=episode,
                template_path=env["post_template_dir"],
                template_file=env["post_template"],
            )
            if not dry_run:
                mastodon_client.post(content=post_text)

    if not dry_run or not arguments.skip_clean:
        feed_database.clean(days_to_keep=env["db_clean_days"])

    if arguments.debug:
        print(f"Completed time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S %Z')}")


if __name__ == "__main__":
    main()
