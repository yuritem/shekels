from datetime import datetime
from dateutil.relativedelta import relativedelta

from bot.db.types import RecurrentPeriodUnit


def recurrent_timestamps(
        next_timestamp: datetime,
        period: int,
        period_unit: RecurrentPeriodUnit
) -> tuple[list[datetime], datetime]:
    """
    Returns a tuple of:
        - list of timestamps starting from `next_timestamp` up to `now` with given periodicity;
        - next timestamp after `now`.
    """
    relativedelta_kwargs = {f"{period_unit}s": period}
    now = datetime.now()
    timestamps = [next_timestamp]
    while timestamps[-1] <= now:
        timestamps.append(timestamps[-1] + relativedelta(**relativedelta_kwargs))
    return timestamps[:-1], timestamps[-1]
