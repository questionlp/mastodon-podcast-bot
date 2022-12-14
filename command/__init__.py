# -*- coding: utf-8 -*-
# vim: set noai syntax=python ts=4 sw=4:
# SPDX-License-Identifier: MIT
#
# Copyright (c) 2022 Linh Pham
# mastodon-podcast-bot is released under the terms of the MIT License

from argparse import ArgumentParser, Namespace


class AppCommand:
    """Application command-line arguments, options and flags."""

    def parse(self) -> Namespace:
        """Parse command-line arguments, options and flags using
        ArgumentParser."""
        parser: ArgumentParser = ArgumentParser(
            description="Fetch items from a podcast feed and publish new items to a Mastodon account."
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
            "--env-file",
            type=str,
            default=".env",
            help="Environment settings file (default: .env)",
        )
        parser.add_argument(
            "--version",
            action="store_true",
            help="Prints out the version of the application and exits.",
        )

        return parser.parse_args()
