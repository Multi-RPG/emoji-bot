#!/usr/bin/env python3
import logging

from typing import List, Tuple

from emojibot.constants import EMOJI_PATTERN
from emojibot.constants import EMOJI_NAME_PATTERN
from emojibot.constants import EMOJI_ID_PATTERN
from emojibot.constants import EMO
from emojibot.constants import Emoji

from emojibot.database import Database

log = logging.getLogger("emobot")


def parse_id(emoji: str) -> int:
    e_id = EMOJI_ID_PATTERN.search(emoji)
    return int(e_id.group())


def parse_name(emoji: str) -> str:
    e_name = EMOJI_NAME_PATTERN.search(emoji)
    return (str(e_name.group())).replace(':', '').lower()


def parse_emoji(msg: str) -> List[str]:
    emojis_list = EMOJI_PATTERN.findall(msg)
    return emojis_list


def is_in_emoji_list(emoji: int) -> bool:
    return emoji in EMO.emoji_list


def load_emoji_database(emo: Emoji) -> None:
    log.debug("checking for new emojis...")
    database = Database()
    database.connect()

    # reset all emojis to inactive
    log.debug("executing reset active emojis...")
    database.execute_reset_active_emojis()

    # a list of tuple containing the emoji_id and the emoji's name.
    contents: List[Tuple[int, str]] = []
    for emoji_id, name in emo.emoji_list.items():
        database.execute_set_emoji_active(emoji_id)
        if database.execute_id_exist(emoji_id):
            continue
        contents.append((emoji_id, name[0]))

    # do insert in bulk
    log.debug("inserting new emojis...")
    database.execute_insert(contents)
    log.debug("done inserting...")

    log.debug("setting active emojis...")
    for emoji_id in emo.emoji_list.keys():
        database.execute_set_emoji_active(emoji_id)

    log.debug("deleting inactive emojis...")
    # delete all inactive emojis from database
    database.execute_delete_inactive_emojis()
    log.debug("done!")
