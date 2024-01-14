import logging
from typing import Callable, Awaitable, Dict, Any
from aiogram import BaseMiddleware
from aiogram.types import Message

from bot.services.repository import Repository

logger = logging.getLogger(__name__)


class UserMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            message: Message,
            data: Dict[str, Any]
    ) -> Any:
        repo: Repository = data.get("repo")
        telegram_id = message.from_user.id
        user = await repo.get_user_by_telegram_id(telegram_id=telegram_id)
        logger.info(f"Got message by {user}")
        if not user:
            first_name = message.from_user.first_name
            user = await repo.add_user(telegram_id=telegram_id, first_name=first_name, banned=False)
            logger.info(f"Added {user} into database.")
        if not user.banned:
            data.update({"user": user})
            return await handler(message, data)
        else:
            pass  # todo: log: banned user tried to access db
            # todo: ban filter on update middleware?
