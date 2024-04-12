import re
from datetime import datetime

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from bot.db.models import User
from bot.filters.filters import NameFilter, IntegerFilter, FloatFilter, DateTimeFilter, PeriodicityFilter
from bot.services.repository import Repository
from bot.states import TransactionStates, RecurrentStates
from bot.utils.transaction import assume_sign
from bot.utils.list_models import (
    get_transaction_list,
    get_storage_list,
    get_category_list,
    get_recurrent_transaction_list
)

router = Router()


@router.message(
    Command("list_transactions"),
    TransactionStates.waiting_for_new_transaction
)
async def cmd_list_transactions(message: Message, repo: Repository, user: User):
    """Handles /list_transactions command"""
    transactions_str = await get_transaction_list(user.user_id, repo)
    if transactions_str:
        await message.answer(transactions_str)
    else:
        await message.answer("No transactions yet.")


@router.message(
    Command("list_recurrent"),
    TransactionStates.waiting_for_new_transaction
)
async def cmd_list_recurrent(message: Message, repo: Repository, user: User):
    """Handles /list_recurrent command"""
    recurrent_transactions_str = await get_recurrent_transaction_list(user.user_id, repo)
    if recurrent_transactions_str:
        await message.answer(recurrent_transactions_str)
    else:
        await message.answer("No recurrent transactions yet.")


@router.message(
    Command("add_recurrent"),
    TransactionStates.waiting_for_new_transaction
)
async def cmd_add_recurrent(message: Message, state: FSMContext, repo: Repository, user: User):
    """Handles /add_recurrent command"""
    storages = repo.get_storages_for_user(user.user_id)
    categories = repo.get_categories_for_user(user.user_id)
    if not storages:
        await message.answer("Add at least one storage first.")
    elif not categories:
        await message.answer("Add at least one category first.")
    else:
        await message.answer("New recurrent transaction name:")
        await state.set_state(RecurrentStates.waiting_for_recurrent_name)


@router.message(
    RecurrentStates.waiting_for_recurrent_name,
    NameFilter()
)
async def recurrent_name(message: Message, state: FSMContext):
    """Handles recurrent_name entry after /add_recurrent command"""
    name = message.text
    await state.update_data({"recurrent_name": name})
    await message.answer("Provide amount for the recurring transaction:")
    await state.set_state(RecurrentStates.waiting_for_recurrent_amount)


@router.message(
    RecurrentStates.waiting_for_recurrent_amount,
    FloatFilter()
)
async def recurrent_amount(message: Message, state: FSMContext):
    """Handles recurrent_amount entry in the process of /add_recurrent command"""
    amount = assume_sign(message.text)
    await state.update_data({"recurrent_amount": amount})
    await message.answer("Provide the recurring transaction's currency alpha code:")
    await state.set_state(RecurrentStates.waiting_for_recurrent_currency)


@router.message(
    RecurrentStates.waiting_for_recurrent_currency,
    NameFilter()
)
async def recurrent_currency(message: Message, state: FSMContext, user: User, repo: Repository):
    """Handles recurrent_currency_alpha_code entry in the process of /add_recurrent command"""
    alpha_code = message.text.upper()
    currency = await repo.get_currency_by_alpha_code(alpha_code=alpha_code)
    if currency:
        await state.update_data({"recurrent_currency_id": currency.currency_id})
        storages = await get_storage_list(user_id=user.user_id, repo=repo)
        await message.answer(f"Provide storage number:\n\n{storages}")
        await state.set_state(RecurrentStates.waiting_for_recurrent_storage)
    else:
        pass  # Filter behavior


@router.message(
    RecurrentStates.waiting_for_recurrent_storage,
    IntegerFilter()
)
async def recurrent_storage_number(message: Message, state: FSMContext, user: User, repo: Repository):
    """Handles recurrent_storage_number entry in the process of /add_recurrent command"""
    storage_number = int(message.text)
    storage = await repo.get_storage_by_number_for_user(user_id=user.user_id, number=storage_number)
    if storage:
        await state.update_data({"recurrent_storage_number": storage_number})
        categories = await get_category_list(user_id=user.user_id, repo=repo)
        await message.answer(f"Provide the recurring transaction's category number:\n\n{categories}")
        await state.set_state(RecurrentStates.waiting_for_recurrent_category)
    else:
        pass  # Filter behavior


@router.message(
    RecurrentStates.waiting_for_recurrent_category,
    IntegerFilter()
)
async def recurrent_category_number(message: Message, state: FSMContext, user: User, repo: Repository):
    """Handles recurrent_category_number entry in the process of /add_recurrent command"""
    category_number = int(message.text)
    category = await repo.get_category_by_number_for_user(user.user_id, category_number)
    if category:
        await state.update_data({"recurrent_category_number": category_number})
        await message.answer("Provide recurrent transaction's periodicity. Examples: '1d', '2w', '1m', '1y':")
        await state.set_state(RecurrentStates.waiting_for_recurrent_periodicity)


@router.message(
    RecurrentStates.waiting_for_recurrent_periodicity,
    PeriodicityFilter()
)
async def recurrent_periodicity(message: Message, state: FSMContext):
    """Handles recurrent_periodicity entry in the process of /add_recurrent command"""
    period, period_unit = re.fullmatch(PeriodicityFilter.periodicity_pattern, message.text).groups()
    period_unit = PeriodicityFilter.map[period_unit]
    period = int(period)
    await state.update_data({"recurrent_period": period, "recurrent_period_unit": period_unit})
    await message.answer("Provide the recurring transaction's start datetime in the 'YYYY-MM-DD HH:MM' format:")
    await state.set_state(RecurrentStates.waiting_for_recurrent_timestamp)


@router.message(
    RecurrentStates.waiting_for_recurrent_timestamp,
    DateTimeFilter()
)
async def recurrent_timestamp(message: Message, state: FSMContext, user: User, repo: Repository):
    """Handles recurrent_timestamp entry in the process of /add_recurrent command"""
    timestamp = datetime.strptime(message.text, '%Y-%m-%d %H:%M')
    state_data = await state.get_data()
    name = state_data.get("recurrent_name")
    amount = state_data.get("recurrent_amount")
    storage_number = state_data.get("recurrent_storage_number")
    storage = await repo.get_storage_by_number_for_user(user_id=user.user_id, number=storage_number)
    category_number = state_data.get("recurrent_category_number")
    category = await repo.get_category_by_number_for_user(user_id=user.user_id, number=category_number)
    currency_id = state_data.get("recurrent_currency_id")
    period = state_data.get("recurrent_period")
    period_unit = state_data.get("recurrent_period_unit")
    await repo.add_recurrent_transaction(
        user_id=user.user_id,
        storage_id=storage.storage_id,
        category_id=category.category_id,
        currency_id=currency_id,
        name=name,
        amount=amount,
        start_timestamp=timestamp,
        period=period,
        period_unit=period_unit
    )
    await message.answer(f"Recurrent transaction '{name}' added successfully!")
    await state.set_state(TransactionStates.waiting_for_new_transaction)


@router.message(
    Command("edit_recurrent"),
    TransactionStates.waiting_for_new_transaction
)
async def edit_recurrent(message: Message, state: FSMContext, user: User, repo: Repository):
    """Handles /edit_recurrent command"""
    recurrent_transactions_str = await get_recurrent_transaction_list(user.user_id, repo)
    if recurrent_transactions_str:
        await message.answer(recurrent_transactions_str)
        await message.answer("Provide the number of the recurrent transaction you want to edit:")
        await state.set_state(RecurrentStates.waiting_for_recurrent_number_to_edit)
    else:
        await message.answer("No recurrent transactions yet.")


@router.message(
    RecurrentStates.waiting_for_recurrent_number_to_edit,
    IntegerFilter()
)
async def recurrent_number_to_edit(message: Message, state: FSMContext, user: User, repo: Repository):
    """Handles recurrent_number entry after /edit_recurrent command"""
    recurrent_number = int(message.text)
    recurrent = await repo.get_recurrent_transaction_by_number_for_user(user_id=user.user_id, number=recurrent_number)
    if recurrent:
        await state.update_data({"recurrent_number": recurrent_number})
        await message.answer("New recurrent transaction name:")
        await state.set_state(RecurrentStates.waiting_for_edited_recurrent_name)
    else:
        pass  # filter behavior


@router.message(
    RecurrentStates.waiting_for_edited_recurrent_name,
    NameFilter()
)
async def edited_recurrent_name(message: Message, state: FSMContext):
    """Handles recurrent_name entry in the process of /edit_recurrent command"""
    name = message.text
    await state.update_data({"recurrent_name": name})
    await message.answer("New recurring transaction amount:")
    await state.set_state(RecurrentStates.waiting_for_edited_recurrent_amount)


@router.message(
    RecurrentStates.waiting_for_edited_recurrent_amount,
    FloatFilter()
)
async def edited_recurrent_amount(message: Message, state: FSMContext, repo: Repository, user: User):
    """Handles recurrent_amount entry in the process of /edit_recurrent command"""
    amount = assume_sign(message.text)
    state_data = await state.get_data()
    number = state_data.get("recurrent_number")
    name = state_data.get("recurrent_name")
    await repo.update_recurrent_transaction_by_number_for_user(
        user_id=user.user_id,
        number=number,
        name=name,
        amount=amount
    )
    await message.answer("Recurrent transaction edited!")
    await state.set_state(TransactionStates.waiting_for_new_transaction)


@router.message(
    Command("delete_recurrent"),
    TransactionStates.waiting_for_new_transaction
)
async def delete_recurrent(message: Message, state: FSMContext, user: User, repo: Repository):
    """Handles /delete_recurrent command"""
    recurrent_transactions_str = await get_recurrent_transaction_list(user.user_id, repo)
    if recurrent_transactions_str:
        await message.answer(recurrent_transactions_str)
        await message.answer("Provide the number of the recurrent transaction you want to delete:")
        await state.set_state(RecurrentStates.waiting_for_recurrent_number_to_delete)
    else:
        await message.answer("No recurrent transactions yet.")


@router.message(
    RecurrentStates.waiting_for_recurrent_number_to_delete,
    IntegerFilter()
)
async def recurrent_number_to_delete(message: Message, state: FSMContext, user: User, repo: Repository):
    """Handles recurrent_number entry after /delete_recurrent command"""
    recurrent_number = int(message.text)
    recurrent = await repo.get_recurrent_transaction_by_number_for_user(user_id=user.user_id, number=recurrent_number)
    if recurrent:
        await repo.delete_recurrent_transaction_by_number_for_user(user_id=user.user_id, number=recurrent_number)
        await message.answer(f"Recurrent transaction '{recurrent.name}' deleted successfully!")
        await state.set_state(TransactionStates.waiting_for_new_transaction)
    else:
        pass  # filter behavior
