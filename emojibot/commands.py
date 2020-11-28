from dataclasses import dataclass
from discord.ext import commands

from emojibot.utility import parse_id
from emojibot.utility import is_in_emoji_list

from emojibot.database import Database


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
        await ctx.send("hello")

    """ Count command

        The count command works with one arg.
        If it's passed more than 1 args, it will just ignore the rest.

        e.g.
        e!count emoji_name
    """

    @commands.cooldown(1, 1, commands.BucketType.user)
    @commands.command(
        name="count",
        description="prints the total count for an emoji or top 10",
        aliases=["c", "C", "COUNT"],
    )
    async def count_method(self, ctx, *arg):
        if arg:
            emoji = arg[0]
            emoji_id = parse_id(arg[0])
            # TODO: add logging
            print(emoji_id)
            if is_in_emoji_list(emoji_id):
                database = Database()
                database.connect()
                result = database.execute_select(emoji_id)
                await ctx.send(f"{emoji} has been used {result} time(s).")
        else:
            await ctx.send(
                "Please enter the emoji you want to check. "
                "e.g. `e!count emoji_name`"
            )


def setup(client):
    client.add_cog(Commands(client))
