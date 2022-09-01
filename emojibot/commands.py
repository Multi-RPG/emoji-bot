#!/usr/bin/python3
import logging
import discord
import collections
import math
import asyncio

from dataclasses import dataclass
from typing import List

from discord.ext import commands
from discord.ext import pages
from discord import option

from emojibot.utility import parse_id
from emojibot.utility import is_in_emoji_list

from emojibot.pages import Emoji_Pages

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

    """Help command"""
    @commands.slash_command(
        name="help",
        description="Show available commands.",
    )
    async def help(self, ctx):
        msg = (
            "```/count - Show emoji usage count.\n"
            "/rank - Show top 15 emojis.\n"
            "/emojis id - Show emoji lists from a given guild id.\n"
            " Alternatively, you can enter -1 if you want to get a random list"
            " of emojis.\n"
            "/guilds_ids - Show a list of guilds and its id.\n"
            "/range - Show the range of ids users can choose.\n"
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
        author = ctx.author
        author_avatar = (
            f"https://cdn.discordapp.com/avatars/"
            f"{author.id}/{author.avatar}.webp?size=64"
        )

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
                name=f"{author.display_name}, ",
                value=f"the {emoji} has been used {result} time(s).",
                inline=True,
            )

        else:
            msg = (
                "this emoji is not in my database. "
                "<:waffleShrug:762854934822518805>"
            )
            em.add_field(
                name=f"{author.display_name}, ",
                value=msg,
                inline=True,
            )

        em.set_footer(
            text=f"Requested by {author.name}", icon_url=author_avatar
        )
        await ctx.respond(embed=em)

    @commands.slash_command(
        name="rank",
        description="Show top 15 emojis."
    )
    async def rank(self, ctx):
        database = Database()
        database.connect()

        author = ctx.author
        author_avatar = (
            f"https://cdn.discordapp.com/avatars/"
            f"{author.id}/{author.avatar}.webp?size=64"
        )

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
            text=f"Requested by {author.name}", icon_url=author_avatar
        )
        await ctx.respond(embed=em)

    @commands.slash_command(
        name="invite",
        description="Show discord link invite.",
    )
    async def invite(self, ctx):
        author = ctx.author
        author_avatar = (
            f"https://cdn.discordapp.com/avatars/"
            f"{author.id}/{author.avatar}.webp?size=64"
        )

        em = discord.Embed(title="", colour=Color.yellow)
        em.add_field(
            name="Bot invite link",
            value=BOT_INVITE_LINK,
            inline=True,
        )
        em.set_footer(
            text=f"Requested by {author.name}", icon_url=author_avatar
        )
        await ctx.respond(embed=em)

    @commands.slash_command(
        name="emojis",
        description="Show emoji lists from a given guild id.",
    )
    @option(
        "guild_id",
        description="Enter the guild id.",
    )
    async def emojislist(
        self,
        ctx: discord.ApplicationContext,
        guild_id: int,
    ):
        """
            Get the lists of emojis of a single server using its id.
            We can get the server's id by using the command guildlist.
        """

        if guild_id > GUILD.max_rng:
            await ctx.respond("`guild_id` out of range.")

        else:
            author = ctx.author
            author_avatar = (
                f"https://cdn.discordapp.com/avatars/"
                f"{author.id}/{author.avatar}.webp?size=64"
            )

            guild = GUILD.guild_list[guild_id]
            guild_name = guild[0]
            guild_emoji_list = guild[1]

            header = f"{guild_name}'s Emojis.\n"

            chunk_size = 25
            chunked_list: List[discord.Embed] = []

            # TODO: how to make this better? avoid 2 loops.
            for i in range(0, len(guild_emoji_list), chunk_size):
                page_em = discord.Embed(title="", colour=Color.yellow)
                temp_str: str = ""
                for emoji in guild_emoji_list[i:i+chunk_size]:
                    temp_str += str(emoji)
                page_em.add_field(name=header, value=temp_str)
                page_em.set_footer(
                    text=f"Requested by {author.name}", icon_url=author_avatar
                )
                chunked_list.append(page_em)

            emoji_pages = Emoji_Pages(chunked_list)

            # TODO: add timeout and delete message after it.
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

    # TODO: add pages
    @commands.slash_command(
        name="guilds_ids",
        description="Show a list of guilds and its id.",
    )
    async def get_guild_emojis_list(self, ctx):
        author = ctx.author
        author_avatar = (
            f"https://cdn.discordapp.com/avatars/"
            f"{author.id}/{author.avatar}.webp?size=64"
        )

        # Emojis used for reaction
        Emoji_Reaction = collections.namedtuple(
            "Emoji_Reaction", ["Left", "Right"]
        )
        emoji = Emoji_Reaction("⬅️", "➡️")

        number_of_guilds = len(GUILD.guild_list)
        log.debug(f"number of guilds: {number_of_guilds}")


        em = discord.Embed(title="", colour=Color.yellow)
        em.set_footer(
            text=f"Requested by {author.name}", icon_url=author_avatar
        )

        counter = 1;
        if number_of_guilds <= 8:
            # one column is enough
            column_1 = ""
            for guild_id, guild_name in GUILD.guild_list.items():
                column_1 += (
                    f"**{guild_id}**: **{guild_name[0]}** \u200B \u200B \n")

            em.add_field(name="Server IDs", value=column_1, inline=True)
            await ctx.respond(embed=em)

        elif number_of_guilds > 8 and number_of_guilds <= 16:
            column_1 = ""
            column_2 = ""
            for guild_id, guild_name in GUILD.guild_list.items():
                if counter < 9:
                    column_1 += (
                        f"**{guild_id}**: **{guild_name[0]}** \u200B \u200B \n")
                else:
                    column_2 += (
                        f"**{guild_id}**: **{guild_name[0]}** \u200B \u200B \n")
                counter += 1

            em.add_field(name="Server IDs", value=column_1, inline=True)
            em.add_field(name="\u200B", value=column_2, inline=True)
            await ctx.respond(embed=em)

        elif number_of_guilds > 16:
            column_1 = ""
            column_2 = ""

            total_pages = int(math.ceil(number_of_guilds) / 16.0)

            guild_lists = [(i, name) for guild_id, guild_name in GUILD.guild_list.items]
            counter = 1
            for i, name in guild_lists[stride : stride + 15]:
                if counter < 9:
                    column_1 += (
                        f"**{i}**: **{name[0]}** \u200B \u200B \n")
                else:
                    column_2 += (
                        f"**{i}**: **{name[0]}** \u200B \u200B \n")
                counter += 1

            em.add_field(name="Server IDs", value=column_1, inline=True)
            em.add_field(name="\u200B", value=column_2, inline=True)
            msg = await ctx.respond(embed=em)
            await msg.add_reaction(emoji=emoji.Right)

            def is_author(reaction, user):
                return user == author and str(reaction.emoji) in emoji

            reaction, user = await self.client.wait_for(
                "reaction_add",
                check=is_author,
                timeout=30)

            stride = 15
            current_page = 1
            while reaction:
                await msg.delete()

                counter = 1
                column_1 = ""
                column_2 = ""

                em.clear_fields()
                if str(reaction) == emoji.Right:
                    current_page += 1
                    for i, name in guild_lists[stride : stride + 15]:
                        if counter < 9:
                            column_1 += (
                                f"**{i}**: **{name[0]}** \u200B \u200B \n")
                        else:
                            column_2 += (
                                f"**{i}**: **{name[0]}** \u200B \u200B \n")
                        counter += 1

                    em.add_field(name="Server IDs", value=column_1, inline=True)
                    em.add_field(name="\u200B", value=column_2, inline=True)
                    msg = await ctx.respond(embed=em)
                    await msg.add_reaction(emoji_emoji.Left)
                    stride += 15
                    if not current_page == total_pages:
                        await msg.add_reaction(emoji=emoji.Right)

                elif str(reaction) == emoji.Left:
                    current_page -= 1
                    for i, name in guild_lists[stride - 15 : stride]:
                        if counter < 9:
                            column_1 += (
                                f"**{i}**: **{name[0]}** \u200B \u200B \n")
                        else:
                            column_2 += (
                                f"**{i}**: **{name[0]}** \u200B \u200B \n")
                        counter += 1

                    em.add_field(name="Server IDs", value=column_1, inline=True)
                    em.add_field(name="\u200B", value=column_2, inline=True)
                    msg = await ctx.respond(embed=em)
                    stride -= 15
                    if not current_page == 1:
                        await msg.add_reaction(emoji=emoji.Left)
                    await msg.add_reaction(emoji_emoji.Right)

                reaction, user = await self.client.wait_for(
                    "reaction_add",
                    check=is_author,
                    timeout=30)

            await asyncio.sleep(30)
            await msg.delete()


    @commands.slash_command(
        name="range",
        description="Show the range of ids users can choose.",
    )
    async def guildlist(self, ctx):
        await ctx.respond(f"```Guild list's IDs range: 0 to {GUILD.max_rng}```")


def setup(client):
    client.add_cog(Commands(client))
