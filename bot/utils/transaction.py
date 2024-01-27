import re
from typing import Sequence, Optional, Type

from bot.db.models import Storage, Alias, Currency, Category
from bot.filters.filters import TransactionFilter
from bot.errors import TransacionParsingError
from bot.services.repository import Repository
from bot.db.types import AliasableModel


async def _aliasable_model(
        text: str,
        model: Type[AliasableModel],
        models: Sequence[AliasableModel],
        model_aliases: Sequence[Alias],
        repo: Repository
) -> Optional[AliasableModel]:

    print(f"Called with: text={text}, model={model}")

    text_casefold = text.casefold()

    if model == Currency:
        print("model is Currency")
        name_field = 'alpha_code'
    else:
        name_field = 'name'
    for m in models:
        if text_casefold == getattr(m, name_field).casefold():
            return m

    for model_alias in model_aliases:
        if text_casefold == model_alias.name.casefold():
            return await repo.session.get(model, model_alias.aliasable_id)

    return None


async def _currency(text: str, currencies: Sequence[Currency], currency_aliases: Sequence[Alias], repo: Repository) -> Optional[Currency]:
    return await _aliasable_model(
        text,
        model=Currency,
        models=currencies,
        model_aliases=currency_aliases,
        repo=repo
    )


async def _storage(text: str, storages: Sequence[Storage], storage_aliases: Sequence[Alias], repo: Repository) -> Optional[Storage]:
    return await _aliasable_model(
        text,
        model=Storage,
        models=storages,
        model_aliases=storage_aliases,
        repo=repo
    )


async def _category(text: str, categories: Sequence[Category], category_aliases: Sequence[Alias], repo: Repository) -> Optional[Category]:
    return await _aliasable_model(
        text,
        model=Category,
        models=categories,
        model_aliases=category_aliases,
        repo=repo
    )


async def parse_transaction(
        text: str,
        user_id: int,
        repo: Repository
):

    category_default = await repo.get_default_category_for_user(user_id)
    storage_default = await repo.get_default_storage_for_user(user_id)
    currency_default = await repo.get_default_currency_for_user(user_id)

    storages = await repo.get_storages_for_user(user_id)
    categories = await repo.get_categories_for_user(user_id)
    currencies = await repo.get_currencies()

    storage_aliases = await repo.get_aliases_of_subtype_for_user(user_id, "storage")
    category_aliases = await repo.get_aliases_of_subtype_for_user(user_id, "category")
    currency_aliases = await repo.get_aliases_of_subtype_for_user(user_id, "currency")

    match = re.fullmatch(TransactionFilter.transaction_pattern, text)
    if not match:
        raise TransacionParsingError("Message does not conform to pattern.")
    amount, months, slot_0, slot_1, slot_2 = match.groups()

    if '+' in amount or '-' in amount:
        amount = float(amount)
    else:
        amount = -float(amount)  # negative amount by default

    months = None if months is None else int(months)

    if (slot_0 is not None) and (currency_ := await _currency(slot_0, currencies, currency_aliases, repo)):
        currency = currency_
    else:
        currency = currency_default
        if slot_2 is not None:
            raise TransacionParsingError(
                "Failed to parse message."
                " Perhaps currency could not be identified"
                " or you explicitly passed a category for a transfer between two storages."
            )
        slot_2, slot_1 = slot_1, slot_0

    # options:
    # - [1] = None       [2] = None
    # - [1] = category   [2] = None
    # - [1] = storage    [2] = None
    # - [1] = storage    [2] = category

    if (not slot_1) and (not slot_2):
        storage = storage_default
        category = category_default

    elif slot_1 and (not slot_2) and (category_ := await _category(slot_1, categories, category_aliases, repo)):
        storage = storage_default
        category = category_

    elif slot_1 and (storage_ := await _storage(slot_1, storages, storage_aliases, repo)):
        storage = storage_

        if slot_2 is None:
            category = category_default

        elif category_ := await _category(slot_2, categories, category_aliases, repo):
            category = category_

        else:
            raise TransacionParsingError("Failed to parse transfer destination storage or category.")

    else:
        raise TransacionParsingError("Failed to parse storage or category.")

    return {
        "amount": amount,
        "months": months,
        "currency": currency,
        "storage": storage,
        "category": category
    }
