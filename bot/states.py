from aiogram.fsm.state import StatesGroup, State


class StorageStates(StatesGroup):
    # add
    waiting_for_new_storage_name = State()
    waiting_for_new_storage_is_credit_flag = State()
    waiting_for_new_storage_billing_day = State()
    waiting_for_new_storage_multicurrency_flag = State()
    waiting_for_new_storage_currency_alphacode = State()
    # edit
    waiting_for_storage_number_to_edit = State()
    waiting_for_edited_storage_name = State()
    # delete
    waiting_for_storage_number_to_delete = State()
    # set default
    waiting_for_storage_number_to_set_default = State()


class CategoryStates(StatesGroup):
    # add
    waiting_for_new_category_name = State()
    waiting_for_new_category_factor_in = State()
    # edit
    waiting_for_category_number_to_edit = State()
    waiting_for_edited_category_name = State()
    waiting_for_edited_category_factor_in = State()
    # delete
    waiting_for_category_number_to_delete = State()
    # set default
    waiting_for_category_number_to_set_default = State()


class AliasStates(StatesGroup):
    # add
    waiting_for_aliasable_subtype = State()
    waiting_for_aliasable_number = State()
    waiting_for_currency_alphacode = State()
    waiting_for_alias_name = State()
    # delete
    waiting_for_alias_number_to_delete = State()


class CurrencyStates(StatesGroup):
    waiting_for_currency_alphacode = State()


class TransactionStates(StatesGroup):
    # add
    waiting_for_new_transaction = State()  # main state
    # todo: edit & delete
