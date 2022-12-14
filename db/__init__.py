# -*- coding: utf-8 -*-
# vim: set noai syntax=python ts=4 sw=4:
# SPDX-License-Identifier: MIT
#
# Copyright (c) 2022 Linh Pham
# mastodon-podcast-bot is released under the terms of the MIT License

from datetime import datetime, timedelta
from pathlib import Path
import sqlite3
from sqlite3 import Connection, Cursor
from typing import Any


class FeedDatabase:
    """Class that provides simple access methods to initialize, query,
    or insert data into an instance of a SQLite3 feed database."""

    def __init__(self, db_file: str = None) -> None:
        """Class initialization method."""
        if db_file and not Path(db_file).exists():
            self.initialize(db_file)
            self.connection: Connection = sqlite3.connect(db_file)
        if db_file and Path(db_file).exists():
            self.connection: Connection = sqlite3.connect(db_file)

    def initialize(self, db_file: str) -> None:
        """Initialize feed database with the required table"""
        if Path(db_file).exists():
            return

        database: Connection = sqlite3.connect(db_file)
        database.execute("CREATE TABLE episodes(guid str, processed datetime)")
        database.close()
        return

    def connect(self, db_file: str) -> None:
        """Returns a connection to the feed database."""
        if Path(db_file).exists():
            self.connection = sqlite3.connect(db_file)

    def insert(self, guid: str, timestamp: datetime = datetime.now()) -> None:
        """Insert feed episode GUID into the feed database with a
        timestamp (default: current date/time)."""
        self.connection.execute(
            "INSERT INTO episodes (guid, processed) VALUES (?, ?)",
            (guid, timestamp),
        )
        self.connection.commit()
        return

    def retrieve(self, episode_guid: str) -> dict[str, Any]:
        """Retrieve stored information for a specific episode GUID from
        the feed database."""
        episode: dict[str, Any] = {}
        result: Cursor = self.connection.execute(
            "SELECT guid, processed FROM episodes WHERE guid = ? LIMIT 1", episode_guid
        )
        episode["guid"], episode["processed"] = result.fetchone()
        return episode

    def retrieve_guids(self) -> list[str]:
        """Retrieve all episode GUIDs from the feed database."""
        episodes: list[str] = []
        for guid in self.connection.execute("SELECT guid FROM episodes"):
            episodes.append(guid[0])

        return episodes

    def clean(self, days_to_keep: int = 90) -> None:
        """Remove episode entries from the database that are older than
        a certain number of days (default: 90)."""
        datetime_filter: datetime = datetime.now() - timedelta(days=days_to_keep)
        self.connection.execute(
            "DELETE FROM episodes WHERE processed <= ?",
            (datetime_filter,)
        )
        self.connection.commit()
