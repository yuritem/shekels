# todo: middleware that provides User object if they are not banned

from typing import Callable, Awaitable, Dict, Any
from aiogram import BaseMiddleware
from aiogram.types import Message
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from bot.repo.repository import Repository


class UserMiddleware(BaseMiddleware):
    def __init__(self, session_pool: async_sessionmaker[AsyncSession]):
        super().__init__()
        self.session_pool = session_pool

    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            message: Message,
            data: Dict[str, Any],
    ) -> Any:
        # session: AsyncSession = data.get("session")
        repo: Repository = data.get("repo")
        telegram_id = message.from_user.id
        user = await repo.get_user(telegram_id=telegram_id)
        if not user.banned:
            data.update({"user": user})
            return await handler(message, data)
        else:
            pass  # todo: logging
