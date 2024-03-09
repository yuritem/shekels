from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot.db.models import User
from bot.filters.filters import AliasableSubtypeFilter, IntegerFilter, NameFilter
from bot.services.repository import Repository
from bot.states import AliasStates, TransactionStates
from bot.utils.list_models import get_alias_list, get_storage_list, get_category_list

router = Router()


@router.message(
    Command("list_aliases"),
    TransactionStates.waiting_for_new_transaction
)
async def cmd_list_aliases(message: Message, repo: Repository, user: User):
    """Handles /list_aliases command"""
    aliases = await get_alias_list(user.user_id, repo)
    await message.answer(f"List of aliases:\n\n{aliases}")


@router.message(
    Command("add_alias"),
    TransactionStates.waiting_for_new_transaction
)
async def cmd_add_alias(message: Message, state: FSMContext):
    """Handles /add_alias command"""
    await message.answer("What is the alias for - storage, category, or currency?")
    await state.set_state(AliasStates.waiting_for_aliasable_subtype)


@router.message(
    AliasStates.waiting_for_aliasable_subtype,
    AliasableSubtypeFilter()
)
async def aliasable_subtype(message: Message, state: FSMContext, repo: Repository, user: User):
    """Handles aliasable_subtype entry after /add_alias command"""
    subtype = message.text.lower()
    await state.update_data({"aliasable_subtype": subtype})
    if subtype in ['storage', 'category']:
        if subtype == 'storage':
            aliasables = await get_storage_list(user.user_id, repo)
        else:
            aliasables = await get_category_list(user.user_id, repo)
        await message.answer(f"Provide {subtype} number:\n\n{aliasables}")
        await state.set_state(AliasStates.waiting_for_aliasable_number)
    elif subtype == 'currency':
        await message.answer("Currency 3-letter alphacode:")
        await state.set_state(AliasStates.waiting_for_currency_alphacode)
    else:
        await message.answer("Unknown type. Try again.")


@router.message(
    AliasStates.waiting_for_aliasable_number,
    IntegerFilter()
)
async def aliasable_number_to_add(message: Message, state: FSMContext, repo: Repository, user: User):
    """Handles aliasable_number entry in the process of /add_alias command"""
    aliasable_number = int(message.text)
    state_data = await state.get_data()
    subtype = state_data.get("aliasable_subtype")
    if subtype == 'storage':
        max_aliasable_number = await repo.get_max_storage_number_for_user(user.user_id)
    else:
        max_aliasable_number = await repo.get_max_category_number_for_user(user.user_id)
    if 1 <= aliasable_number <= max_aliasable_number:
        await state.update_data({"aliasable_number": aliasable_number})
        await message.answer("Your alias:")
        await state.set_state(AliasStates.waiting_for_alias_name)
    else:
        pass  # Filter behavior


@router.message(AliasStates.waiting_for_currency_alphacode)
async def currency_alphacode(message: Message, state: FSMContext, repo: Repository):
    """Handles currency_alphacode entry in the process of /add_alias command"""
    alpha_code = message.text.upper()
    currency = await repo.get_currency_by_alpha_code(alpha_code=alpha_code)
    if currency:
        await state.update_data({"currency_id": currency.currency_id})
        await message.answer("Your alias:")
        await state.set_state(AliasStates.waiting_for_alias_name)
    else:
        pass  # Filter behavior


@router.message(
    AliasStates.waiting_for_alias_name,
    NameFilter()
)
async def alias_name(message: Message, state: FSMContext, repo: Repository, user: User):
    """Handles alias_name entry in the process of /add_alias command"""
    name = message.text
    state_data = await state.get_data()
    aliasable_number = state_data.get("aliasable_number", None)
    currency_id = state_data.get("currency_id", None)
    subtype = state_data.get("aliasable_subtype")
    await repo.add_alias(
        user_id=user.user_id,
        subtype=subtype,
        name=name,
        aliasable_number=aliasable_number,
        currency_id=currency_id
    )
    await message.answer("Alias created!")
    await state.set_state(TransactionStates.waiting_for_new_transaction)


@router.message(
    Command("delete_alias"),
    TransactionStates.waiting_for_new_transaction
)
async def cmd_delete_alias(message: Message, state: FSMContext, repo: Repository, user: User):
    """Handles /delete_alias command"""
    aliases = await get_alias_list(user.user_id, repo)
    await message.answer(f"Provide alias number to delete:\n\n{aliases}")
    await state.set_state(AliasStates.waiting_for_alias_number_to_delete)


@router.message(
    AliasStates.waiting_for_alias_number_to_delete,
    IntegerFilter()
)
async def alias_number_to_delete(message: Message, state: FSMContext, repo: Repository, user: User):
    """Handles number entry after /delete_alias command"""
    alias_number = int(message.text)
    max_alias_number = await repo.get_max_alias_number_for_user(user.user_id)
    if 1 <= alias_number <= max_alias_number:
        await repo.delete_alias(user.user_id, alias_number)
        await message.answer("Alias deleted.")
        await state.set_state(TransactionStates.waiting_for_new_transaction)
    else:
        pass  # Filter behavior
