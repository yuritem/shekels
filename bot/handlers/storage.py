from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot.states import StorageStates, TransactionStates

router = Router()


@router.message(
    Command("add_storage"),
    TransactionStates.waiting_for_new_transaction
)
async def cmd_add_storage(message: Message, state: FSMContext):
    """Handles /add_storage command"""
    await message.answer("Provide storage name.")
    await state.set_state(StorageStates.waiting_for_new_storage_name)
    ...  # storage type selection (second stage)


@router.message(StorageStates.waiting_for_new_storage_name)
async def storage_name_to_add(message: Message, state: FSMContext):
    """Handles storage_name entry after /add_storage command"""
    await message.answer("Provide storage_type.")
    await state.set_state(StorageStates.waiting_for_new_storage_storage_type)


@router.message(StorageStates.waiting_for_new_storage_storage_type)
async def storage_storage_type(message: Message, state: FSMContext):
    """Handles storage_storage_type entry in the process of /add_storage command"""
    await message.answer("Storage creation processed.")
    await state.set_state(TransactionStates.waiting_for_new_transaction)


@router.message(
    Command("edit_storage"),
    TransactionStates.waiting_for_new_transaction
)
async def cmd_edit_storage(message: Message, state: FSMContext):
    """Handles /edit_storage command"""
    await message.answer("Provide storage number to edit.")
    await state.set_state(StorageStates.waiting_for_storage_number_to_edit)


@router.message(StorageStates.waiting_for_storage_number_to_edit)
async def storage_number_to_edit(message: Message, state: FSMContext):
    """Handles storage_number entry in the process of /edit_storage command"""
    await message.answer("Provide new storage name.")
    await state.set_state(StorageStates.waiting_for_edited_storage_name)


@router.message(StorageStates.waiting_for_edited_storage_name)
async def storage_name_to_edit(message: Message, state: FSMContext):
    """Handles storage_name_to_edit in the process of /edit_storage command"""
    await message.answer("Storage edit processed.")
    await state.set_state(TransactionStates.waiting_for_new_transaction)


@router.message(
    Command("delete_storage"),
    TransactionStates.waiting_for_new_transaction
)
async def cmd_delete_storage(message: Message, state: FSMContext):
    """Handles /delete_storage command"""
    await message.answer("Provide storage number to delete.")  # todo: behaviour for DB?
    await state.set_state(StorageStates.waiting_for_storage_number_to_delete)
    ...


@router.message(StorageStates.waiting_for_storage_number_to_delete)
async def storage_number_to_delete(message: Message, state: FSMContext):
    """Handles storage_number entry after /delete_storage command"""
    await message.answer("Storage deletion processed.")
    await state.set_state(TransactionStates.waiting_for_new_transaction)
