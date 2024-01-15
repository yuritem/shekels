from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot.db.models import User
from bot.filters.filters import LongNameFilter, YesNoFilter, NumberFilter
from bot.services.repository import Repository
from bot.states import CategoryStates, TransactionStates
from bot.utils.list_models import get_category_list

router = Router()


@router.message(
    Command("add_category"),
    TransactionStates.waiting_for_new_transaction
)
async def cmd_add_category(message: Message, state: FSMContext):
    """Handles /add_category command"""
    await message.answer("New category name:")
    await state.set_state(CategoryStates.waiting_for_new_category_name)


@router.message(
    CategoryStates.waiting_for_new_category_name,
    LongNameFilter()
)
async def category_name_to_add(message: Message, state: FSMContext):
    """Handles category_name entry after /add_category command"""
    await state.update_data({"category_name": message.text})
    await message.answer(f"Should we account for this category when calculating balance?")
    await state.set_state(CategoryStates.waiting_for_new_category_factor_in)


@router.message(
    CategoryStates.waiting_for_new_category_factor_in,
    YesNoFilter()
)
async def category_factor_in_to_add(message: Message, state: FSMContext, repo: Repository, user: User):
    """Handles category_factor_in entry in the process of /add_category command"""
    state_data = await state.get_data()
    category_name = state_data.get("category_name")
    factor_in = YesNoFilter.map[message.text.lower()]
    await repo.add_category(user_id=user.user_id, name=category_name, factor_in=factor_in)
    await message.answer("Category created!")
    await state.set_state(TransactionStates.waiting_for_new_transaction)


@router.message(
    Command("edit_category"),
    TransactionStates.waiting_for_new_transaction
)
async def cmd_edit_category(message: Message, state: FSMContext, repo: Repository, user: User):
    """Handles /edit_category command"""
    categories = await get_category_list(user.user_id, repo)
    await message.answer(f"Provide category number to edit:\n\n{categories}")
    await state.set_state(CategoryStates.waiting_for_category_number_to_edit)


@router.message(
    CategoryStates.waiting_for_category_number_to_edit,
    NumberFilter()
)
async def category_number_to_edit(message: Message, state: FSMContext, repo: Repository, user: User):
    """Handles category_number entry after /edit_category command"""
    category_number = int(message.text)
    max_category_number = await repo.get_max_category_number_for_user(user.user_id)
    if category_number <= max_category_number:
        await state.update_data({"category_number": category_number})
        await message.answer("New name for the category:")
        await state.set_state(CategoryStates.waiting_for_edited_category_name)
    else:
        pass  # Filter behavior


@router.message(
    CategoryStates.waiting_for_edited_category_name,
    LongNameFilter()
)
async def category_name_to_edit(message: Message, state: FSMContext):
    """Handles category_name entry in the process of /edit_category command"""
    await state.update_data({"category_name": message.text})
    await message.answer(f"Should we account for this category when calculating balance?")
    await state.set_state(CategoryStates.waiting_for_edited_category_factor_in)


@router.message(
    CategoryStates.waiting_for_edited_category_factor_in,
    YesNoFilter()
)
async def category_factor_in_to_edit(message: Message, state: FSMContext, repo: Repository, user: User):
    """Handles category_factor_in in the process of /edit_category command"""
    state_data = await state.get_data()
    category_name = state_data.get("category_name")
    category_number = state_data.get("category_number")
    factor_in = YesNoFilter.map[message.text.lower()]
    await repo.update_category(user_id=user.user_id, number=category_number, name=category_name, factor_in=factor_in)
    await message.answer("Category edited!")
    await state.set_state(TransactionStates.waiting_for_new_transaction)


@router.message(
    Command("delete_category"),
    TransactionStates.waiting_for_new_transaction
)
async def cmd_delete_category(message: Message, state: FSMContext, repo: Repository, user: User):
    """Handles /delete_category command"""
    categories = await get_category_list(user.user_id, repo)
    await message.answer(f"Provide category number to delete:\n\n{categories}")
    await state.set_state(CategoryStates.waiting_for_category_number_to_delete)


@router.message(
    CategoryStates.waiting_for_category_number_to_delete,
    NumberFilter()
)
async def category_number_to_delete(message: Message, state: FSMContext, repo: Repository, user: User):
    """Handles category_number entry after /delete_category command"""
    category_number = int(message.text)
    max_category_number = await repo.get_max_category_number_for_user(user.user_id)
    if category_number <= max_category_number:
        await repo.delete_category(user.user_id, category_number)
        await message.answer(f"Category deleted.")
        await state.set_state(TransactionStates.waiting_for_new_transaction)
    else:
        pass  # Filter behavior


@router.message(
    Command("set_default_category"),
    TransactionStates.waiting_for_new_transaction
)
async def cmd_set_default_category(message: Message, state: FSMContext, repo: Repository, user: User):
    """Handles /set_default_category command"""
    categories = await get_category_list(user.user_id, repo)
    await message.answer(f"Provide category number to set as default:\n\n{categories}")
    await state.set_state(CategoryStates.waiting_for_category_number_to_set_default)


@router.message(
    CategoryStates.waiting_for_category_number_to_set_default,
    NumberFilter()
)
async def category_number_to_set_default(message: Message, state: FSMContext, repo: Repository, user: User):
    """Handles category_number entry after /set_default_category command"""
    category_number = int(message.text)
    max_category_number = await repo.get_max_category_number_for_user(user.user_id)
    if category_number <= max_category_number:
        category = await repo.set_default_category(user.user_id, category_number)
        await message.answer(f"Category '{category.name}' is now default!")
        await state.set_state(TransactionStates.waiting_for_new_transaction)
    else:
        pass  # Filter behavior
