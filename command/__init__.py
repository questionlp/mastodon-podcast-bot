# Copyright (c) 2022-2024 Linh Pham
# mastodon-podcast-bot is released under the terms of the MIT License
# SPDX-License-Identifier: MIT
#
# vim: set noai syntax=python ts=4 sw=4:
"""Application Command-Line Parsing Module."""
from argparse import ArgumentParser, Namespace


class AppCommand:
    """Application command-line arguments, options and flags."""

    def parse(self) -> Namespace:
        """Parse command-line arguments, options and flags using ArgumentParser."""
        parser: ArgumentParser = ArgumentParser(
            description="Fetch items from a podcast feed and publish new items to a Mastodon account."
        )
        parser.add_argument(
            "-m",
            "--multiple-feeds",
            action="store_true",
            default=False,
            help="Process multiple podcast feeds from feeds JSON settings file",
        )
        parser.add_argument(
            "-e",
            "--env-file",
            type=str,
            default=".env",
            help="Environment settings file (default: .env)",
        )
        parser.add_argument(
            "-f",
            "--feeds-file",
            type=str,
            default="feeds.json",
            help="Podcast feeds settings file (default: feeds.json)",
        )
        parser.add_argument(
            "--debug", action="store_true", help="Enable debug output to stdout"
        )
        parser.add_argument(
            "--skip-clean",
            action="store_true",
            help="Skip database clean-up after processing and posting episodes",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Parse podcast feed but do not post anything",
        )
        parser.add_argument(
            "--version",
            action="store_true",
            help="Prints out the version of the application and exits.",
        )

        return parser.parse_args()
