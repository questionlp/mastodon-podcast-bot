# Copyright (c) 2022-2024 Linh Pham
# mastodon-podcast-bot is released under the terms of the MIT License
# SPDX-License-Identifier: MIT
#
# vim: set noai syntax=python ts=4 sw=4:
"""Feed Database Module."""
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from sqlite3 import Connection, Cursor
from typing import Any


class FeedDatabase:
    """Feed Database Access."""

    _timestamp = datetime.now()

    def __init__(self, db_file: str = None) -> None:
        """Class initialization method."""
        if db_file and not Path(db_file).exists():
            self.initialize(db_file)
            self.connection: Connection = sqlite3.connect(db_file)
        if db_file and Path(db_file).exists():
            self.connection: Connection = sqlite3.connect(db_file)
            self._migrate()

    def initialize(self, db_file: str) -> None:
        """Initialize feed database with the required table."""
        if Path(db_file).exists():
            return

        database: Connection = sqlite3.connect(db_file)
        database.execute(
            "CREATE TABLE episodes(podcast_name str, guid str, enclosure_url str, processed str)"
        )
        database.commit()
        database.close()

    def _migrate(self) -> None:
        """Run any required database migration steps."""
        cursor = self.connection.execute(
            "SELECT name FROM pragma_table_info('episodes') WHERE name = 'enclosure_url'"
        )
        result = cursor.fetchone()
        cursor.close()
        if not result:
            self.connection.execute("ALTER TABLE episodes ADD COLUMN enclosure_url str")
            self.connection.commit()

        cursor = self.connection.execute(
            "SELECT name FROM pragma_table_info('episodes') WHERE name = 'podcast_name'"
        )
        result = cursor.fetchone()
        cursor.close()
        if not result:
            self.connection.execute("ALTER TABLE episodes ADD COLUMN podcast_name str")
            self.connection.commit()

    def connect(self, db_file: str) -> None:
        """Returns a connection to the feed database."""
        if Path(db_file).exists():
            self.connection = sqlite3.connect(db_file)

    def insert(
        self,
        guid: str,
        enclosure_url: str = None,
        feed_name: str = None,
        timestamp: datetime = _timestamp,
    ) -> None:
        """Insert feed episode GUID into the feed database with a timestamp.

        Default: current date/time.
        """
        if enclosure_url:
            self.connection.execute(
                (
                    "INSERT INTO episodes (guid, enclosure_url, podcast_name, "
                    "processed) VALUES (?, ?, ?, ?)"
                ),
                (guid, enclosure_url, feed_name, timestamp),
            )
            self.connection.commit()
        else:
            self.connection.execute(
                ("INSERT INTO episodes (guid, podcast_name, processed) VALUES (?, ?, ?)"),
                (guid, feed_name, timestamp),
            )
            self.connection.commit()

    def retrieve(self, episode_guid: str, feed_name: str = None) -> dict[str, Any]:
        """Retrieve stored information for a specific episode GUID."""
        episode: dict[str, Any] = {}
        if feed_name:
            result: Cursor = self.connection.execute(
                "SELECT guid, processed FROM episodes WHERE guid = ? AND podcast_name = ? LIMIT 1",
                (episode_guid, feed_name),
            )
            episode["guid"], episode["processed"] = result.fetchone()
        else:
            result: Cursor = self.connection.execute(
                "SELECT guid, processed FROM episodes WHERE guid = ? LIMIT 1",
                (episode_guid,),
            )
            episode["guid"], episode["processed"] = result.fetchone()

        return episode

    def retrieve_enclosure_urls(self, feed_name: str = None) -> list[str]:
        """Retrieve all episode enclosure URLs from the feed database."""
        urls: list[str] = []
        if feed_name:
            for url in self.connection.execute(
                "SELECT DISTINCT enclosure_url FROM episodes WHERE enclosure_url "
                "IS NOT NULL AND podcast_name = ?",
                (feed_name,),
            ):
                urls.append(url[0])
        else:
            for url in self.connection.execute(
                "SELECT DISTINCT enclosure_url FROM episodes WHERE enclosure_url IS NOT NULL"
            ):
                urls.append(url[0])

        return urls

    def retrieve_guids(self, feed_name: str = None) -> list[str]:
        """Retrieve all episode GUIDs from the feed database."""
        guids: list[str] = []
        if feed_name:
            for guid in self.connection.execute(
                "SELECT DISTINCT guid FROM episodes WHERE guid IS NOT NULL AND podcast_name = ?",
                (feed_name,),
            ):
                guids.append(guid[0])
        else:
            for guid in self.connection.execute(
                "SELECT DISTINCT guid FROM episodes WHERE guid IS NOT NULL"
            ):
                guids.append(guid[0])

        return guids

    def clean(self, days_to_keep: int = 90) -> None:
        """Remove old episode entries from the database."""
        datetime_filter: datetime = datetime.now() - timedelta(days=days_to_keep)
        self.connection.execute("DELETE FROM episodes WHERE processed <= ?", (datetime_filter,))
        self.connection.commit()
