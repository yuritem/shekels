from typing import Union
from bot.db.models import Currency, Storage, Category, Alias

AliasableModel = Union[Currency, Storage, Category]
NumberedModel = Union[Storage, Category, Alias]
ModelWithDefault = Union[Currency, Storage, Category]
