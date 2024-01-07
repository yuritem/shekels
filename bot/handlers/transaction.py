from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from bot.states import TransactionStates
from bot.filters import TransactionFilter

router = Router()


@router.message(
    Command("edit_op"),
    TransactionStates.waiting_for_new_transaction
)
async def cmd_edit_transaction(message: Message, state: FSMContext):
    """Handles /edit_transaction command"""
    raise NotImplementedError


@router.message(
    Command("delete_op"),
    TransactionStates.waiting_for_new_transaction
)
async def cmd_delete_transaction(message: Message, state: FSMContext):
    """Handles /delete_transaction command"""
    raise NotImplementedError
