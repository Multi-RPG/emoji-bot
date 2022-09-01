#!/usr/bin/python3
import logging
import discord
import collections
import math
import asyncio
import random

from dataclasses import dataclass
from typing import List, Optional

from discord.ext import commands
from discord.ext import pages
from discord import option

from emojibot.utility import parse_id
from emojibot.utility import is_in_emoji_list

from emojibot.pages import Common_Pages

from emojibot.constants import EMO
from emojibot.constants import GUILD
from emojibot.constants import Color
from emojibot.constants import BOT_INVITE_LINK

from emojibot.database import Database

log = logging.getLogger("emobot")


@dataclass
class Commands(commands.Cog):
    """Commands for the bot"""
    client: commands.Bot

    def _get_guild(self, i: Optional[int] = None):
        match i:
            case int(i):
                log.debug(f"in get_guild() i = {i}")
                return GUILD.guild_list[i]
            case None:
                return random.choice(GUILD.guild_list)

    """Help command"""
    @commands.slash_command(
        name="help",
        description="Show available commands.",
    )
    async def help(self, ctx):
        msg = (
            "```/count - Show emoji usage count.\n"
            "/rank - Show top 15 emojis.\n"
            "/emojis server_id - Show emoji lists from a given server id.\n"
            "/get_server_ids - Show a list of servers and its id.\n"
            "/range - Show the min and max ids.\n"
            "/invite - Show discord link invite.```"
        )
        await ctx.respond(msg)

    """Count command"""
    @commands.slash_command(
        name="count",
        description="Show emoji usage count.",
    )
    @option("emoji", description="Enter the emoji")
    async def count(
        self,
        ctx: discord.ApplicationContext,
        emoji: str,
    ):
        """
            The count command works with one arg.
            If it's passed more than 1 args, it will just ignore the rest.

            e.g.
            e!count emoji_name
        """
        em = discord.Embed(title="", colour=Color.yellow)

        emoji_id = parse_id(emoji)
        emoji_thumb = (
            f"https://cdn.discordapp.com/emojis/{emoji_id}.png?v=1"
        )
        em.set_thumbnail(url=emoji_thumb)
        log.debug(emoji_id)

        if is_in_emoji_list(emoji_id):
            database = Database()
            database.connect()
            result = database.execute_select_usage_count(emoji_id)

            emoji_thumb = (
                f"https://cdn.discordapp.com/emojis/{emoji_id}.png?v=1"
            )

            em.add_field(
                name=f"{ctx.author.display_name}, ",
                value=f"the {emoji} has been used {result} time(s).",
                inline=True,
            )

        else:
            msg = (
                "this emoji is not in my database. "
                "<:waffleShrug:762854934822518805>"
            )
            em.add_field(
                name=f"{ctx.author.display_name}, ",
                value=msg,
                inline=True,
            )

        em.set_footer(
            text=f"Requested by {ctx.author.name}", icon_url=ctx.author.avatar
        )
        await ctx.respond(embed=em)

    @commands.slash_command(
        name="rank",
        description="Show top 15 emojis."
    )
    async def rank(self, ctx):
        database = Database()
        database.connect()

        # retrieve top 16 emojis
        rankings = database.execute_select_leaderboard(16)

        # variables for embed
        column_1 = ""
        column_2 = ""

        # set the counter to properly display rank numbers
        counter = 1

        log.debug(rankings)
        # start looping through the database results of top 16 used emojis
        for emoji_id, num_uses in rankings:
            try:
                # attempt to build the columns needed to display rankings
                if counter < 9:
                    column_1 += (
                        f"**{counter}.** {EMO.emoji_list[emoji_id][1]} \u200B \u200B \n`{num_uses} uses`\n" # noqa E501
                    )
                else:
                    column_2 += (
                        f"**{counter}.** {EMO.emoji_list[emoji_id][1]} \u200B \u200B \n`{num_uses} uses`\n" # noqa E501
                    )
            # KeyError may happen if the bot no longer 
            # has access to a certain emoji.
            except KeyError as error:
                log.error(
                    f"{type(error).__name__}! Couldn't locate emoji ID {error}"
                )
                continue

            counter += 1

        # embed the rankings
        em = discord.Embed(title="", colour=Color.yellow)
        em.add_field(name="Top 16 Emojis", value=column_1, inline=True)
        em.add_field(name="\u200B", value=column_2, inline=True)
        big_url = (
            "https://cdn.shopify.com/s/files/1/0185/5092/"
            "products/objects-0104_800x.png?v=1369543363"
        )
        em.set_thumbnail(
            url=big_url)
        em.set_footer(
            text=f"Requested by {ctx.author.name}", icon_url=ctx.author.avatar
        )
        await ctx.respond(embed=em)

    @commands.slash_command(
        name="invite",
        description="Show discord link invite.",
    )
    async def invite(self, ctx):
        em = discord.Embed(title="", colour=Color.yellow)
        em.add_field(
            name="Bot invite link",
            value=BOT_INVITE_LINK,
            inline=True,
        )
        em.set_footer(
            text=f"Requested by {ctx.author.name}", icon_url=ctx.author.avatar
        )
        await ctx.respond(embed=em)

    @commands.slash_command(
        name="emojis",
        description="Show emoji lists from a given server id. Or an emoji list from a random server.",
    )
    @option(
        "server_id",
        description="Enter the server id.",
        required=False
    )
    async def emojislist(
        self,
        ctx: discord.ApplicationContext,
        server_id: int,
    ):
        """
            Get the lists of emojis of a single server using its id.
            We can get the server's id by using the command guildlist.
        """
        if server_id:
            if server_id > GUILD.max_rng:
                await ctx.respond("`server_id` out of range.")
                return

        guild = self._get_guild(server_id)
        guild_name = guild[0]
        guild_emoji_list = guild[1]

        header = f"{guild_name}'s Emojis.\n"

        chunk_size = 25
        embed_list: List[discord.Embed] = []

        # TODO: how to make this better? avoid 2 loops.
        for i in range(0, len(guild_emoji_list), chunk_size):
            page_em = discord.Embed(title="", colour=Color.yellow)
            temp_str: str = ""
            for emoji in guild_emoji_list[i:i+chunk_size]:
                temp_str += str(emoji)
            page_em.add_field(name=header, value=temp_str)
            page_em.set_footer(
                text=f"Requested by {ctx.author.name}", icon_url=ctx.author.avatar
            )
            embed_list.append(page_em)

        emoji_pages = Common_Pages(embed_list)

        # TODO: delete message after timeout.
        paginator = pages.Paginator(
            pages=emoji_pages.pages,
            show_disabled=True,
            show_indicator=True,
            use_default_buttons=False,
            custom_buttons=emoji_pages.page_buttons,
            loop_pages=True,
            timeout=300.0,
        )
        await paginator.respond(ctx.interaction, ephemeral=False)

    @commands.slash_command(
        name="get_server_ids",
        description="Show a list of servers and its id.",
    )
    async def get_guild_emojis_list(self, ctx):
        chunk_size = 8
        embed_list: List[discord.Embed] = []

        # TODO: two loops. monkaD!
        for i in range(0, len(GUILD.guild_list.items()), chunk_size):
            page_em = discord.Embed(title="", colour=Color.yellow)
            temp_str: str = ""
            for idx in range(i,i+chunk_size):
                guild_tpl = GUILD.guild_list.get(idx)
                if guild_tpl is None:
                    break
                temp_str += (
                    f"**{idx}**: **{guild_tpl[0]}** \u200B \u200B \n")
            page_em.add_field(name="Server IDs", value=temp_str, inline=True)
            page_em.set_footer(
                text=f"Requested by {ctx.author.name}", icon_url=ctx.author.avatar
            )
            embed_list.append(page_em)

        guild_pages = Common_Pages(embed_list)

        # TODO: delete message after timeout.
        paginator = pages.Paginator(
            pages=guild_pages.pages,
            show_disabled=True,
            show_indicator=True,
            use_default_buttons=False,
            custom_buttons=guild_pages.page_buttons,
            loop_pages=True,
            timeout=300.0,
        )
        await paginator.respond(ctx.interaction, ephemeral=False)

    @commands.slash_command(
        name="range",
        description="Show the min and max ids.",
    )
    async def guildlist(self, ctx):
        await ctx.respond(f"```Server list's IDs range: 0 to {GUILD.max_rng}```")


def setup(client):
    client.add_cog(Commands(client))
