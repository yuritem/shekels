from aiogram.types import BotCommand
from aiogram import Bot


# todo: move somewhere. i18n? configs?
COMMANDS = {
    "start": "Start the bot",
    "help": "Get an overview of all commands",
    "balance": "Get current balance across all storages",
    "cancel": "Cancel current command",
    "add_category": "Add new transaction category",
    "edit_category": "Edit existing category",
    "delete_category": "Delete existing category",
    "add_storage": "Add new storage",
    "edit_storage": "Edit existing storage",
    "delete_storage": "Delete existing storage",
    "add_alias": "Add new alias",
    "delete_alias": "Delete existing alias",
    "add_recurrent": "Add new recurrent transaction",
    "set_default_category": "Set default category",
    "set_default_storage": "Set default storage",
    "set_default_currency": "Set default currency",
    "list_categories": "List my categories",
    "list_storages": "List my categories",
    "list_aliases": "List my aliases",
    "list_transactions": "List my transactions"
    # "list_recurrent_transactions": "List my recurrent transactions"
}


async def set_commands(bot: Bot):
    commands = [
        BotCommand(command=command_name, description=command_description)
        for command_name, command_description in COMMANDS.items()
    ]
    await bot.set_my_commands(commands)
