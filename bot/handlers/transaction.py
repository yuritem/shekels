from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from bot.db.models import User
from bot.services.repository import Repository
from bot.states import TransactionStates
from bot.utils.list_models import get_transaction_list

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
    await message.answer("Provide name of the recurrent transaction")
    await state.set_state()
