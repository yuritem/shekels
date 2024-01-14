from bot.services.repository import Repository


async def get_category_list(user_id: int, repo: Repository) -> str:
    categories = await repo.get_categories_for_user(user_id)
    category_default = await repo.get_default_category_for_user(user_id)
    categories_str = '\n'.join([
        f"{c.number}. {c.name}" + " [default]" * (c.category_id == category_default.category_id)
        for c in categories
    ])
    return categories_str


async def get_storage_list(user_id: int, repo: Repository) -> str:
    storages = await repo.get_storages_for_user(user_id)
    storage_default = await repo.get_default_storage_for_user(user_id)
    storage_strings = []
    for storage in storages:
        default = ' [default]' if storage.storage_id == storage_default.storage_id else ''
        credit = ' [credit]' if storage.is_credit else ''
        multicurrency = ' [multicurrency]' if storage.multicurrency else ''
        s = f"{storage.number}. {storage.name}{credit}{multicurrency}{default}"
        storage_strings.append(s)

    storages_str = '\n'.join([
        f"{s.number}. {s.name}" + " [default]" * (s.storage_id == storage_default.storage_id)
        for s in storages
    ])
    return storages_str


async def get_alias_list(user_id: int, repo: Repository):
    aliases = await repo.get_aliases_with_full_names_for_user(user_id)
    aliases_str = '\n'.join([
        f"{a['alias_number']}. {a['alias_name']} ← {a['name']}"
        for a in aliases
    ])
    return aliases_str
