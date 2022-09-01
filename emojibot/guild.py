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
        self.max_rng: int = 0

    def add(self, index: int, guild_name: str, emojis: Tuple[Emoji]):
        self.guild_list.update({index: (guild_name, emojis)}) 

    def set_range(self):
        self.max_rng = self.max_range()

    def len(self) -> int:
        return len(self.guild_list)

    def max_range(self) -> int:
        return self.len() - 1
