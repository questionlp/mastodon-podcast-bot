# Copyright (c) 2022-2024 Linh Pham
# mastodon-podcast-bot is released under the terms of the MIT License
# SPDX-License-Identifier: MIT
#
# vim: set noai syntax=python ts=4 sw=4:
"""Import JSON Entries into a Podcast Feed Database Script."""
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
        description="Import entries from a podcast feed JSON file into a database."
    )
    parser.add_argument(
        "--json-file",
        "--json",
        dest="json_file",
        help="Path to the source podcast feed JSON file",
        type=str,
        required=True,
    )
    parser.add_argument(
        "--database",
        "--db",
        dest="db_file",
        help="Path to the destination podcast feed database file",
        type=str,
        required=True,
    )
    parser.add_argument(
        "--podcast-name",
        "--podcast",
        dest="podcast_name",
        help="Podcast name used to tag the imported entries",
        type=str,
        required=True,
    )

    return parser.parse_args()


def get_entries(json_file: str) -> list[dict[str, Any]] | None:
    """Retrieve entries from a podcast feed JSON file."""
    json_file_path = Path(json_file)
    if not json_file_path.exists():
        print(f"ERROR: Podcast feed JSON database file {json_file} not found.")
        sys.exit(1)

    with json_file_path.open(mode="r", encoding="utf-8") as input_file:
        entries = json.load(input_file)

    return entries


def create_database(db_file: str) -> None:
    """Create a podcast feed database file."""
    database: Connection = sqlite3.connect(db_file)
    database.execute(
        "CREATE TABLE episodes(podcast_name str, guid str, enclosure_url str, processed str)"
    )
    database.commit()
    database.close()


def import_entries(entries: list[dict[str, Any]], db_file: str, podcast_name: str) -> None:
    """Import entries into a podcast feed database file."""
    if not entries:
        return

    data = []
    for entry in entries:
        if "podcast_name" not in entry or not entry["podcast_name"]:
            entry["podcast_name"] = podcast_name

        data.append(
            (
                entry["podcast_name"],
                entry["guid"],
                entry["enclosure_url"],
                entry["processed_date"],
            )
        )

    db_file_path = Path(db_file)
    if not db_file_path.exists():
        create_database(db_file=db_file)

    database: Connection = sqlite3.connect(db_file)
    database.executemany("INSERT INTO episodes VALUES(?, ?, ?, ?)", data)
    database.commit()
    return


def _main() -> None:
    """Script entry point."""
    _command = command_parse()
    _entries = get_entries(json_file=_command.json_file)
    if not _entries:
        print("No entries to import.")
        return

    import_entries(entries=_entries, db_file=_command.db_file, podcast_name=_command.podcast_name)
    return


if __name__ == "__main__":
    _main()
