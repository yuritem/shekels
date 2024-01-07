import re
from aiogram.filters import BaseFilter
from aiogram.types import Message


class LongNameFilter(BaseFilter):
    r"""Matches one or several `[a-zA-Z0-9_\-]` words separated by whitespace"""
    phrase_pattern = re.compile(r"^\w[\w\-]+(?:\s+\w[\w\-]+)*")

    async def __call__(self, message: Message) -> bool:
        return re.match(self.phrase_pattern, message.text) is not None


class AnyBooleanFilter(BaseFilter):
    str_bool = {
        '1': True,
        '0': False,
        't': True,
        'f': False,
        'yes': True,
        'no': False,
        'true': True,
        'false': False,
        'да': True,
        'нет': False
    }

    async def __call__(self, message: Message) -> bool:
        return message.text.lower() in self.str_bool


class NumberFilter(BaseFilter):
    number_pattern = r"\d+"

    async def __call__(self, message: Message) -> bool:
        return re.match(self.number_pattern, message.text) is not None
