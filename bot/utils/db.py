import json
import logging
import os

from typing import List, Dict, Union
from sqlalchemy import MetaData, inspect
from sqlalchemy.schema import ForeignKeyConstraint, Table, DropConstraint, DropTable
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, AsyncEngine
from sqlalchemy.sql.expression import func
from sqlalchemy.dialects.postgresql import insert

from bot.db.models import Currency, Aliasable
from bot.config import CURRENCY_DATA_PATH

logger = logging.getLogger(__name__)


async def get_table_names(engine: AsyncEngine) -> List[str]:
    async with engine.begin() as conn:
        # 'conn.run_sync(callable)' passes conn as the first argument to the callable
        return await conn.run_sync(lambda conn_: inspect(conn_).get_table_names())


def get_currency_data(currency_json_path: Union[os.PathLike, str, bytes] = CURRENCY_DATA_PATH) -> List[Dict]:
    with open(currency_json_path, 'r', encoding='utf-8') as fh:
        currency_data = json.load(fh)
    return currency_data


async def init_database(
        metadata: MetaData,
        engine: AsyncEngine,
        session_pool: async_sessionmaker[AsyncSession]
) -> None:
    table_names = await get_table_names(engine=engine)
    if not table_names:
        logger.info("Creating all tables...")
        async with engine.begin() as conn:
            await conn.run_sync(metadata.create_all)
        logger.info("All tables are created.")
        async with session_pool.begin() as session:
            currency_data = get_currency_data()
            logger.info("Inserting `currency` data...")
            for _, currency_values in enumerate(currency_data):
                res = await session.execute(insert(Aliasable).values({"aliasable_subtype": "currency"}))
                id_inserted = res.inserted_primary_key[0]  # returned_defaults[0]
                await session.execute(insert(Currency).values({"aliasable_id": id_inserted} | currency_values))
            logger.info("Populated `currency` with data.")
    else:
        logger.info("Tables are already created.")


async def drop_all_tables(engine: AsyncEngine):
    logger.info("Dropping all tables...")
    async with engine.begin() as conn:
        table_names = await get_table_names(engine=engine)
        meta = MetaData()
        tables = []
        all_fkeys = []
        for table_name in table_names:
            fkeys = []
            foreign_keys = await conn.run_sync(lambda conn_: inspect(conn_).get_foreign_keys(table_name))
            for fkey in foreign_keys:
                if not fkey["name"]:
                    continue
                fkeys.append(ForeignKeyConstraint(columns=(), refcolumns=(), name=fkey["name"]))
            tables.append(Table(table_name, meta, *fkeys))
            all_fkeys.extend(fkeys)
        for fkey in all_fkeys:
            await conn.execute(DropConstraint(fkey))
        for table in tables:
            await conn.execute(DropTable(table))
    logger.info("Dropped all tables.")


async def get_last_row(session: AsyncSession, table: Table):
    primary_keys = inspect(table).primary_key
    if len(primary_keys) > 1:
        raise ValueError("Table got more than 1 primary key.")
    stmt = func.max()
    res = await session.execute(stmt)
