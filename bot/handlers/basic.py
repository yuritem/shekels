# todo: i18n
import logging

from aiogram import Router
from aiogram.filters import CommandStart, Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

# from bot.db.models import User
# from bot.services.repository import Repository
from bot.states import TransactionStates
from bot.filters.filters import TransactionFilter, YesNoFilter, NotWaitingForTransactionFilter

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
async def transaction(message: Message):
    """
    Handles transactions: standard storage transaction / money transfer between storages / installment payment
    :param message: Telegram message
    """
    # todo: db
    """
    provided (user_id: int, category: str, storage: str, currency: str),
    we don't know if user used any aliases in the names, we need to get their IDs from database
    or throw an error if we fail
    """
    await message.answer("Transaction processed.")


@router.message(
    Command("help"),
    TransactionStates.waiting_for_new_transaction
)
async def cmd_help(message: Message):
    """Handles /help command"""
    await message.answer("Category & Storage names format (under 40 characters):\n"
                         "1+ words consisting of letters, numbers, '-', and '_' separated with spaces.\n\n"
                         "All yes/no entry format - one of the following (case insensitive):\n"
                         f"{', '.join(YesNoFilter.map.keys())}\n"
                         "Aliases: 1 word consisting of letters and numbers (under 10 characters)")  # todo


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
    # todo: db
    await message.answer("Balance message.")
