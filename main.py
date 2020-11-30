#!/usr/bin/python3
import configparser
import sys
import re
import logging
import discord
import json
import time

from discord.ext import commands
from pathlib import Path

from init_logging import init_logging

from emojibot.constants import EXTENSIONS
from emojibot.constants import EMO

from emojibot.utility import parse_id
from emojibot.utility import parse_name
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
    log.info(f"connected to {len(client.guilds)} servers.")

    for guild in client.guilds:
        log.info(f"connected to [ {guild.name} - id: {guild.id} ]")

    log.info("Loading server emojis...")
    for emoji in client.emojis:
        EMO.add(emoji.id, emoji.name.lower(), emoji)
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
    # check if bot
    if message.author == client.user:
        return

    # TODO:
    # user_id = emoji_user.id

    msg = message.content
    log.debug(f"user: {message.author}, message content: {msg}")

    # if msg starts with !e, ignore.
    if re.match(r"(?:^e!)", msg):
        return

    # Grab all emojis from the msg (message.content)
    emojis_list = parse_emoji(msg)

    # check if emoji_list is empty, if so, no emoji was sent
    if len(emojis_list) == 0:
        return
    else:
        # if user sent an emoji less than 15s ago, exit this event.
        if await check_if_cooldown(str(message.author.id)):
            return

        # connect to database
        database = Database()
        database.connect()

        # an empty set to hold the emojis_id from the emojis in the msg.
        emoji_id_set = set()

        # iterate through the emojis found in message
        for em in emojis_list:
            log.debug(f"{em}")
            # parse the name and id from the emojis found in message
            emoji_id = parse_id(em)
            emoji_name = parse_name(em)

            # if the emoji id exists in database
            if database.execute_id_exist(emoji_id):
                # add it to our set that will be used to update counts in database
                emoji_id_set.add(emoji_id)
            # if the emoji id couldn't be found, but there's a name match in database
            elif database.execute_name_exist(emoji_name):
                # overwrite ID with the closest database match
                emoji_id = database.execute_select_id(emoji_name)
                # add it to our set that will be used to update counts in database
                emoji_id_set.add(emoji_id)

        # update the emoji usage counts by 1 in database for each unique emoji found
        for emoji_id in emoji_id_set:
            log.debug(f"emoji with {emoji_id} updated.")
            database.execute_update_emoji(emoji_id)


async def check_if_cooldown(user_id):
    # open file with all user's last message timestamp
    with open("data/user_data.json", "r") as f:
        user_data = json.load(f)

    # if user isn't found in file
    if user_id not in user_data:
        user_data[user_id] = 0

    # if it's been more than 30 seconds since the user's last emoji
    if time.time() - user_data[user_id] > 30:
        # set new timestamp for user's latest emoji
        user_data[user_id] = time.time()
        # dump new data into file
        with open("data/user_data.json", "w") as f:
            json.dump(user_data, f)
        return False
    # it it hasn't been enough time since the user's last emoji
    else:
        return True

if __name__ == "__main__":
    for extension in EXTENSIONS:
        try:
            client.load_extension(extension)

        except Exception as e:
            exc = f"{type(e).__name__}: {e}"
            log.error(f"Failed to load extension {extension}\n {exc}")

    client.run(TOKEN)
