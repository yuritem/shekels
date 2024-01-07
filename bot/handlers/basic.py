# todo: i18n
import logging

from aiogram import Router
from aiogram.filters import CommandStart, Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.db.models import User
from bot.states import TransactionStates
from bot.filters.transaction import TransactionFilter


router: Router = Router()
logger = logging.getLogger(__name__)


@router.message(
    CommandStart(),
    StateFilter(None)
)
async def cmd_start(message: Message, state: FSMContext, session: AsyncSession):
    """Handles /start command"""
    user = User(
        chat_id=message.chat.id,
        telegram_id=message.from_user.id,
        user_firstname=message.from_user.first_name,
        banned=False
    )
    session.add(user)  # merge?!
    logger.info(f"Added {user} into database.")
    await message.answer("Start message.")
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
    """provided (user_id: int, category: str, storage: str, currency: str), we don't know if user used any aliases in the names, we need to get their IDs from database or to denote an error if we fail to do so
    
    
    
    categories_unaliased = (
        SELECT (category_id, category_name)
          FROM category
         WHERE category.user_id=`user_id`
    )
    categories_aliased = (
        SELECT (category_id, category_name, aliasable_id)
          FROM category
         WHERE category.user_id=`user_id`
           AND category.aliasable_id IS NOT NULL
    
    )
    
    category_id = ...
    
    """
    await message.answer("Operation processed.")


@router.message(Command("help"))
async def cmd_help(message: Message):
    """Handles /help command"""
    await message.answer("Help message.")


@router.message(Command("cancel"))
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
