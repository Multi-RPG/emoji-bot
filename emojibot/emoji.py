#!/usr/bin/python3
from dataclasses import dataclass
from typing import List, Dict


@dataclass
class Emoji:
    """Emoji class"""
    def __init__(self) -> None:
        self.emoji_list: Dict[int, List[str]] = {}

    # TODO: add __iter__ so it's easy to iterate this.
    def add(self, emoji_id: int, name: str, full_name: str) -> None:
        temp_list: List[str] = [name, full_name]
        self.emoji_list.update({emoji_id: temp_list})
