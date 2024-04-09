from typing import Union
from bot.db.models import Currency, Storage, Category, Alias, Recurrent

AliasableModel = Union[Currency, Storage, Category]
NumberedModel = Union[Storage, Category, Alias, Recurrent]
ModelWithDefault = Union[Currency, Storage, Category]
