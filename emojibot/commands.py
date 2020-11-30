#!/usr/bin/python3
import logging
import discord

from dataclasses import dataclass
from discord.ext import commands

from emojibot.utility import parse_id
from emojibot.utility import is_in_emoji_list

from emojibot.constants import EMO
from emojibot.constants import Color

from emojibot.database import Database

from num2words import num2words

log = logging.getLogger("emobot")


@dataclass
class Commands(commands.Cog):
    """Commands for the bot"""

    client: commands.Bot

    """Help command"""
    @commands.command(
        name="help",
        description="command information",
        brief="commands",
        aliases=["h", "H", "HELP"],
    )
    async def helper(self, ctx):
        msg = (
            "```e!count emoji - the total number of uses\n"
            "e!rank - top 15 emojis```"
        )
        await ctx.send(msg)

    """Count command"""
    @commands.cooldown(1, 1, commands.BucketType.user)
    @commands.command(
        name="count",
        description="prints the total count for an emoji or top 10",
        aliases=["c", "C", "COUNT"],
    )
    async def count_method(self, ctx, *arg):
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

        if arg:
            emoji = arg[0]
            emoji_id = parse_id(arg[0])
            emoji_thumb = (
                f"https://cdn.discordapp.com/emojis/{emoji_id}.png?v=1"
            )
            em.set_thumbnail(url=emoji_thumb)
            log.debug(emoji_id)

            if is_in_emoji_list(emoji_id):
                database = Database()
                database.connect()
                result = database.execute_select(emoji_id)

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
        else:
            msg = (
                "please enter the emoji you want to check. "
                "e.g. `e!count emoji`"
            )

            em.add_field(
                name=f"{author.display_name}, ",
                value=msg,
                inline=True,
            )

        em.set_footer(
            text=f"Requested by {author.name}", icon_url=author_avatar
        )
        await ctx.send(embed=em)

    @commands.cooldown(1, 1, commands.BucketType.user)
    @commands.command(
        name="ranking",
        aliases=["ranks", "leaderboards", "leaderboard", "lb", "rank"],
    )
    async def ranks(self, ctx):
        database = Database()
        database.connect()

        author = ctx.author
        author_avatar = (
            f"https://cdn.discordapp.com/avatars/"
            f"{author.id}/{author.avatar}.webp?size=64"
        )

        # retrieve top 16 emojis
        rankings = database.execute_select_leaderboard(15)

        # variables for embed
        name_field_column = ""
        count_field_column = ""

        # set the counter to properly display rank numbers
        counter = 1

        log.debug(rankings)
        # start looping through the database results of top 15 used emojis
        for emoji_id, num_uses in rankings:
            # attempt to build the first column (emoji column)
            try:
                name_field_column += (
                    f"{EMO.emoji_list[emoji_id][1]} \n"
                )
                # KeyError may happen if the bot no longer has access to a certain emoji.
            except KeyError as error:
                log.error(f"{type(error).__name__}! Couldn't locate emoji ID {error}")
                continue

            # convert the number of uses (integer) to a string
            num_uses_numbers = [int(digit) for digit in str(num_uses)]
            # prepare new string to store each word in
            num_uses_emojis = ""

            # for every integer in the string of numbers, convert it to english
            for number in num_uses_numbers:
                # put the numbers in english form (EX. 1 -> one) and put colons around them to convert to emojis
                num_uses_emojis += f":{num2words(int(number))}:"

            # now build the second column (number of uses for that emoji)
            count_field_column += f"{num_uses_emojis} \n"
            counter += 1

        # embed the rankings
        em = discord.Embed(title="", colour=Color.yellow)
        em.add_field(name="Top 15 \u200B \u200B ", value=name_field_column, inline=True)
        em.add_field(name="Uses", value=count_field_column, inline=True)
        big_url = (
            "https://cdn.shopify.com/s/files/1/0185/5092/"
            "products/objects-0104_800x.png?v=1369543363"
        )
        em.set_thumbnail(
            url=big_url)
        em.set_footer(
            text=f"Requested by {author.name}", icon_url=author_avatar
        )
        await ctx.send(embed=em)


def setup(client):
    client.add_cog(Commands(client))
