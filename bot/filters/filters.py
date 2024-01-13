import re
from typing import get_args
from aiogram.filters import BaseFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot.db.models import AliasableSubtype
from bot.states import TransactionStates


class LongNameFilter(BaseFilter):
    r"""Matches one or several words (consisting of symbols matching [a-zA-Z0-9_\-.]) separated by whitespace"""
    phrase_pattern = re.compile(r"^\w[\w\-.]+(?:\s+\w[\w\-.]+)*")

    async def __call__(self, message: Message) -> bool:
        return (re.fullmatch(self.phrase_pattern, message.text) is not None) and (len(message.text) <= 40)


class ShortNameFilter(BaseFilter):
    word_pattern = re.compile(r"\w+")

    async def __call__(self, message: Message) -> bool:
        return (re.fullmatch(self.word_pattern, message.text) is not None) and (len(message.text) <= 10)


class YesNoFilter(BaseFilter):
    map = {
        'yes': True,
        'no': False,
        'y': True,
        'n': False,
        'да': True,
        'нет': False,
        '+': True,
        '-': False
    }

    async def __call__(self, message: Message) -> bool:
        return message.text.lower() in self.map


class NumberFilter(BaseFilter):
    number_pattern = r"\d+"

    async def __call__(self, message: Message) -> bool:
        return re.fullmatch(self.number_pattern, message.text) is not None


class DayOfTheMonthFilter(NumberFilter):

    async def __call__(self, message: Message) -> bool:
        match = re.fullmatch(self.number_pattern, message.text)
        if match:
            num = int(match.group())
            if num in range(1, 32):
                return True
        return False


class AliasableSubtypeFilter:
    allowed = get_args(AliasableSubtype)

    async def __call__(self, message: Message) -> bool:
        return message.text.lower() in self.allowed


class TransactionFilter(BaseFilter):
    transaction_pattern = re.compile(r"([+-]?\d+(?:\.\d*)?)\s+(\w+)(?:\s+(\w+))?(?:\s+(\w+))?")
    # todo: Adjust pattern to support installment payments

    def __init__(self):
        pass

    async def __call__(self, message: Message) -> bool:
        return re.fullmatch(self.transaction_pattern, message.text) is not None


class NotWaitingForTransactionFilter(BaseFilter):

    async def __call__(self, message: Message, state: FSMContext):
        state_ = await state.get_state()
        return state_ != TransactionStates.waiting_for_new_transaction
