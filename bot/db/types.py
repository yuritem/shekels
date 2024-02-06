from typing import Union, Literal
from bot.db.models import Currency, Storage, Category, Alias

AliasableSubtype = Literal["category", "storage", "currency"]
RecurrentPeriodUnit = Literal["day", "week", "month", "year"]
AliasableModel = Union[Currency, Storage, Category]
NumberedModel = Union[Storage, Alias, Category]
