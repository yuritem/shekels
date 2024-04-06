from bot.services.repository import Repository


async def get_category_list(user_id: int, repo: Repository) -> str:
    categories = await repo.get_categories_for_user(user_id)
    if not categories:
        return "No categories yet."
    category_default = await repo.get_default_category_for_user(user_id)
    categories_str = '\n'.join([
        f"{c.number}. {c.name}" + " [default]" * (c.category_id == category_default.category_id)
        for c in categories
    ])
    categories_str = f"List of categories:\n\n{categories_str}"
    return categories_str


async def get_storage_list(user_id: int, repo: Repository) -> str:
    storages = await repo.get_storages_for_user(user_id)
    if not storages:
        return "No storages yet."
    storage_default = await repo.get_default_storage_for_user(user_id)
    storage_strings = []
    for storage in storages:
        default = ' [default]' if storage.storage_id == storage_default.storage_id else ''
        credit = ' [credit]' if storage.is_credit else ''
        multicurrency = ' [multicurrency]' if storage.multicurrency else ''
        s = f"{storage.number}. {storage.name}{credit}{multicurrency}{default}"
        storage_strings.append(s)

    storages_str = '\n'.join(storage_strings)
    storages_str = f"List of storages:\n\n{storages_str}"
    return storages_str


async def get_alias_list(user_id: int, repo: Repository) -> str:
    aliases = await repo.get_aliases_with_full_names_for_user(user_id)
    if not aliases:
        return "No aliases yet."

    aliases_str = '\n'.join([
        f"{a['alias_number']}. {a['alias_name']} ← {a['name']}"
        for a in aliases
    ])
    aliases_str = f"List of aliases:\n\n{aliases_str}"
    return aliases_str


async def get_transaction_list(user_id: int, repo: Repository) -> str:
    transactions = await repo.get_transactions_with_names_for_user(user_id)

    if not transactions:
        return "No transactions yet."

    transactions_str = '\n'.join([
        f"{t['Transaction'].timestamp.strftime('%Y.%m.%d %H:%M')} "
        f"{t['Transaction'].amount:.2f} "
        f"{t['currency_symbol']} "
        f"{t['storage_name']} "
        f"({t['category_name']})"
        for t in transactions
    ])
    transactions_str = f"List of transactions:\n\n{transactions_str}"
    return transactions_str


# async def get_recurrent_transaction_list(user_id: int, repo: Repository) -> str:
#     recurrent_transactions = await repo.get_recurrent_transactions_with_names_for_user(user_id)
#     recurrent_transactions_str = '\n'.join([
#         f"{t['Recurrent'].next_timestamp.strftime('%Y.%m.%d %H:%M')} "
#         f"{t['Transaction'].amount:.2f} "
#         f"{t['currency_symbol']} "
#         f"{t['storage_name']} "
#         f"({t['category_name']})"
#         for t in recurrent_transactions
#     ])
#     return recurrent_transactions_str
