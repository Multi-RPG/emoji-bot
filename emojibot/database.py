#!/usr/bin/env python3
import sqlite3

from sqlite3 import Error
from dataclasses import dataclass

from emojibot.constants import Query


@dataclass
class Database:
    data_file: str = r"data\emojis_data.sqlite3"

    def connect(self):
        try:
            self.connection = sqlite3.connect(self.data_file)
            self.connection.execute("PRAGMA foreign_keys = ON")
            return self.connection
        except Error as e:
            print(e)

    def execute_insert(self, *args):
        cur = self.connection.cursor()
        cur.execute(Query.insert_new_emoji, (args[0], args[1]))
        self.connection.commit()

    def execute_exist(self, arg) -> bool:
        cur = self.connection.cursor()
        cur.execute(Query.emoji_exists, (arg,))
        row = cur.fetchone()
        return row[0] == 1

    def execute_update_emoji(self, arg):
        cur = self.connection.cursor()
        cur.execute(Query.update_emoji_count, (arg,))
        self.connection.commit()
