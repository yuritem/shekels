from datetime import datetime
from typing import Iterator

from dateutil.relativedelta import relativedelta


async def split_transaction(amount_total: float, months: int) -> Iterator[tuple]:
    """
        Meant for installment payments.
        For `months` > 1 splits transaction into multiple transactions 1 month apart with `amount_total` equally
    distributed between payments and calculates each transaction's `timestamp`.
        Starting timestamp is taken as the current time calculated inside this function.
        Returns an iterator of timestamps and amounts.
    """

    # sign treated separately for proper integer division and modulo
    sign = 1 if amount_total > 0 else -1
    amount_total = abs(amount_total)

    amount_total_cents = int(round(amount_total * 100, 0))
    amount_cents = amount_total_cents // months
    remaining_cents = amount_total_cents % months

    amounts_cents = [amount_cents for _ in range(months)]
    for i in range(remaining_cents):
        amounts_cents[i] += 1
    amounts = [sign * amnt / 100 for amnt in amounts_cents]

    now = datetime.now()
    timestamps = [
        now + relativedelta(months=+i)
        for i in range(months)
    ]

    return zip(timestamps, amounts)
