from __future__ import annotations

from aiogram import F, Router
from aiogram.types import CallbackQuery

from app.texts import TODO_ACTION_TEXT, TODO_SUPPORT_TEXT


def create_callback_router() -> Router:
    router = Router(name="callbacks")

    @router.callback_query(F.data == "menu:common:support")
    async def support_placeholder(callback: CallbackQuery) -> None:
        await callback.answer()
        if callback.message is not None:
            await callback.message.answer(TODO_SUPPORT_TEXT)

    @router.callback_query(F.data.startswith("menu:"))
    async def generic_menu_placeholder(callback: CallbackQuery) -> None:
        await callback.answer()
        if callback.message is not None:
            await callback.message.answer(TODO_ACTION_TEXT)

    return router
