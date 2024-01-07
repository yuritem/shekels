import re
from aiogram.filters import BaseFilter
from aiogram.types import Message


class TransactionFilter(BaseFilter):
    transaction_pattern = re.compile(r"([+-]?\d+(?:\.\d*)?)\s+(\w+)(?:\s+(\w+))?(?:\s+(\w+))?")
    # todo: Adjust pattern to support installment payments

    def __init__(self):
        pass

    async def __call__(self, message: Message) -> bool:
        return re.match(self.transaction_pattern, message.text) is not None
