import re
from datetime import datetime
from dateutil.relativedelta import relativedelta
from typing import Sequence, Optional, Type, Iterator

from bot.db.models import Storage, Alias, Currency, Category
from bot.filters.filters import TransactionFilter
from bot.errors import TransacionParsingError
from bot.services.repository import Repository
from bot.db.model_types import AliasableModel


async def _aliasable_model(
        text: str,
        model: Type[AliasableModel],
        models: Sequence[AliasableModel],
        model_aliases: Sequence[Alias],
        repo: Repository
) -> Optional[AliasableModel]:

    text_casefold = text.casefold()

    if model == Currency:
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


async def parse_and_add_transactions(text: str, user_id: int, repo: Repository) -> None:

    category_default = await repo.get_default_category_for_user(user_id)
    storage_default = await repo.get_default_storage_for_user(user_id)
    currency_default = await repo.get_default_currency_for_user(user_id)

    storages = await repo.get_storages_for_user(user_id)
    categories = await repo.get_categories_for_user(user_id)
    currencies = await repo.get_currencies()

    storage_aliases = await repo.get_storage_aliases_for_user(user_id)
    category_aliases = await repo.get_category_aliases_for_user(user_id)
    currency_aliases = await repo.get_currency_aliases_for_user(user_id)

    match = re.fullmatch(TransactionFilter.transaction_pattern, text)
    if not match:
        raise TransacionParsingError("Message does not conform to pattern.")
    amount_total, months, slot_0, slot_1, slot_2 = match.groups()
    if not amount_total:
        raise TransacionParsingError("Amount could not be parsed. Perhaps you passed more than 2 decimal points.")

    if '+' in amount_total or '-' in amount_total:
        amount_total = float(amount_total)
    else:
        amount_total = -float(amount_total)  # negative amount by default

    months = 1 if months is None else int(months)

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

    if currency is None or storage is None or category is None:
        raise TransacionParsingError("One or more defaults missing and not passed explicitly.")

    await repo.add_transactions(
        user_id=user_id,
        amount_total=amount_total,
        months=months,
        currency_id=currency.currency_id,
        storage_id=storage.storage_id,
        category_id=category.category_id
    )


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
