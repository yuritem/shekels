from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.states import AliasStates, TransactionStates

router = Router()


@router.message(
    Command("add_alias"),
    TransactionStates.waiting_for_new_transaction
)
async def cmd_add_alias(message: Message, state: FSMContext, session: AsyncSession):
    """Handles /add_alias command"""
    await message.answer("Provide an aliasable sybtype: 'storage', 'category', or 'currency'.")  # todo
    await state.set_state(AliasStates.waiting_for_aliasable_subtype)


@router.message(AliasStates.waiting_for_aliasable_subtype)
async def aliasable_subtype(message: Message, state: FSMContext):
    """Handles aliasable_subtype entry after /add_alias command"""
    subtype = message.text
    if subtype in ['storage', 'category']:
        await message.answer("Provide aliasable number.")  # todo
        await state.set_state(AliasStates.waiting_for_aliasable_number)
    elif subtype == 'currency':
        await message.answer("Provide currency alphacode.")  # todo
        await state.set_state(AliasStates.waiting_for_currency_alphacode)
    else:
        await message.answer("Unknown type. Try again. Provide an aliasable sybtype.")


@router.message(AliasStates.waiting_for_aliasable_number)
async def aliasable_number(message: Message, state: FSMContext):
    """Handles aliasable_number entry in the process of /add_alias command"""
    await message.answer("Provide alias name.")
    await state.set_state(AliasStates.waiting_for_alias_name)


@router.message(AliasStates.waiting_for_currency_alphacode)
async def currency_alphacode(message: Message, state: FSMContext):
    """Handles currency_alphacode entry in the process of /add_alias command"""
    await message.answer("Provide alias name.")
    await state.set_state(AliasStates.waiting_for_alias_name)


@router.message(AliasStates.waiting_for_alias_name)
async def alias_name(message: Message, state: FSMContext):
    """Handles alias_name entry in the process of /add_alias command"""
    await message.answer("Alias creation processed.")
    await state.set_state(TransactionStates.waiting_for_new_transaction)


@router.message(
    Command("delete_alias"),
    TransactionStates.waiting_for_new_transaction
)
async def cmd_delete_alias(message: Message, state: FSMContext):
    """Handles /delete_alias command"""
    await message.answer("Provide alias number to delete.")
    await state.set_state(AliasStates.waiting_for_alias_number_to_delete)


@router.message(AliasStates.waiting_for_alias_number_to_delete)
async def alias_number_to_delete(message: Message, state: FSMContext):
    """Handles alias_number entry after /delete_alias command"""
    await message.answer("Alias deletion processed.")
    await state.set_state(TransactionStates.waiting_for_new_transaction)
