from datetime import datetime

from dateutil.relativedelta import relativedelta


def split_float_conserve_sum(money: float, parts: int) -> list[float]:
    """
        Splits a float `money` into `parts` parts, conserving the sum.
        Assumes `money` is rounded to 2 decimal places. If not, rounds it.
        Returns a list of floats that sum to `money`.
    """
    sign = 1 if money > 0 else -1  # sign treated separately for proper integer division and modulo
    money = abs(money)
    money = round(money, 2)
    money_cents = int(money * 100)
    part_cents, remaining_cents = divmod(money_cents, parts)
    return [
        sign * round((part_cents + int(i < remaining_cents)) / 100, 2)
        for i in range(parts)
    ]


async def split_transaction(amount_total: float, months: int, start_date: datetime = None) -> tuple[list[datetime], list[float]]:
    """
        Meant for installment payments.
        For `months` > 1 splits transaction into multiple transactions 1 month apart with `amount_total` equally
    distributed between payments and calculates each transaction's `timestamp`.
        If not provided, starting timestamp is taken as the current time calculated inside this function.
        Returns a tuple of two lists: timestamps and amounts.
    """

    amounts = split_float_conserve_sum(amount_total, months)

    if not start_date:
        start_date = datetime.now()
    timestamps = [
        start_date + relativedelta(months=+i)
        for i in range(months)
    ]

    return timestamps, amounts
