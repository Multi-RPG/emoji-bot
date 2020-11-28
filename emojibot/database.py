#!/usr/bin/env python3
import sqlite3
import logging

from sqlite3 import Error
from dataclasses import dataclass

from emojibot.constants import Query

log = logging.getLogger("emobot")


@dataclass
class Database:
    data_file: str = r"data\emojis_data.sqlite3"

    def connect(self):
        try:
            self.connection = sqlite3.connect(self.data_file)
            self.connection.execute("PRAGMA foreign_keys = ON")
            return self.connection
        except Error as e:
            log.error(e)

    def execute_insert(self, *args):
        cur = self.connection.cursor()
        cur.execute(Query.insert_new_emoji, (args[0], args[1]))
        self.connection.commit()

    def execute_exist(self, arg) -> bool:
        cur = self.connection.cursor()
        cur.execute(Query.emoji_exists, (arg,))
        row = cur.fetchone()
        # log.debug(f"execute_exist result: {row[0]}")
        return row[0] == 1

    def execute_update_emoji(self, arg):
        cur = self.connection.cursor()
        cur.execute(Query.update_emoji_count, (arg,))
        self.connection.commit()

    def execute_select(self, arg):
        cur = self.connection.cursor()
        cur.execute(Query.select_emoji_count, (arg,))
        row = cur.fetchone()
        log.debug(f"execute_select result: {row[0]}")
        return row[0]

    def execute_select_leaderboard(self, arg):
        cur = self.connection.cursor()
        cur.execute(Query.select_leaderboard, (arg,))
        rows = cur.fetchall()
        log.debug(f"execute_select_top result {len(rows)}")
        assert len(rows) == arg
        return rows
