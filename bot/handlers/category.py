from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.db.models import Category, Aliasable
from bot.filters.category import LongNameFilter, AnyBooleanFilter
from bot.states import CategoryStates, TransactionStates

router = Router()


@router.message(
    Command("add_category"),
    TransactionStates.waiting_for_new_transaction
)
async def cmd_add_category(message: Message, state: FSMContext):
    """Handles /add_category command"""
    await message.answer("New category name:")
    await state.set_state(CategoryStates.waiting_for_new_category_name)


@router.message(CategoryStates.waiting_for_new_category_name)
async def category_name_to_add(message: Message, state: FSMContext):
    """Handles category_name entry after /add_category command"""
    if LongNameFilter()(message):
        await state.update_data({"category_name": message.text})
        await message.answer("Provide category factor_in: whether it should be accounted for in balance (1), or not (0)")
        await state.set_state(CategoryStates.waiting_for_new_category_factor_in)
    else:
        await message.answer("Category name should be 1+ words (letters, numbers, -, _) separated with spaces.")


@router.message(CategoryStates.waiting_for_new_category_factor_in)
async def category_factor_in_to_add(message: Message, state: FSMContext, session: AsyncSession):
    """Handles category_factor_in entry in the process of /add_category command"""
    if AnyBooleanFilter()(message):
        state_data = await state.get_data()
        user_id = message.from_user.id
        factor_in = AnyBooleanFilter.str_bool[message.text.lower()]
        category_name = state_data.get("category_name")
        aliasable = Aliasable(aliasable_subtype="category")
        session.add(aliasable)
        await session.refresh(aliasable)
        res = await session.execute(select(Category).where(Category.user_id == user_id).order_by())  # todo
        Category(
            user_id=user_id,
            aliasable_id=aliasable.aliasable_id,
            category_number=...,
            name=category_name,
            factor_in=factor_in
        )
        await message.answer("Category creation processed.")
        await state.set_state(TransactionStates.waiting_for_new_transaction)
    else:
        await message.answer(f"Answer should be one of the following: {', '.join(AnyBooleanFilter.str_bool.keys())}.")


@router.message(
    Command("edit_category"),
    TransactionStates.waiting_for_new_transaction
)
async def cmd_edit_category(message: Message, state: FSMContext):
    """Handles /edit_category command"""
    await message.answer("Provide category number to edit.")
    await state.set_state(CategoryStates.waiting_for_category_number_to_edit)


@router.message(CategoryStates.waiting_for_category_number_to_edit)
async def category_number_to_edit(message: Message, state: FSMContext):
    """Handles category_number entry after /edit_category command"""
    await message.answer("Provide new name for the category.")
    await state.set_state(CategoryStates.waiting_for_edited_category_name)


@router.message(CategoryStates.waiting_for_edited_category_name)
async def category_name_to_edit(message: Message, state: FSMContext):
    """Handles category_name entry in the process of /edit_category command"""
    await message.answer("Provide new factor_in value for the category. 1 if acocount for in balance, 0 otherwise")
    await state.set_state(CategoryStates.waiting_for_edited_category_factor_in)


@router.message(CategoryStates.waiting_for_edited_category_factor_in)
async def category_factor_in_to_edit(message: Message, state: FSMContext):
    """Handles category_factor_in in the process of /edit_category command"""
    await message.answer("Category edit processed.")
    await state.set_state(TransactionStates.waiting_for_new_transaction)


@router.message(
    Command("delete_category"),
    TransactionStates.waiting_for_new_transaction
)
async def cmd_delete_category(message: Message, state: FSMContext):
    """Handles /delete_category command"""
    await message.answer("Provide category number to delete.")  # todo: behaviour for DB?
    await state.set_state(CategoryStates.waiting_for_category_number_to_delete)


@router.message(CategoryStates.waiting_for_category_number_to_delete)
async def category_number_to_delete(message: Message, state: FSMContext):
    """Handles category_number entry after /delete_category command"""
    await message.answer("Category deletion processed.")
    await state.set_state(TransactionStates.waiting_for_new_transaction)
