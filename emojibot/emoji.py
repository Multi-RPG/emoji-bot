#!/usr/bin/python3
from dataclasses import dataclass


@dataclass
class Emoji:
    """Emoji class"""
    def __init__(self):
        self.emoji_list = dict()

    # TODO: add __iter__ so it's easy to iterate this.
    def add(self, emoji_id, name, full_name):
        temp_list = [name, full_name]
        self.emoji_list.update({emoji_id: temp_list})

    @staticmethod
    def get_emoji_ranking():
        pass

    @staticmethod
    def get_emoji_usage(emo):
        pass

    @staticmethod
    def update_emoji(emo):
        pass
