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
            self.connection.execute('PRAGMA journal_mode = MEMORY')
            return self.connection
        except Error as e:
            log.error(e)

    def execute_insert(self, *args):
        cur = self.connection.cursor()
        cur.executemany(Query.insert_new_emoji, *args)
        self.connection.commit()
        log.debug(f"total rowcount {cur.rowcount}")
        cur.close()

    def execute_delete(self, arg):
        cur = self.connection.cursor()
        cur.execute(Query.delete_emoji, (arg,))
        self.connection.commit()

    def execute_id_exist(self, arg) -> bool:
        cur = self.connection.cursor()
        cur.execute(Query.emoji_id_exists, (arg,))
        row = cur.fetchone()
        # log.debug(f"execute_exist result: {row[0]}")
        return row[0] == 1

    def execute_name_exist(self, arg) -> bool:
        cur = self.connection.cursor()
        cur.execute(Query.emoji_name_exists, (arg,))
        row = cur.fetchone()
        # log.debug(f"execute_exist result: {row[0]}")
        return row[0] == 1

    def execute_set_emoji_active(self, arg):
        cur = self.connection.cursor()
        cur.execute(Query.set_emoji_active, (arg,))
        self.connection.commit()

    def execute_reset_active_emojis(self):
        cur = self.connection.cursor()
        cur.execute(Query.reset_active_emojis)
        self.connection.commit()

    def execute_delete_inactive_emojis(self):
        cur = self.connection.cursor()
        cur.execute(Query.delete_inactive_emojis)
        self.connection.commit()

    def execute_update_emoji(self, arg):
        cur = self.connection.cursor()
        cur.execute(Query.update_emoji_count, (arg,))
        self.connection.commit()

    def execute_select_usage_count(self, arg):
        cur = self.connection.cursor()
        cur.execute(Query.select_emoji_count, (arg,))
        row = cur.fetchone()
        log.debug(f"execute_select result: {row[0]}")
        return row[0]

    def execute_select_id(self, arg):
        cur = self.connection.cursor()
        cur.execute(Query.select_emoji_id, (arg,))
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
