# todo: is PK primary key autoincrement flag excessive?

import datetime

from typing import List, Literal, get_args
from sqlalchemy import ForeignKey, Identity
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql.functions import current_timestamp
from sqlalchemy.dialects.postgresql import BIGINT, BOOLEAN, VARCHAR, INTEGER, MONEY, TIMESTAMP, ENUM

from bot.db.base import Base

AliasableSubtype = Literal["category", "storage", "currency"]


class User(Base):
    __tablename__ = "user"

    user_id: Mapped[int] = mapped_column(
        INTEGER,
        Identity(always=True, start=1, increment=1),
        primary_key=True,
        autoincrement=True
    )
    telegram_id: Mapped[int] = mapped_column(BIGINT, unique=True, nullable=False)
    chat_id: Mapped[int] = mapped_column(BIGINT, unique=True, nullable=False)
    first_name: Mapped[str] = mapped_column(VARCHAR(64), nullable=False)
    banned: Mapped[bool] = mapped_column(BOOLEAN, nullable=False)

    aliases: List["Alias"] = relationship("Alias", back_populates="user")
    categories: List["Category"] = relationship("Category", back_populates="user")
    storages: List["Storage"] = relationship("Storage", back_populates="user")
    transactions: List["Transaction"] = relationship("Transaction", back_populates="user")

    def __repr__(self) -> str:
        return (f"User(user_id={self.user_id!r}, telegram_id={self.telegram_id!r}, "
                f"chat_id={self.chat_id!r}, banned={self.banned!r})")


class Aliasable(Base):
    """Supertype for Category, Storage, and Currency"""
    __tablename__ = "aliasable"

    aliasable_id: Mapped[int] = mapped_column(
        INTEGER,
        Identity(always=True, start=1, increment=1),
        primary_key=True,
        autoincrement=True
    )
    aliasable_subtype: Mapped[AliasableSubtype] = mapped_column(
        ENUM(
            *get_args(AliasableSubtype),
            name="aliasable_subtype",
            create_type=True
        ),
        nullable=False
    )

    def __repr__(self) -> str:
        return f"Aliasable(aliasable_id={self.aliasable_id!r})"


class Alias(Base):
    __tablename__ = "alias"

    alias_id: Mapped[int] = mapped_column(
        INTEGER,
        Identity(always=True, start=1, increment=1),
        primary_key=True,
        autoincrement=True
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("user.user_id"))
    aliasable_id: Mapped[int] = mapped_column(ForeignKey("aliasable.aliasable_id"))
    alias_number: Mapped[int] = mapped_column(INTEGER, nullable=False)
    alias: Mapped[str] = mapped_column(VARCHAR(10), nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="aliases")

    def __repr__(self) -> str:
        return (f"Alias(alias_id={self.alias_id!r}), user_id={self.user_id!r}, "
                f"aliasable_id={self.aliasable_id!r}, alias_number={self.alias_number!r}, alias={self.alias!r}")


class Currency(Base):
    __tablename__ = "currency"

    currency_id: Mapped[int] = mapped_column(
        INTEGER,
        Identity(always=True, start=1, increment=1),
        primary_key=True,
        autoincrement=True
    )
    aliasable_id: Mapped[int] = mapped_column(ForeignKey("aliasable.aliasable_id"))
    name: Mapped[str] = mapped_column(VARCHAR(40), nullable=False)
    symbol: Mapped[str] = mapped_column(VARCHAR(5), nullable=False)  # unique?
    alpha_code: Mapped[str] = mapped_column(VARCHAR(3), unique=True, nullable=False)

    def __repr__(self) -> str:
        return (f"Currency(currency_id={self.currency_id!r}, aliasable_id={self.aliasable_id!r}, "
                f"name={self.name!r}, symbol={self.symbol!r}, alpha_code={self.alpha_code!r})")


class Storage(Base):
    __tablename__ = "storage"

    storage_id: Mapped[int] = mapped_column(
        INTEGER,
        Identity(always=True, start=1, increment=1),
        primary_key=True,
        autoincrement=True
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("user.user_id"))
    aliasable_id: Mapped[int] = mapped_column(ForeignKey("aliasable.aliasable_id"))
    storage_number: Mapped[int] = mapped_column(INTEGER, nullable=False)
    name: Mapped[str] = mapped_column(VARCHAR(40), nullable=False)
    is_credit: Mapped[bool] = mapped_column(BOOLEAN, nullable=False)
    multicurrency: Mapped[bool] = mapped_column(BOOLEAN, nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="storages")

    def __repr__(self) -> str:
        return (f"Storage(storage_id={self.storage_id!r}, user_id={self.user_id!r}, "
                f"aliasable_id={self.aliasable_id!r}, storage_number={self.storage_number!r}, name={self.name!r}")


class StorageCredit(Base):
    __tablename__ = "credit"

    storage_id: Mapped[int] = mapped_column(ForeignKey("storage.storage_id"), primary_key=True)
    due_day: Mapped[int] = mapped_column(INTEGER, nullable=False)  # todo: properly handle 30/31 and February (app-side)
    limit: Mapped[float] = mapped_column(MONEY, nullable=False)

    def __repr__(self):
        return (f"StorageCredit(storage_id={self.storage_id!r}, "
                f"due_day={self.due_day!r}, limit={self.limit!r})")


class StorageCurrency(Base):
    __tablename__ = "storage_currency"

    storage_id: Mapped[int] = mapped_column(ForeignKey("storage.storage_id"), primary_key=True, unique=True)
    currency_id: Mapped[int] = mapped_column(ForeignKey("currency.currency_id"), primary_key=True)

    def __repr__(self):
        return f"StorageCurrency(storage_id={self.storage_id!r}, currency_id={self.currency_id!r})"


class Category(Base):
    __tablename__ = "category"

    category_id: Mapped[int] = mapped_column(
        INTEGER,
        Identity(always=True, start=1, increment=1),
        primary_key=True,
        autoincrement=True
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("user.user_id"))
    aliasable_id: Mapped[int] = mapped_column(ForeignKey("aliasable.aliasable_id"))
    category_number: Mapped[int] = mapped_column(INTEGER, nullable=False)
    name: Mapped[str] = mapped_column(VARCHAR(40), nullable=False)
    factor_in: Mapped[bool] = mapped_column(BOOLEAN, nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="categories")

    def __repr__(self) -> str:
        return (f"Category(category_id={self.category_id!r}), user_id={self.user_id!r}, "
                f"aliasable_id={self.aliasable_id!r}, category_number={self.category_number!r}, name={self.name!r})")


class DefaultCurrency(Base):
    __tablename__ = "default_currency"

    user_id: Mapped[int] = mapped_column(ForeignKey("user.user_id"), primary_key=True, unique=True)
    currency_id: Mapped[int] = mapped_column(ForeignKey("currency.currency_id"), primary_key=True)

    def __repr__(self):
        return f"DefaultCurrency(user_id={self.user_id!r}, currency_id={self.currency_id!r})"


class DefaultCategory(Base):
    __tablename__ = "default_category"

    user_id: Mapped[int] = mapped_column(ForeignKey("user.user_id"), primary_key=True, unique=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("category.category_id"), primary_key=True)

    def __repr__(self):
        return f"DefaultCategory(user_id={self.user_id!r}, category_id={self.category_id!r})"


class DefaultStorage(Base):
    __tablename__ = "default_storage"

    user_id: Mapped[int] = mapped_column(ForeignKey("user.user_id"), primary_key=True, unique=True)
    storage_id: Mapped[int] = mapped_column(ForeignKey("storage.storage_id"), primary_key=True)

    def __repr__(self):
        return f"DefaultStorage(user_id={self.user_id!r}, storage_id={self.storage_id!r})"


class Transaction(Base):
    __tablename__ = "transaction"

    transaction_id: Mapped[int] = mapped_column(
        BIGINT,
        Identity(always=True, start=1, increment=1),
        primary_key=True,
        autoincrement=True
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("user.user_id"))
    storage_id: Mapped[int] = mapped_column(ForeignKey("storage.storage_id"))
    category_id: Mapped[int] = mapped_column(ForeignKey("category.category_id"))
    currency_id: Mapped[int] = mapped_column(ForeignKey("currency.currency_id"))
    timestamp: Mapped[datetime.datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=current_timestamp()
    )
    amount: Mapped[float] = mapped_column(MONEY, nullable=False)
    months: Mapped[int] = mapped_column(INTEGER, nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="transactions")

    def __repr__(self) -> str:
        return (f"Transaction(op_id={self.transaction_id!r}, user_id={self.user_id!r}, storage_id={self.storage_id!r}, "
                f"category_id={self.category_id!r}, currency_id={self.currency_id!r}, "
                f"timestamp={self.timestamp!r}, amount={self.amount!r}, months={self.months!r}")
