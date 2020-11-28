#!/usr/bin/python3
import configparser
import sys
import re
# import time

from discord.ext import commands
from pathlib import Path

from emojibot.constants import EXTENSIONS
from emojibot.constants import EMOJI_LIST
from emojibot.constants import EMOJI_LIST_ID

from emojibot.utility import parse_id
from emojibot.utility import parse_emoji
from emojibot.utility import load_emoji_database

from emojibot.database import Database
from emojibot.emoji import Emoji

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
client = commands.Bot(command_prefix=["e!"])
client.remove_command("help")


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

    # TODO:
    # load users into the USER_LIST cache.

    print(f"{len(EMOJI_LIST)} emojis")
    print("Done loading emojis!")


@client.listen()
async def on_message(message):
    emoji_user = message.author

    # check if bot
    if emoji_user == client.user:
        return

    # TODO:
    # user_id = emoji_user.id

    msg = message.content
    # print(f"user: {emoji_user}, user_id: {user_id}, message content: {msg}")

    # if msg starts with !e, ignore.
    if re.match(r"(?:^e!)", msg):
        return

    # Grab all emojis from the msg (message.content)
    emojis_list = parse_emoji(msg)

    # check if emoji_list is empty, if so, no emoji was sent
    if len(emojis_list) == 0:
        return
    else:
        # a list holding the emojis_id from the emojis in the msg.
        emojis_id = list()

        # check if is usable emoji.
        for em in emojis_list:
            emoji_id = parse_id(em)
            if emoji_id in EMOJI_LIST_ID:
                emojis_id.append(emoji_id)

        # update the emojis
        database = Database()
        database.connect()
        for emo_id in emojis_id:
            # bump the emoji count
            # bump the emoji count in the user dictionary
            database.execute_update_emoji(emo_id)


if __name__ == "__main__":
    for extension in EXTENSIONS:
        try:
            client.load_extension(extension)

        except Exception as e:
            exc = f"{type(e).__name__}: {e}"
            print(f"Failed to load extension {extension}\n {exc}")

    client.run(TOKEN)
