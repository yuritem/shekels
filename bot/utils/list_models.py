from bot.db.models import Category, Storage
from bot.services.repository import Repository


def _format_category(category: Category, category_default: Category | None) -> str:
    default = " [default]" if (category_default and category.category_id == category_default.category_id) else ""
    return f"{category.number}. {category.name}{default}"


async def get_category_list(user_id: int, repo: Repository) -> str:
    categories = await repo.get_categories_for_user(user_id)
    category_default = await repo.get_default_category_for_user(user_id)
    categories_str = '\n'.join([_format_category(c, category_default) for c in categories])
    return categories_str


def _format_storage(storage: Storage, storage_default: Storage | None) -> str:
    default = ' [default]' if (storage_default and storage.storage_id == storage_default.storage_id) else ''
    credit = ' [credit]' if storage.is_credit else ''
    multicurrency = ' [multicurrency]' if storage.multicurrency else ''
    return f"{storage.number}. {storage.name}{credit}{multicurrency}{default}"


async def get_storage_list(user_id: int, repo: Repository) -> str:
    storages = await repo.get_storages_for_user(user_id)
    storage_default = await repo.get_default_storage_for_user(user_id)
    storages_str = '\n'.join([_format_storage(s, storage_default) for s in storages])
    return storages_str


def _format_alias(alias: dict) -> str:
    return f"{alias['alias_number']}. {alias['alias_name']} ← {alias['name']}"


async def get_alias_list(user_id: int, repo: Repository) -> str:
    aliases = await repo.get_aliases_with_full_names_for_user(user_id)
    aliases_str = '\n'.join([_format_alias(a) for a in aliases])
    return aliases_str


def _format_transaction(transaction: dict) -> str:
    return (f"{transaction['Transaction'].timestamp.strftime('%m.%d %H:%M')} | "
            f"{transaction['Transaction'].amount:.2f} "
            f"{transaction['currency_symbol']} | "
            f"{transaction['storage_name']} | "
            f"({transaction['category_name']})")


async def get_transaction_list(user_id: int, repo: Repository) -> str:
    transactions = await repo.get_transactions_with_names_for_user(user_id)
    if not transactions:
        return "No transactions yet."
    transactions_str = '\n'.join([_format_transaction(t) for t in transactions])
    transactions_str = f"List of transactions:\n\n{transactions_str}"
    return transactions_str


def _format_recurrent_transaction(rt: dict) -> str:
    return (
        f"{rt['number']}. {rt['name']}: "
        f"{rt['Recurrent'].amount:.2f} {rt['currency_symbol']} "
        f"[{rt['period']}{rt['period_unit']}] | "
        f"{rt['storage_name']} | "
        f"({rt['category_name']})"
    )


async def get_recurrent_transaction_list(user_id: int, repo: Repository) -> str:
    recurrent_transactions = await repo.get_recurrent_transactions_with_names_for_user(user_id)
    if not recurrent_transactions:
        return "No recurrent transactions yet."
    recurrent_transactions_str = '\n'.join([_format_recurrent_transaction(rt) for rt in recurrent_transactions])
    recurrent_transactions_str = f"List of recurrent transactions:\n\n{recurrent_transactions_str}"
    return recurrent_transactions_str
