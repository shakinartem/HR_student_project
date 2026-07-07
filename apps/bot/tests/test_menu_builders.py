from aiogram.types import InlineKeyboardMarkup

from app.keyboards.main_menu import build_main_menu, build_webapp_url
from app.models import AppRole


def flatten_texts(markup: InlineKeyboardMarkup) -> list[str]:
    return [button.text for row in markup.inline_keyboard for button in row]


def find_button(markup: InlineKeyboardMarkup, text: str):
    for row in markup.inline_keyboard:
        for button in row:
            if button.text == text:
                return button
    return None


def test_default_menu_contains_open_vacancies_and_register_action() -> None:
    markup = build_main_menu(role=AppRole.GUEST, webapp_url="https://mini.app")

    texts = flatten_texts(markup)

    assert "Open vacancies" in texts
    assert "Register / activate access" in texts


def test_student_menu_includes_open_vacancies() -> None:
    markup = build_main_menu(role=AppRole.STUDENT, webapp_url="https://mini.app")

    assert "Open vacancies" in flatten_texts(markup)


def test_hr_menu_includes_create_vacancy() -> None:
    markup = build_main_menu(role=AppRole.HR, webapp_url="https://mini.app")

    assert "Create vacancy" in flatten_texts(markup)


def test_admin_menu_includes_moderation_queue() -> None:
    markup = build_main_menu(role=AppRole.ADMIN, webapp_url="https://mini.app")

    assert "Moderation queue" in flatten_texts(markup)


def test_open_vacancies_button_uses_telegram_webapp_url() -> None:
    markup = build_main_menu(role=AppRole.STUDENT, webapp_url="https://mini.app/base")

    button = find_button(markup, "Open vacancies")

    assert button is not None
    assert button.web_app is not None
    assert button.web_app.url == "https://mini.app/base?route=%2Ffeed"


def test_build_webapp_url_preserves_existing_query_params() -> None:
    url = build_webapp_url("https://mini.app/base?theme=telegram", "/hr/vacancies/new")

    assert url == "https://mini.app/base?theme=telegram&route=%2Fhr%2Fvacancies%2Fnew"
