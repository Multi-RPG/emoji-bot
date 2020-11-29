#!/usr/bin/python3
import re
from typing import NamedTuple

from emojibot.emoji import Emoji

# Emoji list object
EMO = Emoji()

EMOJI_PATTERN = re.compile(
    r"(?:<){1}(?:a)?\:(?:[0-9a-zA-Z_])+\:(?:[0-9])+(?:>){1}"
)

# To compare parsed emojis to emojis in the server(s)
EMOJI_NAME_PATTERN = re.compile(r"(?:<?)(?::?)(?:[0-9]?)(?:>?)")

# Matches the id of an emoji
EMOJI_ID_PATTERN = re.compile(r"(?:[0-9]){18}")

# extensions for bot to load in cog
EXTENSIONS = [
    "emojibot.commands",
]


class Query(NamedTuple):
    insert_new_emoji = (
        "INSERT INTO emoji (emoji_id, name, usage_count)" "VALUES (?, ?, 0)"
    )
    delete_emoji = (
        "DELETE FROM emoji WHERE emoji_id = ?"
    )
    update_emoji_count = (
        "UPDATE emoji SET usage_count = usage_count + 1 WHERE emoji_id = ?"
    )
    select_emoji_count = "SELECT usage_count FROM emoji WHERE emoji_id = ?"
    emoji_exists = "SELECT EXISTS (SELECT 1 FROM emoji WHERE emoji_id = ?)"
    select_leaderboard = (
        "SELECT emoji_id, usage_count FROM emoji "
        "ORDER BY usage_count DESC LIMIT ?"
    )


class Color(NamedTuple):
    yellow = 0xfdd14b
