import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
# from aiogram.fsm.storage.memory import SimpleEventIsolation
from aiogram.fsm.storage.redis import RedisStorage, DefaultKeyBuilder
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from bot.db.base import Base
from bot.config import config
from bot.middlewares.db import DatabaseSessionMiddleware
from bot.middlewares.user import UserMiddleware
from bot.handlers import basic, category, alias, storage, currency, transaction
from bot.set_commands import set_commands
from bot.utils.db import init_database, drop_all_tables
from bot.utils.log import setup_logging


async def main():
    engine = create_async_engine(
        url=config.POSTGRES_DSN.unicode_string(),
        echo=False,
        connect_args={"server_settings": {"jit": "off"}},
    )

    sessionmaker = async_sessionmaker(
        engine,
        expire_on_commit=False
    )
    if config.RESET_POSTGRES_ON_STARTUP:
        await drop_all_tables(engine=engine)
    await init_database(metadata=Base.metadata, engine=engine, session_pool=sessionmaker)

    redis_storage = RedisStorage.from_url(
        config.REDIS_DSN.unicode_string(),
        key_builder=DefaultKeyBuilder(with_bot_id=True)
    )
    if config.RESET_REDIS_ON_STARTUP:
        await redis_storage.redis.flushdb()

    dp = Dispatcher(
        storage=redis_storage,
        events_isolation=redis_storage.create_isolation()
        # events_isolation=SimpleEventIsolation()
    )

    dp.update.middleware(DatabaseSessionMiddleware(session_pool=sessionmaker))
    dp.message.middleware(UserMiddleware())
    dp.include_routers(
        basic.router,
        category.router,
        alias.router,
        storage.router,
        currency.router,
        transaction.router
    )

    bot = Bot(token=config.BOT_TOKEN.get_secret_value(), default=DefaultBotProperties(parse_mode="HTML"))
    await set_commands(bot)

    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    setup_logging(config=config)
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    asyncio.get_event_loop().run_until_complete(main())
