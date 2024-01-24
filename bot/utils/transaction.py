import re
from typing import Sequence, Optional, Type

from bot.db.models import Storage, Alias, Currency, Category
from bot.filters.filters import TransactionFilter
from bot.errors import ParsingError
from bot.services.repository import Repository
from bot.db.types import AliasableModel


async def _aliasable_model(
        text: str,
        model: Type[AliasableModel],
        models: Sequence[AliasableModel],
        model_aliases: Sequence[Alias],
        repo: Repository
) -> Optional[AliasableModel]:

    for s in models:
        if text == s.name:
            return s
    for a in model_aliases:
        if text == a.name:
            return await repo.session.get(model, a.aliasable_id)
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


async def parse_transaction_(
        text: str,
        user_id: int,
        repo: Repository
):

    category_default = repo.get_default_category_for_user(user_id)
    storage_default = repo.get_default_storage_for_user(user_id)
    currency_default = repo.get_default_currency_for_user(user_id)

    storages = await repo.get_storages_for_user(user_id)
    categories = await repo.get_categories_for_user(user_id)
    currencies = await repo.get_currencies()

    storage_aliases = await repo.get_aliases_of_subtype_for_user(user_id, "storage")
    category_aliases = await repo.get_aliases_of_subtype_for_user(user_id, "storage")
    currency_aliases = await repo.get_aliases_of_subtype_for_user(user_id, "storage")

    match = re.fullmatch(TransactionFilter.transaction_pattern, text)
    if not match:
        raise ParsingError("Message does not conform to pattern.")
    amount, months, slot_0, slot_1, slot_2 = match.groups()

    if '+' in amount or '-' in amount:
        amount = float(amount)
    else:
        amount = -float(amount)  # negative amount by default

    months = None if months is None else int(months)

    currency = await _currency(slot_0, currencies, currency_aliases, repo)
    if not currency:
        currency = currency_default
        if slot_2 is not None:
            raise ParsingError(
                "Failed to parse message."
                " Perhaps currency could not be identified"
                " or you explicitly passed a category for a transfer between two storages."
            )
        slot_1, slot_2 = slot_0, slot_1

    # options:
    # - [1] = storage_1  [2] = storage_2
    # - [1] = storage    [2] = category
    # - [1] = storage    [2] = None
    # - [1] = category   [2] = None
    # - [1] = None       [2] = None

    if slot_1 is None and slot_2 is None:
        storages = [storage_default, ]
        category = category_default

    elif (slot_2 is None) and (category := await _category(slot_1, categories, category_aliases, repo)):
        storages = [storage_default, ]
        category = category

    elif storage_1 := await _storage(slot_1, storages, storage_aliases, repo):
        storages = [storage_1, ]

        if storage_2 := await _storage(slot_2, storages, storage_aliases, repo):
            storages.append(storage_2)
            category = "Transfer"

        elif category := await _category(slot_2, categories, category_aliases, repo):
            category = category

        elif slot_2 is None:
            category = category_default

        else:
            raise ParsingError("Failed to parse transfer destination storage or category.")

    else:
        raise ParsingError("Failed to parse storage or category.")

    return {
        "amount": amount,
        "months": months,
        "currency": currency,
        "storages": storages,
        "category": category
    }
