from typing import Optional, Type, Union, List, Dict, Sequence

from sqlalchemy import select, func, delete, update, union
from sqlalchemy.ext.asyncio import AsyncSession

from bot.db.models import (
    User,
    Aliasable,
    AliasableSubtype,
    Category,
    Storage,
    StorageCredit,
    StorageCurrency,
    Alias,
    Currency,
    UserDefault, Transaction
)


class Repository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def _get_max_model_target_for_user(self, user_id: int, colname_target: str, model: Type[Union[Category, Alias, Storage]]):
        column_target = getattr(model, colname_target)
        column_user_id = getattr(model, "user_id")

        stmt_get_last_record = (
            select(func.max(column_target))
            .where(column_user_id == user_id)
        )
        r = await self.session.execute(stmt_get_last_record)

        max_target = r.scalar()

        return max_target

    async def _get_max_model_number_for_user(self, user_id: int, model: Type[Union[Category, Alias, Storage]]) -> int:
        max_num = await self._get_max_model_target_for_user(
            user_id=user_id,
            colname_target="number",
            model=model
        )
        if max_num is None:
            max_num = 0
        return max_num

    async def _get_model_by_number_for_user(self, user_id: int, number: int, model: Type[Union[Category, Alias, Storage]]) -> Union[Category, Alias, Storage]:
        user_id_column = getattr(model, "user_id")
        number_column = getattr(model, "number")

        r = await self.session.execute(
            select(model)
            .where(
                user_id_column == user_id,
                number_column == number
            )
        )
        model_instance = r.scalar()
        return model_instance

    async def _get_model_for_user(self, user_id: int, model: Type[Union[Category, Alias, Storage]]) -> Sequence[Union[Category, Alias, Storage]]:
        if not hasattr(model, "user_id"):
            raise ValueError(f"Model {model.__class__} does not define a column named 'user_id'")
        if not hasattr(model, "number"):
            raise ValueError(f"Model {model.__class__} does not define a column named 'number'")
        r = await self.session.execute(
            select(model)
            .where(model.user_id == user_id)
            .order_by(model.number)
        )
        return r.scalars().all()

    async def _get_aliasable_id_by_currency_id(self, currency_id: int) -> int:
        r = await self.session.execute(
            select(Currency.aliasable_id)
            .where(Currency.currency_id == currency_id)
        )
        currency_id = r.scalar()
        return currency_id

    async def _refresh_model_numbers_for_user(self, user_id: int, model: Type[Union[Category, Alias, Storage]]) -> None:
        if not hasattr(model, "number"):
            raise ValueError(f"Model {model.__class__} does not define a column named 'number'")
        model_instances = await self._get_model_for_user(user_id, model=model)
        for n, model_instance in enumerate(model_instances):
            model_instance.number = n + 1
            await self.session.merge(model_instance)

    async def _add_aliasable(self, aliasable_subtype: AliasableSubtype) -> Aliasable:
        aliasable = Aliasable(aliasable_subtype=aliasable_subtype)
        return await self.session.merge(aliasable)

    async def _delete_aliasable(self, aliasable_id) -> None:
        await self.session.execute(
            delete(Aliasable)
            .where(Aliasable.aliasable_id == aliasable_id)
        )

    async def _add_storage_credit(self, storage_id: int, billing_day: int) -> StorageCredit:
        storage_credit = StorageCredit(
            storage_id=storage_id,
            billing_day=billing_day
        )
        return await self.session.merge(storage_credit)

    async def _add_storage_currency(self, storage_id: int, currency_id: int) -> StorageCurrency:
        storage_currency = StorageCurrency(
            storage_id=storage_id,
            currency_id=currency_id
        )
        return await self.session.merge(storage_currency)

    async def _upsert_user_default(
            self,
            user_id: int,
            category_id: Optional[int] = None,
            storage_id: Optional[int] = None,
            currency_id: Optional[int] = None
    ) -> UserDefault:
        user_default = await self.get_user_default(user_id)

        if user_default is None:
            user_default = UserDefault(
                user_id=user_id,
                category_id=category_id,
                storage_id=storage_id,
                currency_id=currency_id
            )
        else:
            if category_id is not None:
                user_default.category_id = category_id
            if storage_id is not None:
                user_default.storage_id = storage_id
            if currency_id is not None:
                user_default.currency_id = currency_id

        return await self.session.merge(user_default)

    async def add_user(self, telegram_id: int, first_name: str, banned: bool) -> User:
        user = User(
            telegram_id=telegram_id,
            first_name=first_name,
            banned=banned
        )
        return await self.session.merge(user)

    async def get_user_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        r = await self.session.execute(
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

        return await self.session.merge(category)

    async def get_categories_for_user(self, user_id: int) -> Sequence[Category]:
        return await self._get_model_for_user(user_id, model=Category)

    async def get_category_by_number_for_user(self, user_id: int, number: int) -> Category:
        return await self._get_model_by_number_for_user(user_id, number, model=Category)

    async def get_max_category_number_for_user(self, user_id: int) -> int:
        return await self._get_max_model_number_for_user(user_id, model=Category)

    async def update_category(self, user_id: int, number: int, name: str, factor_in: bool) -> None:
        await self.session.execute(
            update(Category)
            .where(
                Category.user_id == user_id,
                Category.number == number
            )
            .values({"name": name, "factor_in": factor_in})
        )

    async def refresh_category_numbers_for_user(self, user_id: int) -> None:
        await self._refresh_model_numbers_for_user(user_id, model=Category)

    async def delete_category(self, user_id: int, number: int) -> None:
        # todo: what to do with Transaction table?
        category = await self.get_category_by_number_for_user(user_id, number)
        await self._delete_aliasable(category.aliasable_id)
        await self.session.delete(category)
        await self.session.flush()
        await self.refresh_category_numbers_for_user(user_id)

    async def set_default_category(self, user_id: int, number: int) -> Category:
        category = await self.get_category_by_number_for_user(user_id, number)
        await self._upsert_user_default(user_id, category_id=category.category_id)
        return category

    async def get_default_category_for_user(self, user_id: int) -> Optional[Category]:
        user_default = await self.get_user_default(user_id)
        if user_default.category_id:
            category = self.session.get(Category, user_default.category_id)
            return await category
        else:
            return None

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
        storage = await self.session.merge(storage)
        await self.session.flush()

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

    async def get_storages_for_user(self, user_id: int) -> Sequence[Storage]:
        return await self._get_model_for_user(user_id, model=Storage)

    async def get_storage_by_number_for_user(self, user_id: int, number: int) -> Storage:
        return await self._get_model_by_number_for_user(user_id, number, model=Storage)

    async def get_max_storage_number_for_user(self, user_id: int) -> int:
        return await self._get_max_model_number_for_user(user_id, model=Storage)

    async def upadte_storage(self, user_id: int, number: int, name: str) -> None:
        await self.session.execute(
            update(Storage)
            .where(
                Storage.user_id == user_id,
                Storage.number == number
            )
            .values({"name": name})
        )

    async def refresh_storage_numbers_for_user(self, user_id: int) -> None:
        await self._refresh_model_numbers_for_user(user_id, model=Storage)

    async def delete_storage(self, user_id: int, number: int) -> None:
        # todo: what to do with Transaction table?
        storage = await self.get_storage_by_number_for_user(user_id, number)
        await self._delete_aliasable(storage.aliasable_id)
        await self.session.delete(storage)
        await self.session.flush()
        await self.refresh_storage_numbers_for_user(user_id)

    async def set_default_storage(self, user_id: int, number: int) -> Storage:
        storage = await self.get_storage_by_number_for_user(user_id, number)
        await self._upsert_user_default(user_id, storage_id=storage.storage_id)
        return storage

    async def get_default_storage_for_user(self, user_id: int) -> Optional[Storage]:
        user_default = await self.get_user_default(user_id)
        if user_default.storage_id:
            storage = self.session.get(Storage, user_default.storage_id)
            return await storage
        else:
            return None

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
            aliasable_id = await self._get_aliasable_id_by_currency_id(currency_id)
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

        return await self.session.merge(alias)

    async def get_aliases_for_user(self, user_id: int) -> Sequence[Alias]:
        return await self._get_model_for_user(user_id, model=Alias)

    async def get_alias_by_number_for_user(self, user_id: int, number: int) -> Alias:
        return await self._get_model_by_number_for_user(user_id, number, model=Alias)

    async def get_aliases_with_full_names_for_user(self, user_id: int) -> List[Dict]:
        """
        Returns a list of aliases for user with user_id in the following format:
        {"alias_number": w, "alias_name": x, "aliasable_subtype": y, "name": z}
        """

        alias_user = (
            select(Alias.aliasable_id, Alias.name.label("alias_name"), Aliasable.aliasable_subtype)
            .where(Alias.user_id == user_id)
            .join(Aliasable, Alias.aliasable_id == Aliasable.aliasable_id)
            .subquery()
        )

        category_user = select(Category.aliasable_id, Category.name.label("name")).where(Category.user_id == user_id)
        storage_user = select(Storage.aliasable_id, Storage.name.label("name")).where(Storage.user_id == user_id)
        currency = select(Currency.aliasable_id, Currency.name.label("name"))

        u = union(category_user, storage_user, currency).subquery()

        r = await self.session.execute(
            select(alias_user.c.alias_number, alias_user.c.alias_name, alias_user.c.aliasable_subtype, u.c.name)
            .join(u, alias_user.c.aliasable_id == u.c.aliasable_id)
            .order_by(alias_user.c.alias_number)
        )

        return [row._asdict() for row in r.all()]

    async def get_max_alias_number_for_user(self, user_id: int) -> int:
        return await self._get_max_model_number_for_user(user_id, model=Alias)

    async def refresh_alias_numbers_for_user(self, user_id: int) -> None:
        await self._refresh_model_numbers_for_user(user_id, model=Alias)

    async def delete_alias(self, user_id: int, number: int) -> None:
        alias = self.get_alias_by_number_for_user(user_id, number)
        await self.session.delete(alias)
        await self.session.flush()
        await self.refresh_alias_numbers_for_user(user_id)

    async def get_user_default(self, user_id: int) -> Optional[UserDefault]:
        r = await self.session.execute(
            select(UserDefault)
            .where(UserDefault.user_id == user_id)
        )
        user_default = r.scalar()
        return user_default

    async def get_currencies(self) -> Sequence[Currency]:
        r = await self.session.execute(
            select(Currency)
            .order_by(Currency.currency_id)
        )
        currencies = r.scalars().all()
        return currencies

    async def get_currency_by_alpha_code(self, alpha_code: str) -> Optional[Currency]:
        r = await self.session.execute(
            select(Currency)
            .where(Currency.alpha_code == alpha_code)
        )
        currency = r.scalar()
        return currency

    async def set_default_currency(self, user_id: int, alpha_code: str) -> Currency:
        currency = await self.get_currency_by_alpha_code(alpha_code)
        await self._upsert_user_default(user_id, currency_id=currency.currency_id)
        return currency

    async def add_transaction(
            self,
            user_id: int,
            storage_id: int,
            category_id: int,
            currency_id: int,
            amount: float,
            months: int
    ) -> Transaction:
        pass
