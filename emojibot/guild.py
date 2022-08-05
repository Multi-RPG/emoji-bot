#!/usr/bin/python3
from dataclasses import dataclass
from typing import List, Dict, Tuple

from discord import Emoji


@dataclass
class Guild:
    """Guild class aka Server"""
    def __init__(self) -> None:
        # {index, (name, (emojis...))}
        self.guild_list: Dict[int, Tuple[str, Tuple[Emoji]]] = {}

    def add(self, index: int, guild_name: str, emojis: Tuple[Emoji]):
        self.guild_list.update({index: (guild_name, emojis)}) 
