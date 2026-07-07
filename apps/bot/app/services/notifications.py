from __future__ import annotations

from collections.abc import Mapping

from aiogram import Bot


def format_student_access_activated(expires_at_text: str) -> str:
    return f"Access activated.\n\nYour student access is active until {expires_at_text}."


def format_student_application_sent(vacancy_title: str) -> str:
    return (
        f"Application sent for: {vacancy_title}.\n\n"
        "If the employer is interested, you will get a status update here."
    )


def format_student_hr_accepted_application(vacancy_title: str) -> str:
    return (
        f"An HR team accepted your application for: {vacancy_title}.\n\n"
        "Please make sure your profile contact details are up to date."
    )


def format_hr_new_application(
    vacancy_title: str,
    student_name: str,
    include_contacts: bool = False,
    contacts: Mapping[str, str | None] | None = None,
) -> str:
    message = f"New application for: {vacancy_title}.\nStudent: {student_name}."
    if not include_contacts or not contacts:
        return message

    contact_lines = []
    if contacts.get("phone"):
        contact_lines.append(f"Phone: {contacts['phone']}")
    if contacts.get("email"):
        contact_lines.append(f"Email: {contacts['email']}")
    if contacts.get("telegram_username"):
        contact_lines.append(f"Telegram: @{contacts['telegram_username']}")

    if not contact_lines:
        return message

    return f"{message}\n\nContacts:\n" + "\n".join(contact_lines)


def format_hr_vacancy_approved(vacancy_title: str) -> str:
    return f"Your vacancy was approved: {vacancy_title}."


def format_hr_vacancy_rejected(vacancy_title: str, reason: str | None = None) -> str:
    suffix = f"\nReason: {reason}" if reason else ""
    return f"Your vacancy was rejected: {vacancy_title}.{suffix}"


def format_admin_new_complaint(subject: str) -> str:
    return f"New complaint requires review: {subject}."


def format_admin_manual_moderation_required(vacancy_title: str, company_name: str) -> str:
    return f"Manual moderation required for vacancy '{vacancy_title}' from {company_name}."


class NotificationService:
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    async def notify_student_access_activated(self, chat_id: int, expires_at_text: str) -> None:
        await self.bot.send_message(chat_id, format_student_access_activated(expires_at_text))

    async def notify_student_application_sent(self, chat_id: int, vacancy_title: str) -> None:
        await self.bot.send_message(chat_id, format_student_application_sent(vacancy_title))

    async def notify_student_hr_accepted_application(self, chat_id: int, vacancy_title: str) -> None:
        await self.bot.send_message(chat_id, format_student_hr_accepted_application(vacancy_title))

    async def notify_hr_new_application(
        self,
        chat_id: int,
        vacancy_title: str,
        student_name: str,
        include_contacts: bool = False,
        contacts: Mapping[str, str | None] | None = None,
    ) -> None:
        await self.bot.send_message(
            chat_id,
            format_hr_new_application(
                vacancy_title=vacancy_title,
                student_name=student_name,
                include_contacts=include_contacts,
                contacts=contacts,
            ),
        )

    async def notify_hr_vacancy_approved(self, chat_id: int, vacancy_title: str) -> None:
        await self.bot.send_message(chat_id, format_hr_vacancy_approved(vacancy_title))

    async def notify_hr_vacancy_rejected(self, chat_id: int, vacancy_title: str, reason: str | None = None) -> None:
        await self.bot.send_message(chat_id, format_hr_vacancy_rejected(vacancy_title, reason))

    async def notify_admin_new_complaint(self, chat_id: int, subject: str) -> None:
        await self.bot.send_message(chat_id, format_admin_new_complaint(subject))

    async def notify_admin_manual_moderation_required(
        self,
        chat_id: int,
        vacancy_title: str,
        company_name: str,
    ) -> None:
        await self.bot.send_message(chat_id, format_admin_manual_moderation_required(vacancy_title, company_name))
