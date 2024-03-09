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
from bot.utils.list_models import get_transaction_list, get_storage_list, get_category_list

router = Router()


@router.message(
    Command("list_transactions"),
    TransactionStates.waiting_for_new_transaction
)
async def cmd_list_transactions(message: Message, repo: Repository, user: User):
    """Handles /list_transactions command"""
    transactions = await get_transaction_list(user.user_id, repo)
    await message.answer(f"List of transactions:\n\n{transactions}")


@router.message(
    Command("add_recurrent"),
    TransactionStates.waiting_for_new_transaction
)
async def cmd_add_recurrent(message: Message, state: FSMContext):
    await message.answer("New recurrent transaction name:")
    await state.set_state(RecurrentStates.waiting_for_recurrent_name)


@router.message(
    RecurrentStates.waiting_for_recurrent_name,
    NameFilter()
)
async def recurrent_name(message: Message, state: FSMContext):
    await state.update_data({"recurrent_name": message.text})
    await message.answer("Provide amount for the recurring transaction:")
    await state.set_state(RecurrentStates.waiting_for_recurrent_amount)


@router.message(
    RecurrentStates.waiting_for_recurrent_amount,
    FloatFilter()
)
async def recurrent_amount(message: Message, state: FSMContext):
    await state.update_data({"recurrent_amount": message.text})
    await message.answer("Provide the recurring transaction's currency alpha code:")
    await state.set_state(RecurrentStates.waiting_for_recurrent_currency)


@router.message(
    RecurrentStates.waiting_for_recurrent_currency,
    NameFilter()
)
async def recurrent_currency(message: Message, state: FSMContext, user: User, repo: Repository):
    alpha_code = message.text.upper()
    currency = await repo.get_currency_by_alpha_code(alpha_code=alpha_code)
    if currency:
        await state.update_data({"recurrent_currency": currency})
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
    storage_number = int(message.text)
    max_storage_number = await repo.get_max_storage_number_for_user(user.user_id)
    if 1 <= storage_number <= max_storage_number:
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
    category_number = int(message.text)
    max_category_number = await repo.get_max_category_number_for_user(user.user_id)
    if 1 <= category_number <= max_category_number:
        await state.update_data({"recurrent_category_number": category_number})
        await message.answer("Provide recurrent transaction's periodicity. Examples: '1d', '2w', '1m', '1y':")


@router.message(
    RecurrentStates.waiting_for_recurrent_periodicity,
    PeriodicityFilter()
)
async def recurrent_periodicity(message: Message, state: FSMContext):
    period, period_unit = re.fullmatch(PeriodicityFilter.periodicity_pattern, message.text).groups()
    await state.update_data({"recurrent_period": int(period), "recurrent_period_unit": period_unit})
    await message.answer("Provide the recurring transaction's start datetime in the 'YYYY-MM-DD HH:MM' format:")
    await state.set_state(RecurrentStates.waiting_for_recurrent_timestamp)


@router.message(
    RecurrentStates.waiting_for_recurrent_timestamp,
    DateTimeFilter()
)
async def recurrent_timestamp(message: Message, state: FSMContext, user: User, repo: Repository):
    timestamp = datetime.strptime(message.text, '%Y-%m-%d %H:%M')
    state_data = await state.get_data()
    name = state_data.get("recurrent_name")
    amount = state_data.get("recurrent_amount")
    storage_number = state_data.get("recurrent_storage_number")
    storage = await repo.get_storage_by_number_for_user(user_id=user.user_id, number=storage_number)
    category_number = state_data.get("recurrent_category_number")
    category = await repo.get_category_by_number_for_user(user_id=user.user_id, number=category_number)
    alpha_code = state_data.get("recurrent_currency")
    currency = await repo.get_currency_by_alpha_code(alpha_code=alpha_code)
    period = state_data.get("recurrent_period")
    period_unit = state_data.get("recurrent_period_unit")
    await repo.add_recurrent_transaction(
        user_id=user.user_id,
        storage_id=storage.storage_id,
        category_id=category.category_id,
        currency_id=currency.currency_id,
        name=name,
        amount=amount,
        start_timestamp=timestamp,
        period=period,
        period_unit=period_unit
    )
    await message.answer(f"Recurrent transaction '{name}' added successfully!")
