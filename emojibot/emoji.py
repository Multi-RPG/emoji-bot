#!/usr/bin/python3
from dataclasses import dataclass


@dataclass
class Emoji:
    """Emoji class"""
    id: int
    name: str
    full_name: str

    def get_id(self) -> int:
        return self.id

    def get_name(self) -> str:
        return self.name

    def get_full_name(self) -> str:
        return self.full_name

    @staticmethod
    def get_emoji_ranking():
        pass

    @staticmethod
    def get_emoji_usage(emo):
        pass

    @staticmethod
    def update_emoji(emo):
        pass
