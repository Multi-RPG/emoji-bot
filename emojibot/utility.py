#!/usr/bin/env python3
from emojibot.constants import EMOJI_PATTERN
from emojibot.constants import EMOJI_ID_PATTERN
from emojibot.constants import EMOJI_LIST_ID

from emojibot.database import Database


def parse_id(emoji) -> int:
    e_id = EMOJI_ID_PATTERN.search(emoji)
    return int(e_id.group())


def parse_emoji(msg) -> list():
    emojis_list = EMOJI_PATTERN.findall(msg)
    return emojis_list


def is_in_emoji_list(emoji) -> bool:
    return emoji in EMOJI_LIST_ID


def load_emoji_database(emoji_list) -> None:
    database = Database()
    database.connect()

    for emoji_obj in emoji_list:
        if database.execute_exist(emoji_obj.get_id()):
            continue
        database.execute_insert(emoji_obj.get_id(), emoji_obj.get_name())
