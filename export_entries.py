# Copyright (c) 2022-2024 Linh Pham
# mastodon-podcast-bot is released under the terms of the MIT License
# SPDX-License-Identifier: MIT
#
# vim: set noai syntax=python ts=4 sw=4:
"""Export Podcast Feed Database Entries to a JSON File Script."""
import json
import sqlite3
import sys
from argparse import ArgumentParser, Namespace
from pathlib import Path
from sqlite3 import Connection
from typing import Any


def command_parse() -> Namespace:
    """Parse command arguments and options."""
    parser: ArgumentParser = ArgumentParser(
        description="Export entries from a podcast feed database to a JSON file."
    )
    parser.add_argument(
        "--database",
        "--db",
        dest="db_file",
        help="Path to the source podcast feed database file",
        type=str,
        required=True,
    )
    parser.add_argument(
        "--json-file",
        "--json",
        dest="json_file",
        help="Path to the destination podcast feed JSON file",
        type=str,
        required=True,
    )
    parser.add_argument(
        "--podcast-name",
        "--podcast",
        dest="podcast_name",
        help="Podcast name used to tag the exported entries",
        type=str,
        required=True,
    )
    return parser.parse_args()


def get_entries(db_file: str, podcast_name: str = None) -> list[dict[str, Any]] | None:
    """Retrieve entries from a podcast feed database file."""
    db_file_path = Path(db_file)
    if not db_file_path.exists():
        print(f"ERROR: Podcast feed database file {db_file} not found.")
        sys.exit(1)

    database: Connection = sqlite3.connect(db_file)
    database.row_factory = sqlite3.Row
    cursor = database.execute(
        """SELECT guid, enclosure_url, processed FROM episodes ORDER BY processed ASC"""
    )
    records = cursor.fetchall()
    cursor.close()

    if not records:
        return None

    entries = []
    for record in records:
        entries.append(
            {
                "podcast_name": podcast_name
                if podcast_name
                else record["podcast_name"],
                "guid": record["guid"],
                "enclosure_url": record["enclosure_url"],
                "processed_date": record["processed"],
            }
        )

    return entries


def export_json(entries: list[dict[str, Any]], json_file: str) -> None:
    """Export entries to a JSON file."""
    if not entries:
        return None

    json_file_path = Path(json_file)
    with json_file_path.open(mode="wt", encoding="utf-8") as output_file:
        json.dump(entries, output_file, sort_keys=False, indent=2)

    return None


def _main() -> None:
    """Script entry point."""
    _command = command_parse()
    _entries = get_entries(
        db_file=_command.db_file,
        podcast_name=_command.podcast_name,
    )
    if not _entries:
        print("No entries to export.")
        return None

    export_json(entries=_entries, json_file=_command.json_file)


if __name__ == "__main__":
    _main()
