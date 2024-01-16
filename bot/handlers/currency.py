from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot.db.models import User
from bot.services.repository import Repository
from bot.states import CurrencyStates, TransactionStates

router = Router()


@router.message(
    Command("set_default_currency"),
    TransactionStates.waiting_for_new_transaction
)
async def cmd_set_default_currency(message: Message, state: FSMContext):
    """Handles /set_default_currency command"""
    await message.answer("Currency 3-letter alphacode:")
    await state.set_state(CurrencyStates.waiting_for_currency_alphacode)


@router.message(CurrencyStates.waiting_for_currency_alphacode)
async def currency_alphacode(message: Message, state: FSMContext, repo: Repository, user: User):
    """Handles currency_alphacode entry in the process of /add_alias command"""
    alpha_code = message.text.upper()
    currency = await repo.get_currency_by_alpha_code(alpha_code)
    if currency:
        await repo.set_default_currency(user.user_id, alpha_code)
        await message.answer(f"Currency '{currency.name}' ({currency.alpha_code}) is now default!")
        await state.set_state(TransactionStates.waiting_for_new_transaction)
    else:
        pass  # Filter behavior
