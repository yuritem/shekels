from datetime import datetime
from dateutil.relativedelta import relativedelta

from bot.db.types import RecurrentPeriodUnit


def recurrent_timestamps(
        next_timestamp: datetime,
        period: int,
        period_unit: RecurrentPeriodUnit,
        up_to_timestamp: datetime = None
) -> tuple[list[datetime], datetime]:
    """
    Returns a tuple of:
        - list of timestamps starting from `next_timestamp` up to `up_to_timestamp` with given periodicity;
        - next timestamp after `up_to`.
    """
    relativedelta_kwargs = {f"{period_unit}s": period}
    if not up_to_timestamp:
        up_to_timestamp = datetime.now(tz=next_timestamp.tzinfo)
    else:
        if not up_to_timestamp.tzinfo:
            up_to_timestamp = up_to_timestamp.replace(tzinfo=next_timestamp.tzinfo)
    timestamps = [next_timestamp]
    while timestamps[-1] <= up_to_timestamp:
        timestamps.append(timestamps[-1] + relativedelta(**relativedelta_kwargs))
    return timestamps[:-1], timestamps[-1]
