#!/usr/bin/python3
import configparser
import sys
import re
import logging
import discord
# import time

from discord.ext import commands
from pathlib import Path

from init_logging import init_logging

from emojibot.constants import EXTENSIONS
from emojibot.constants import EMO

from emojibot.utility import parse_id
from emojibot.utility import parse_emoji
from emojibot.utility import load_emoji_database

from emojibot.database import Database

# initialize logging
# TODO: add arg parser
# change to logging.DEBUG during debug
level = logging.INFO
log = init_logging("emobot", level)

# Token Configuration
config = configparser.ConfigParser()
token_path = Path("configs/token.ini")

try:
    config.read(token_path)
    TOKEN = config.get("TOKEN", "token")
except IOError:
    log.error("An error occured trying to read the file.")
    sys.exit()

# Bot command prefix
client = commands.Bot(command_prefix=["e!"])
client.remove_command("help")

log.info("Connecting...")


@client.event
async def on_ready():
    log.info(f"{client.user.name} has connected to Discord!")

    for guild in client.guilds:
        log.info(f"connected to [ {guild.name} - id: {guild.id} ]")

    log.info(f"{len(client.guilds)} servers")

    log.info("Loading server emojis...")
    for emoji in client.emojis:
        EMO.add(emoji.id, emoji.name, emoji)
    assert len(EMO.emoji_list) > 0, "Empty emojis, didn't load emojis"

    # load emoji database if necessary.
    load_emoji_database(EMO)

    # TODO:
    # load users into the USER_LIST cache.

    log.info(f"{len(EMO.emoji_list)} emojis")
    log.info("Done loading emojis!")

    pog_du = discord.Game(name="e!help for commands")
    await client.change_presence(activity=pog_du)


@client.listen()
async def on_message(message):
    emoji_user = message.author

    # check if bot
    if emoji_user == client.user:
        return

    # TODO:
    # user_id = emoji_user.id

    msg = message.content
    log.debug(f"user: {emoji_user}, message content: {msg}")

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
            log.debug(f"{em}")
            emoji_id = parse_id(em)
            if emoji_id in EMO.emoji_list:
                emojis_id.append(emoji_id)

        # convert list into set to remove duplicates
        emojis_id = set(emojis_id)

        # update the emojis
        database = Database()
        database.connect()
        for emo_id in emojis_id:
            # bump the emoji count
            # bump the emoji count in the user dictionary
            log.debug(f"emoji with {emo_id} updated.")
            database.execute_update_emoji(emo_id)


if __name__ == "__main__":
    for extension in EXTENSIONS:
        try:
            client.load_extension(extension)

        except Exception as e:
            exc = f"{type(e).__name__}: {e}"
            log.error(f"Failed to load extension {extension}\n {exc}")

    client.run(TOKEN)
