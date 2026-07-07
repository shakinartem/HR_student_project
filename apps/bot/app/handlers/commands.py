from __future__ import annotations

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app.keyboards.main_menu import build_main_menu, build_webapp_shortcut
from app.models import AppRole
from app.services.backend import BotBackendClient
from app.texts import DEFAULT_ROLE_NOTE, TODO_SUPPORT_TEXT, WELCOME_TEXT


def _coerce_role(role_value: str | None) -> AppRole:
    if role_value == AppRole.HR.value:
        return AppRole.HR
    if role_value == AppRole.ADMIN.value:
        return AppRole.ADMIN
    if role_value == AppRole.STUDENT.value:
        return AppRole.STUDENT
    return AppRole.GUEST


async def resolve_role(backend_client: BotBackendClient, telegram_id: int | None) -> AppRole:
    if telegram_id is None:
        return AppRole.GUEST

    backend_user = await backend_client.get_me_by_telegram_id(telegram_id)
    if backend_user is None:
        return AppRole.GUEST

    return _coerce_role(backend_user.role)


def create_command_router(backend_client: BotBackendClient, webapp_url: str) -> Router:
    router = Router(name="commands")

    async def send_menu(message: Message, role: AppRole) -> None:
        lines = [WELCOME_TEXT]
        if role == AppRole.GUEST:
            lines.append(DEFAULT_ROLE_NOTE)
        await message.answer("\n\n".join(lines), reply_markup=build_main_menu(role=role, webapp_url=webapp_url))

    @router.message(Command("start"))
    async def start_command(message: Message) -> None:
        telegram_id = message.from_user.id if message.from_user else None
        role = await resolve_role(backend_client, telegram_id)
        await send_menu(message, role)

    @router.message(Command("help"))
    async def help_command(message: Message) -> None:
        await message.answer(
            "/start - show main menu\n"
            "/help - show commands\n"
            "/profile - open profile area\n"
            "/balance - open balance area\n"
            "/support - contact support placeholder"
        )

    @router.message(Command("profile"))
    async def profile_command(message: Message) -> None:
        telegram_id = message.from_user.id if message.from_user else None
        role = await resolve_role(backend_client, telegram_id)
        if role == AppRole.GUEST:
            await message.answer(
                "Registration and access activation continue in the Mini App.",
                reply_markup=build_main_menu(role=role, webapp_url=webapp_url),
            )
            return

        route = "/profile" if role == AppRole.STUDENT else "/hr"
        label = "Open profile" if role == AppRole.STUDENT else "Open HR dashboard"
        await message.answer("Open the relevant Mini App area below.", reply_markup=build_webapp_shortcut(label, webapp_url, route))

    @router.message(Command("balance"))
    async def balance_command(message: Message) -> None:
        telegram_id = message.from_user.id if message.from_user else None
        role = await resolve_role(backend_client, telegram_id)
        if role == AppRole.ADMIN:
            await message.answer(
                "Admin payments and stats live in the Mini App.",
                reply_markup=build_webapp_shortcut("Open payments", webapp_url, "/admin/payments"),
            )
            return

        if role == AppRole.HR:
            await message.answer(
                "Open the HR dashboard to continue with vacancy payment and application handling.",
                reply_markup=build_webapp_shortcut("Open HR dashboard", webapp_url, "/hr"),
            )
            return

        await message.answer(
            "Open balance and access controls in the Mini App.",
            reply_markup=build_webapp_shortcut("Open balance", webapp_url, "/balance"),
        )

    @router.message(Command("support"))
    async def support_command(message: Message) -> None:
        await message.answer(TODO_SUPPORT_TEXT)

    return router
