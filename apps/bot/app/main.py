from __future__ import annotations

import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from app.config import get_settings
from app.handlers import create_callback_router, create_command_router
from app.services import BotBackendClient


def create_dispatcher() -> Dispatcher:
    settings = get_settings()
    backend_client = BotBackendClient(
        base_url=settings.backend_base_url,
        timeout_seconds=settings.backend_timeout_seconds,
    )

    dispatcher = Dispatcher()
    dispatcher.include_router(create_command_router(backend_client, settings.telegram_webapp_url))
    dispatcher.include_router(create_callback_router())
    return dispatcher


async def run_polling() -> None:
    settings = get_settings()
    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dispatcher = create_dispatcher()
    await dispatcher.start_polling(bot)


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    asyncio.run(run_polling())


if __name__ == "__main__":
    main()
