from aiogram.types import BotCommand
from aiogram import Bot


# todo: move somewhere. i18n? configs?
COMMANDS = {
    "start": "Start the bot",
    "help": "Overview of all commands",
    "balance": "Current balance across all storages",
    "report": "Get a report for a given period",
    "cancel": "Cancel current command",
    "add_category": "Add new transaction category",
    "add_storage": "Add new storage",
    "add_alias": "Add new alias",
    "add_recurrent": "Add new recurrent transaction",
    "edit_category": "Edit existing category",
    "edit_storage": "Edit existing storage",
    "edit_recurrent": "Edit existing recurrent transaction",
    "delete_category": "Delete existing category",
    "delete_storage": "Delete existing storage",
    "delete_alias": "Delete existing alias",
    "delete_recurrent": "Delete existing recurrent transaction",
    "set_default_category": "Set default category",
    "set_default_storage": "Set default storage",
    "set_default_currency": "Set default currency",
    "list_categories": "List my categories",
    "list_storages": "List my categories",
    "list_aliases": "List my aliases",
    "list_transactions": "List my transactions",
    "list_recurrent": "List my recurrent transactions"
}


async def set_commands(bot: Bot):
    commands = [
        BotCommand(command=command_name, description=command_description)
        for command_name, command_description in COMMANDS.items()
    ]
    await bot.set_my_commands(commands)
