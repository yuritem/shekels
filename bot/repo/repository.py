from typing import Optional

from sqlalchemy import select, func, delete, update
from sqlalchemy.ext.asyncio import AsyncSession

from bot.db.models import (
    User,
    Aliasable,
    AliasableSubtype,
    Category,
    Storage,
    StorageCredit,
    StorageCurrency,
    Alias, Currency
)


class Repository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def _get_max_model_target_for_user(self, user_id: int, colname_target: str, model):
        # todo: Type-hint `model`
        column_target = getattr(model, colname_target)
        column_user_id = getattr(model, "user_id")

        stmt_get_last_record = (
            select(func.max(column_target))
            .where(column_user_id == user_id)
        )
        r = await self._session.execute(stmt_get_last_record)

        max_target = r.scalar()

        if max_target is None:
            max_target = 0

        return max_target

    async def _get_max_model_number_for_user(self, user_id: int, model) -> int:
        max_num = await self._get_max_model_target_for_user(
            user_id=user_id,
            colname_target="number",
            model=model
        )
        if max_num is None:
            max_num = 0
        return max_num

    async def _get_model_by_number_for_user(self, user_id: int, number: int, model):
        user_id_column = getattr(model, "user_id")
        number_column = getattr(model, "number")

        r = await self._session.execute(
            select(model)
            .where(
                user_id_column == user_id,
                number_column == number
            )
        )
        model_obj = r.scalar()
        return model_obj

    async def _get_model_for_user(self, user_id: int, model):
        user_id_column = getattr(model, "user_id")
        r = await self._session.execute(
            select(model)
            .where(user_id_column == user_id)
        )
        return r.scalars().all()

    async def _get_aliasable_id_by_currency_id(self, currency_id: int) -> int:
        r = await self._session.execute(
            select(Currency.aliasable_id)
            .where(Currency.currency_id == currency_id)
        )
        currency_id = r.scalar()
        return currency_id

    async def _add_aliasable(self, aliasable_subtype: AliasableSubtype) -> Aliasable:
        aliasable = Aliasable(aliasable_subtype=aliasable_subtype)
        return await self._session.merge(aliasable)

    async def _add_storage_credit(self, storage_id: int, billing_day: int) -> StorageCredit:
        storage_credit = StorageCredit(
            storage_id=storage_id,
            billing_day=billing_day
        )
        return await self._session.merge(storage_credit)

    async def _add_storage_currency(self, storage_id: int, currency_id: int) -> StorageCurrency:
        storage_currency = StorageCurrency(
            storage_id=storage_id,
            currency_id=currency_id
        )
        return await(self._session.merge(storage_currency))

    async def add_user(self, telegram_id: int, first_name: str, banned: bool) -> User:
        # todo: heresy, rewrite (how many times I'm adding categories and storages?)
        user = await self._session.merge(
            User(
                telegram_id=telegram_id,
                first_name=first_name,
                banned=banned
            )
        )
        category = await self.add_category(
            user_id=user.user_id,
            name="Uncategorized",
            factor_in=True
        )  # todo: set it default
        storage = await self.add_storage(
            user_id=user.user_id,
            name="Wallet",
            is_credit=False,
            multicurrency=True
        )  # todo: set it default

        user.categories.append(category)
        user.storages.append(storage)

        return await self._session.merge(user)

    async def get_user_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        r = await self._session.execute(
            select(User)
            .where(User.telegram_id == telegram_id)
        )
        user = r.scalar()
        return user

    async def add_category(self, user_id: int, name: str, factor_in: bool) -> Category:
        aliasable = await self._add_aliasable(aliasable_subtype="category")

        number = await self.get_max_category_number_for_user(user_id) + 1

        category = Category(
            user_id=user_id,
            aliasable_id=aliasable.aliasable_id,
            number=number,
            name=name,
            factor_in=factor_in
        )

        return await self._session.merge(category)

    async def update_category(self, user_id: int, number: int, name: str, factor_in: bool):
        await self._session.execute(
            update(Category)
            .where(
                Category.user_id == user_id,
                Category.number == number
            )
            .values({"name": name, "factor_in": factor_in})
        )

    async def delete_category(self, user_id: int, number: int):
        # todo: undeletable "uncategorized"
        # todo: what to do with Transaction table?
        # todo: delete aliasable
        # todo: return Category object (or change handler response)
        await self._session.execute(
            delete(Category)
            .where(
                Category.user_id == user_id,
                Category.number == number
            )
        )

    async def set_default_category(self, user_id: int, number: int):
        pass  # todo!

    async def get_categories_for_user(self, user_id: int):
        return await self._get_model_for_user(user_id, model=Category)

    async def get_category_by_number_for_user(self, user_id: int, number: int):
        return await self._get_model_by_number_for_user(user_id, number, model=Category)

    async def get_max_category_number_for_user(self, user_id: int) -> int:
        return await self._get_max_model_number_for_user(user_id, model=Category)

    async def add_storage(
            self,
            user_id: int,
            name: str,
            is_credit: bool,
            multicurrency: bool,
            billing_day: Optional[int] = None,
            currency_id: Optional[int] = None
    ) -> Storage:
        if is_credit:
            if billing_day is None:
                raise ValueError("`billing_day` not provided for `is_credit` Storage")
        if not multicurrency:
            if currency_id is None:
                raise ValueError("`currency_id` not provided for Storage with multicurrency=False")

        aliasable = await self._add_aliasable(aliasable_subtype="storage")

        number = await self.get_max_storage_number_for_user(user_id) + 1

        storage = Storage(
            user_id=user_id,
            aliasable_id=aliasable.aliasable_id,
            number=number,
            name=name,
            is_credit=is_credit,
            multicurrency=multicurrency
        )

        storage = await self._session.merge(storage)

        if is_credit:
            await self._add_storage_credit(
                storage_id=storage.storage_id,
                billing_day=billing_day
            )
        if not multicurrency:
            await self._add_storage_currency(
                storage_id=storage.storage_id,
                currency_id=currency_id
            )

        return storage

    async def upadte_storage(self, user_id: int, number: int, name: str):
        await self._session.execute(
            update(Storage)
            .where(
                Storage.user_id == user_id,
                Storage.number == number
            )
            .values({"name": name})
        )

    async def delete_storage(self, user_id: int, number: int):
        # todo: undeletable "wallet"
        # todo: what to do with Transaction table?
        # todo: delete aliasable
        # todo: return Storage object (or change handler response)
        await self._session.execute(
            delete(Storage)
            .where(
                Storage.user_id == user_id,
                Storage.number == number
            )
        )

    async def set_default_storage(self, user_id: int, number: int):
        pass  # todo!

    async def get_storages_for_user(self, user_id: int):
        return await self._get_model_for_user(user_id, model=Storage)

    async def get_storage_by_number_for_user(self, user_id: int, number: int):
        return await self._get_model_by_number_for_user(user_id, number, model=Storage)

    async def get_max_storage_number_for_user(self, user_id: int) -> int:
        return await self._get_max_model_number_for_user(user_id, model=Storage)

    async def add_alias(
            self,
            user_id: int,
            subtype: AliasableSubtype,
            name: str,
            aliasable_number: Optional[int] = None,
            currency_id: Optional[int] = None
    ) -> Alias:
        if subtype == 'currency':
            if currency_id is None:
                raise ValueError(f"`currency_id` not provided for `{subtype}` alias")
            aliasable_id = self._get_aliasable_id_by_currency_id(currency_id)
        elif subtype in ['category', 'storage']:
            if aliasable_number is None:
                raise ValueError(f"`aliasable_number` not provided for `{subtype}` alias")
            if subtype == 'storage':
                storage = await self.get_storage_by_number_for_user(user_id=user_id, number=aliasable_number)
                aliasable_id = storage.aliasable_id
            else:
                category = await self.get_category_by_number_for_user(user_id=user_id, number=aliasable_number)
                aliasable_id = category.aliasable_id
        else:
            raise ValueError(f"Aliasable subtype '{subtype}' is not supported")

        number = await self.get_max_alias_number_for_user(user_id=user_id) + 1

        alias = Alias(
            user_id=user_id,
            aliasable_id=aliasable_id,
            number=number,
            name=name
        )

        return await self._session.merge(alias)

    async def delete_alias(self, user_id: int, number: int):
        await self._session.execute(
            delete(Alias)
            .where(
                Alias.user_id == user_id,
                Alias.number == number
            )
        )

    async def get_aliases_for_user(self, user_id: int):
        return await self._get_model_for_user(user_id, model=Alias)

    async def get_max_alias_number_for_user(self, user_id: int) -> int:
        return await self._get_max_model_number_for_user(user_id, model=Alias)

    async def get_currency_by_alpha_code(self, alpha_code: str) -> Optional[Currency]:
        r = await self._session.execute(
            select(Currency)
            .where(Currency.alpha_code == alpha_code)
        )
        currency = r.scalar()
        return currency
