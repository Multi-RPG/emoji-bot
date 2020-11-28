#!/usr/bin/python3
import re
from typing import NamedTuple

EMOJI_PATTERN = re.compile(
    r"(?:<){1}(?:a)?\:(?:[0-9a-zA-Z_])+\:(?:[0-9])+(?:>){1}"
)

# To compare parsed emojis to emojis in the server(s)
EMOJI_NAME_PATTERN = re.compile(r"(?:<?)(?::?)(?:[0-9]?)(?:>?)")

# Matches the id of an emoji
EMOJI_ID_PATTERN = re.compile(r"(?:[0-9]){18}")

# To load extensions
EXTENSIONS = [
    "emojibot.commands",
]

SERVERS = [
    617033777465655333,
    347951756313100292,
    491343421055827989,
    583498997969190922,
    589939049196945409,
    612373729800093775,
    618867007642796042,
    626536810473979918,
    667510421866938396,
    679822025711288374,
    681231353760710701,
    714295282715852870,
    756534162965528599,
    762854909883318333,
    689238715503083553,
    504709641490661400,
    643661313389625344,
    608670404768169985,
    567940881928290304,
    459192201961013248,
    432292263591411722,
    471490447790047233,
    350579948903464963,
    163898327191126017,
    431285694812389406,
]


class Query(NamedTuple):
    insert_new_emoji = (
        "INSERT INTO emoji (emoji_id, name, usage_count)" "VALUES (?, ?, 0)"
    )
    update_emoji_count = (
        "UPDATE emoji SET usage_count = usage_count + 1 WHERE emoji_id = ?"
    )
    select_emoji_count = "SELECT usage_count FROM emoji WHERE emoji_id = ?"
    emoji_exists = "SELECT EXISTS (SELECT 1 FROM emoji WHERE emoji_id = ?)"
