#!/usr/bin/env python3
import logging
import discord

from typing import List, Tuple

from discord.ext.pages import PaginatorButton

log = logging.getLogger("emobot")

class Common_Buttons:
    def __init__(self):
        self.page_buttons: List[PaginatorButton] = [
            PaginatorButton(
                "first",
                label="<<-",
                style=discord.ButtonStyle.green
            ),
            PaginatorButton(
                "prev",
                label="<-",
                style=discord.ButtonStyle.green
            ),
            PaginatorButton(
                "page_indicator",
                style=discord.ButtonStyle.gray,
                disabled=True
            ),
            PaginatorButton(
                "next",
                label="->",
                style=discord.ButtonStyle.green
            ),
            PaginatorButton(
                "last",
                label="->>",
                style=discord.ButtonStyle.green
            ),
        ]


class Common_Pages(Common_Buttons):
    def __init__(self, pages: List[discord.Embed]):
        Common_Buttons.__init__(self)
        self.pages: List[discod.Embed] = pages
