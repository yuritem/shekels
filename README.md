# ₪ Shekels

[Shekels](https://t.me/ilshekelbot) is a fully asynchronous telegram bot for personal finance built with the [aiogram](https://github.com/aiogram/aiogram) framework.  
Shekels is designed to be easy and fast to use out of the box &mdash; but even more so once you configure it.

⚠️ The project is currently under development. Bot is down.

## Features

- Send your transactions in plain text
- Add custom categories and money storages
- Set up aliases for caterogies, storages, and currencies to speed things up
- Set up default categories and storages for even more speed
- View current balance, stats, and clean monthly reports
- Exclude categories from balance calculations
- 150+ currencies avaliable


## Overview

TBS.

<!--
### Storages

### Categories

### Aliases
-->

## Technologies
<!--
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Postgres](https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white)
![Poetry](https://img.shields.io/badge/Poetry-%233B82F6.svg?style=for-the-badge&logo=poetry&logoColor=0B3D8D)
![Asyncio](https://img.shields.io/badge/asyncio-%2300BAFF.svg?&style=for-the-badge&logo=python&logoColor=white)
-->

- [Aiogram 3.x](https://github.com/aiogram/aiogram) &mdash; telegram bot interface;
- [PostgreSQL](https://www.postgresql.org/) &mdash; RDBMS;
- [Sqlalchemy 2.x](https://www.sqlalchemy.org/) &mdash; async ORM for Postgres;
- [Pydantic 2.x](https://github.com/pydantic/pydantic) &mdash; data validation via models;
- [Poetry](https://python-poetry.org/) &mdash; dependency management;
- [Redis](https://redis.io/) &mdash; persistent storage for temporary data.

## Data model

![Shekels database model](media/shekels_db_model.svg "Shekels database model")

(made with [dbdiagram.io](https://dbdiagram.io/))

## Usage

- Get a bot token from [BotFather](https://t.me/botfather)
- Create an `.env` file in the project root with bot token and other variables specified in `bot.config.Settings`
- Install `poetry` and run `poetry install` command in project root
- Activate the virtual environment with `poetry shell`
- Run `bot/main.py` with `python3 -m bot.main` from the project root
