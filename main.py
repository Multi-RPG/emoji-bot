#!/usr/bin/python3
import configparser
import sys
import re
# import sqlite3
# import time

from discord.ext import commands
from pathlib import Path

from emojibot.emoji import Emoji
from emojibot.constants import EMOJI_PATTERN
from emojibot.constants import EMOJI_ID_PATTERN
from emojibot.constants import EXTENSIONS
from emojibot.database import Database

# Token Configuration
config = configparser.ConfigParser()
token_path = Path("configs/token.ini")

try:
    config.read(token_path)
    TOKEN = config.get("TOKEN", "token")
except IOError:
    print("An error occured trying to read the file.")
    sys.exit()

# Bot command prefix
client = commands.Bot(command_prefix=["!emo"])
client.remove_command("help")


def load_emoji_database(emoji_list):
    database = Database()
    database.connect()

    for emoji_obj in emoji_list:
        if database.execute_exist(emoji_obj.get_id()):
            continue
        database.execute_insert(emoji_obj.get_id(), emoji_obj.get_name())


# List of Emoji object
EMOJI_LIST = list()
USER_LIST = list()

# List of emoji ids for fast check
EMOJI_LIST_ID = list()

print("Connecting...")


@client.event
async def on_ready():
    print(f"{client.user.name} has connected to Discord!")

    for guild in client.guilds:
        print(f"connected to [ {guild.name} - id: {guild.id} ]")

    print(f"{len(client.guilds)} servers")

    print("Loading server emojis...")
    for emoji in client.emojis:
        emo = Emoji(emoji.id, emoji.name, emoji)
        EMOJI_LIST.append(emo)
        EMOJI_LIST_ID.append(emoji.id)
    assert len(EMOJI_LIST) > 0, "Empty emojis, didn't load emojis"
    assert len(EMOJI_LIST) == len(EMOJI_LIST_ID), ""

    # load emoji database if necessary.
    load_emoji_database(EMOJI_LIST)

    # load users into the USER_LIST cache.

    print(f"{len(EMOJI_LIST)} emojis")
    print("Done loading emojis!")


@client.listen()
async def on_message(message):
    emoji_user = message.author

    # check it's a msg sent by the bot
    if emoji_user == client.user:
        return

    # TODO:
    # check if user is in the database, creates a new user if not.
    # user_id = emoji_user.id

    msg = message.content
    # print(f"user: {emoji_user}, user_id: {user_id}, message content: {msg}")

    # TODO: Change this for new commands.
    # We don't want to increment emojis used in commands.
    # e.g. !count :pepega:
    #
    # OLD: Don't increment emoji if it's used with &query or &q command
    if re.match(r"(?:^&)q(?:uery)?", msg):
        return

    # Grab all emojis from the msg (message.content)
    emojis_list = re.findall(EMOJI_PATTERN, msg)

    # check if emoji_list is empty, if so, no emoji was sent
    if len(emojis_list) == 0:
        return
    else:
        # a list holding the emojis_id from the emojis in the msg.
        emojis_id = list()

        # takes the id from the emojis in the msg.
        def parse_id(emoji) -> int:
            e_id = EMOJI_ID_PATTERN.search(emoji)
            return int(e_id.group())

        # check if is usable emoji.
        for em in emojis_list:
            emoji_id = parse_id(em)
            if emoji_id in EMOJI_LIST_ID:
                print(emoji_id)
                emojis_id.append(emoji_id)

        # update the emojis
        database = Database()
        database.connect()
        for emo_id in emojis_id:
            # Desired behavior:
            # bump the emoji count
            # bump the emoji count in the user dictionary
            # emo.update_emoji(emoji)
            database.execute_update_emoji(emo_id)


if __name__ == "__main__":
    for extension in EXTENSIONS:
        try:
            client.load_extension(extension)

        except Exception as e:
            exc = f"{type(e).__name__}: {e}"
            print(f"Failed to load extension {extension}\n {exc}")

    client.run(TOKEN)
