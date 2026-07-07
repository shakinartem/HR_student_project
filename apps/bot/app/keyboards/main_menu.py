from __future__ import annotations

from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from aiogram.types import InlineKeyboardMarkup, WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.models import AppRole


def build_webapp_url(base_url: str, route: str) -> str:
    parts = urlsplit(base_url)
    query = dict(parse_qsl(parts.query, keep_blank_values=True))
    query["route"] = route
    return urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(query), parts.fragment))


def build_main_menu(role: AppRole, webapp_url: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    if role == AppRole.GUEST:
        builder.button(text="Open vacancies", web_app=WebAppInfo(url=build_webapp_url(webapp_url, "/feed")))
        builder.button(text="Register / activate access", callback_data="menu:guest:activate")
        builder.button(text="Support", callback_data="menu:common:support")
        builder.adjust(1)
        return builder.as_markup()

    if role == AppRole.STUDENT:
        builder.button(text="Open vacancies", web_app=WebAppInfo(url=build_webapp_url(webapp_url, "/feed")))
        builder.button(text="My profile", web_app=WebAppInfo(url=build_webapp_url(webapp_url, "/profile")))
        builder.button(text="My balance", web_app=WebAppInfo(url=build_webapp_url(webapp_url, "/balance")))
        builder.button(
            text="My applications",
            web_app=WebAppInfo(url=build_webapp_url(webapp_url, "/applications")),
        )
        builder.button(text="Top up balance", callback_data="menu:student:topup")
        builder.button(text="Support", callback_data="menu:common:support")
        builder.adjust(1, 2, 2, 1)
        return builder.as_markup()

    if role == AppRole.HR:
        builder.button(
            text="Create vacancy",
            web_app=WebAppInfo(url=build_webapp_url(webapp_url, "/hr/vacancies/new")),
        )
        builder.button(
            text="My vacancies",
            web_app=WebAppInfo(url=build_webapp_url(webapp_url, "/hr")),
        )
        builder.button(
            text="Applications",
            web_app=WebAppInfo(url=build_webapp_url(webapp_url, "/hr")),
        )
        builder.button(text="Support", callback_data="menu:common:support")
        builder.adjust(1)
        return builder.as_markup()

    builder.button(text="Users", web_app=WebAppInfo(url=build_webapp_url(webapp_url, "/admin/users")))
    builder.button(text="HR access", web_app=WebAppInfo(url=build_webapp_url(webapp_url, "/admin/hr-access")))
    builder.button(
        text="Moderation queue",
        web_app=WebAppInfo(url=build_webapp_url(webapp_url, "/admin/moderation")),
    )
    builder.button(text="Complaints", web_app=WebAppInfo(url=build_webapp_url(webapp_url, "/admin/complaints")))
    builder.button(text="Payments", web_app=WebAppInfo(url=build_webapp_url(webapp_url, "/admin/payments")))
    builder.button(text="Stats", web_app=WebAppInfo(url=build_webapp_url(webapp_url, "/admin/stats")))
    builder.adjust(1)
    return builder.as_markup()


def build_webapp_shortcut(text: str, webapp_url: str, route: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=text, web_app=WebAppInfo(url=build_webapp_url(webapp_url, route)))
    return builder.as_markup()
