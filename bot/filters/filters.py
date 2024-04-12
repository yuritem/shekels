import re
from typing import get_args
from aiogram.filters import BaseFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot.db.models import AliasableSubtype
from bot.states import TransactionStates


class NameFilter(BaseFilter):
    r"""Matches a word consisting of symbols matching [a-zA-Z0-9_\-.]"""
    phrase_pattern = re.compile(r"^[\w\-.']{1,40}$")

    async def __call__(self, message: Message) -> bool:
        return (re.fullmatch(self.phrase_pattern, message.text) is not None) and (len(message.text) <= 40)


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


class PeriodicityFilter(BaseFilter):
    periodicity_pattern = re.compile(r"(\d+)([dwmy])")
    map = {
        'd': 'day',
        'w': 'week',
        'm': 'month',
        'y': 'year'
    }

    async def __call__(self, message: Message) -> bool:
        return re.fullmatch(self.periodicity_pattern, message.text) is not None


class IntegerFilter(BaseFilter):
    number_pattern = r"\d+"

    async def __call__(self, message: Message) -> bool:
        return re.fullmatch(self.number_pattern, message.text) is not None


class DayOfTheMonthFilter(IntegerFilter):

    async def __call__(self, message: Message) -> bool:
        match = re.fullmatch(self.number_pattern, message.text)
        if match:
            num = int(match.group())
            if num in range(1, 32):
                return True
        return False


class FloatFilter(BaseFilter):
    number_pattern = r"[+-]?\d+(?:\.\d*)?"

    async def __call__(self, message: Message) -> bool:
        return re.fullmatch(self.number_pattern, message.text) is not None


class DateTimeFilter(BaseFilter):
    datetime_pattern = r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}"

    async def __call__(self, message: Message) -> bool:
        return re.fullmatch(self.datetime_pattern, message.text) is not None


class AliasableSubtypeFilter(BaseFilter):
    allowed = get_args(AliasableSubtype)

    async def __call__(self, message: Message) -> bool:
        return message.text.lower() in self.allowed


class TransactionFilter(BaseFilter):
    transaction_pattern = re.compile(
        r"([+-]?\d+(?:\.\d{,2})?)"  # amount (required)
        r"(?:/(\d+))?"  # months for installment payments (optional)
        r"(?:\s+([\w\-.]+))?"  # currency (optional)
        r"(?:\s+([\w\-.]+))?"  # storage 1 (optional)
        r"(?:\s+([\w\-.]+))?"  # storage 2 (optional) / category (optional)
    )

    async def __call__(self, message: Message) -> bool:
        return re.fullmatch(self.transaction_pattern, message.text) is not None


class NotWaitingForTransactionFilter(BaseFilter):

    async def __call__(self, message: Message, state: FSMContext):
        state_ = await state.get_state()
        return state_ != TransactionStates.waiting_for_new_transaction
