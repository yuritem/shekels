from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot.db.models import User
from bot.filters.filters import IntegerFilter, NameFilter, YesNoFilter, DayOfTheMonthFilter
from bot.services.repository import Repository
from bot.states import StorageStates, TransactionStates
from bot.utils.list_models import get_storage_list

router = Router()


@router.message(
    Command("list_storages"),
    TransactionStates.waiting_for_new_transaction
)
async def cmd_list_storages(message: Message, repo: Repository, user: User):
    """Handles /list_storages command"""
    storages_str = await get_storage_list(user.user_id, repo)
    if storages_str:
        await message.answer(f"List of storages:\n\n{storages_str}")
    else:
        await message.answer("No storages yet.")


@router.message(
    Command("add_storage"),
    TransactionStates.waiting_for_new_transaction
)
async def cmd_add_storage(message: Message, state: FSMContext):
    """Handles /add_storage command"""
    await message.answer("New storage name:")
    await state.set_state(StorageStates.waiting_for_new_storage_name)


@router.message(
    StorageStates.waiting_for_new_storage_name,
    NameFilter()
)
async def storage_name_to_add(message: Message, state: FSMContext):
    """Handles storage_name entry after /add_storage command"""
    storage_name = message.text
    await state.update_data({"storage_name": storage_name})
    await message.answer("Does this storage have a billing day?")
    await state.set_state(StorageStates.waiting_for_new_storage_is_credit_flag)


@router.message(
    StorageStates.waiting_for_new_storage_is_credit_flag,
    YesNoFilter()
)
async def storage_is_credit(message: Message, state: FSMContext):
    """Handles storage_is_credit entry in the process of /add_storage command"""
    is_credit = YesNoFilter.map[message.text.lower()]
    await state.update_data({"is_credit": is_credit})
    if is_credit:
        await message.answer("Billing day of the month:")
        await state.set_state(StorageStates.waiting_for_new_storage_billing_day)
    else:
        await message.answer("Is this storage multicurrency?")
        await state.set_state(StorageStates.waiting_for_new_storage_multicurrency_flag)


@router.message(
    StorageStates.waiting_for_new_storage_billing_day,
    DayOfTheMonthFilter()
)
async def storage_billing_day(message: Message, state: FSMContext):
    """Handles storage_billing_day entry in the process of /add_storage command"""
    billing_day = int(message.text)
    await state.update_data({"billing_day": billing_day})
    await message.answer("Is this storage multicurrency?")
    await state.set_state(StorageStates.waiting_for_new_storage_multicurrency_flag)


@router.message(
    StorageStates.waiting_for_new_storage_multicurrency_flag,
    YesNoFilter()
)
async def storage_multicurrency(message: Message, state: FSMContext, repo: Repository, user: User):
    """Handles storage_multicurrency entry in the process of /add_storage command"""
    multicurrency = YesNoFilter.map[message.text.lower()]
    if multicurrency:
        state_data = await state.get_data()
        is_credit = state_data.get("is_credit")
        billing_day = state_data.get("billing_day", None)
        storage_name = state_data.get("storage_name")
        await repo.add_storage(
            user_id=user.user_id,
            name=storage_name,
            is_credit=is_credit,
            multicurrency=multicurrency,
            billing_day=billing_day
        )
        await message.answer(f"Storage '{storage_name}' created!")
        await state.set_state(TransactionStates.waiting_for_new_transaction)
    else:
        await state.update_data({"multicurrency": multicurrency})
        await message.answer("Currency 3-letter alphacode:")
        await state.set_state(StorageStates.waiting_for_new_storage_currency_alphacode)


@router.message(StorageStates.waiting_for_new_storage_currency_alphacode)
async def storage_currency_alpha_code(message: Message, state: FSMContext, repo: Repository, user: User):
    """Handles storage_currency_alpha_code entry in the process of /add_storage command"""
    alpha_code = message.text.upper()
    currency = await repo.get_currency_by_alpha_code(alpha_code=alpha_code)
    if currency:
        state_data = await state.get_data()
        is_credit = state_data.get("is_credit")
        billing_day = state_data.get("billing_day", None)
        storage_name = state_data.get("storage_name")
        multicurrency = state_data.get("multicurrency")
        await repo.add_storage(
            user_id=user.user_id,
            name=storage_name,
            is_credit=is_credit,
            multicurrency=multicurrency,
            billing_day=billing_day,
            currency_id=currency.currency_id
        )
        await message.answer(f"Storage '{storage_name}' created!")
        await state.set_state(TransactionStates.waiting_for_new_transaction)
    else:
        pass  # Filter behavior


@router.message(
    Command("edit_storage"),
    TransactionStates.waiting_for_new_transaction
)
async def cmd_edit_storage(message: Message, state: FSMContext, repo: Repository, user: User):
    """Handles /edit_storage command"""
    storages_str = await get_storage_list(user.user_id, repo)
    if storages_str:
        await message.answer(f"Provide storage number to edit:\n\n{storages_str}")
        await state.set_state(StorageStates.waiting_for_storage_number_to_edit)
    else:
        await message.answer("No storages yet.")


@router.message(
    StorageStates.waiting_for_storage_number_to_edit,
    IntegerFilter()
)
async def storage_number_to_edit(message: Message, state: FSMContext, repo: Repository, user: User):
    """Handles storage_number entry in the process of /edit_storage command"""
    storage_number = int(message.text)
    storage = await repo.get_storage_by_number_for_user(user_id=user.user_id, number=storage_number)
    if storage:
        await state.update_data({"storage_number": storage_number})
        await message.answer("New storage name:")
        await state.set_state(StorageStates.waiting_for_edited_storage_name)
    else:
        pass  # Filter behavior


@router.message(
    StorageStates.waiting_for_edited_storage_name,
    NameFilter()
)
async def storage_name_to_edit(message: Message, state: FSMContext, repo: Repository, user: User):
    """Handles storage_name_to_edit in the process of /edit_storage command"""
    state_data = await state.get_data()
    storage_number = state_data.get("storage_number")
    storage_name = message.text
    await repo.update_storage_by_number_for_user(user_id=user.user_id, number=storage_number, name=storage_name)
    await message.answer("Storage edited!")
    await state.set_state(TransactionStates.waiting_for_new_transaction)


@router.message(
    Command("delete_storage"),
    TransactionStates.waiting_for_new_transaction
)
async def cmd_delete_storage(message: Message, state: FSMContext, repo: Repository, user: User):
    """Handles /delete_storage command"""
    storages_str = await get_storage_list(user.user_id, repo)
    if storages_str:
        await message.answer(f"Provide storage number to delete:\n\n{storages_str}")
        await state.set_state(StorageStates.waiting_for_storage_number_to_delete)
    else:
        await message.answer("No storages yet.")


@router.message(
    StorageStates.waiting_for_storage_number_to_delete,
    IntegerFilter()
)
async def storage_number_to_delete(message: Message, state: FSMContext, repo: Repository, user: User):
    """Handles storage_number entry after /delete_storage command"""
    storage_number = int(message.text)
    storage = await repo.get_storage_by_number_for_user(user_id=user.user_id, number=storage_number)
    if storage:
        await repo.delete_storage_by_number_for_user(user_id=user.user_id, number=storage_number)
        await message.answer(f"Storage deleted.")
        await state.set_state(TransactionStates.waiting_for_new_transaction)
    else:
        pass  # Filter behavior


@router.message(
    Command("set_default_storage"),
    TransactionStates.waiting_for_new_transaction
)
async def cmd_set_default_storage(message: Message, state: FSMContext, repo: Repository, user: User):
    """Handles /set_default_storage command"""
    storages_str = await get_storage_list(user.user_id, repo)
    if storages_str:
        await message.answer(f"Provide storage number to set as default:\n\n{storages_str}")
        await state.set_state(StorageStates.waiting_for_storage_number_to_set_default)
    else:
        await message.answer("No storages yet.")


@router.message(
    StorageStates.waiting_for_storage_number_to_set_default,
    IntegerFilter()
)
async def storage_number_to_set_default(message: Message, state: FSMContext, repo: Repository, user: User):
    """Handles storage_number entry after /set_default_storage command"""
    storage_number = int(message.text)
    storage = await repo.get_storage_by_number_for_user(user_id=user.user_id, number=storage_number)
    if storage:
        storage = await repo.set_default_storage(user.user_id, number=storage_number)
        await message.answer(f"Storage '{storage.name}' is now default!")
        await state.set_state(TransactionStates.waiting_for_new_transaction)
    else:
        pass  # Filter behavior
