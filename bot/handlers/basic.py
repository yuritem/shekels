import logging

from aiogram import Router
from aiogram.filters import CommandStart, Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot.db.models import User
from bot.services.repository import Repository
# from bot.db.models import User
# from bot.services.repository import Repository
from bot.states import TransactionStates
from bot.filters.filters import TransactionFilter, YesNoFilter, NotWaitingForTransactionFilter
from bot.utils.parse_transaction import parse_and_add_transactions

router: Router = Router()
logger = logging.getLogger(__name__)


@router.message(
    CommandStart(),
    StateFilter(None)
)
async def cmd_start(message: Message, state: FSMContext):
    """Handles /start command"""
    await message.answer("Welcome!")
    await state.set_state(TransactionStates.waiting_for_new_transaction)


@router.message(
    TransactionStates.waiting_for_new_transaction,
    TransactionFilter()
)
async def transaction(message: Message, repo: Repository, user: User):
    """
    Handles transactions: standard storage transaction / money transfer between storages / installment payment
    """
    await parse_and_add_transactions(message.text, user_id=user.user_id, repo=repo)
    await message.answer("Transaction added!")
    transactions = await repo.get_transactions_for_user(user_id=user.user_id)
    await message.answer('\n'.join(map(str, transactions)))
    """
    provided (user_id: int, category: str, storage: str, currency: str),
    we don't know if user used any aliases in the names, we need to get their IDs from database
    or raise an error if we fail
    """


@router.message(
    Command("help"),
    TransactionStates.waiting_for_new_transaction
)
async def cmd_help(message: Message):
    """Handles /help command"""
    await message.answer(
        "Formats:\n\n"
        "Categories & Storages: word consisting of letters, numbers, '-', and '_' (under 40 characters):\n\n"
        "yes/no entry format - one of the following (case insensitive):\n"
        f"{', '.join(YesNoFilter.map.keys())}\n\n"
        "Aliases: word consisting of letters and numbers (under 40 characters)"
    )  # todo


@router.message(
    Command("cancel"),
    NotWaitingForTransactionFilter()
)
async def cmd_cancel(message: Message, state: FSMContext):
    """Handles /cancel command"""
    await message.answer("Cancelled.")
    await state.set_state(TransactionStates.waiting_for_new_transaction)


@router.message(
    Command("balance"),
    TransactionStates.waiting_for_new_transaction
)
async def cmd_balance(message: Message):
    """Handles /balance command"""

    await message.answer("TBS")


@router.message(
    Command("report"),
    TransactionStates.waiting_for_new_transaction
)
async def cmd_report(message: Message):
    """Handles /report command"""
    await message.answer("TBS")
