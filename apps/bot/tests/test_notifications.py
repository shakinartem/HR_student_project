from app.services.notifications import (
    format_admin_manual_moderation_required,
    format_hr_new_application,
    format_hr_vacancy_approved,
    format_hr_vacancy_rejected,
    format_student_access_activated,
    format_student_application_sent,
    format_student_hr_accepted_application,
)


def test_student_access_activated_message_is_safe() -> None:
    message = format_student_access_activated(expires_at_text="2026-08-05")

    assert "Access activated" in message
    assert "@" not in message
    assert "+7" not in message


def test_student_application_sent_message_does_not_include_hr_contacts() -> None:
    message = format_student_application_sent(vacancy_title="Barista")

    assert "Barista" in message
    assert "phone" not in message.lower()
    assert "telegram" not in message.lower()


def test_student_hr_accepted_message_does_not_expose_hr_contacts() -> None:
    message = format_student_hr_accepted_application(vacancy_title="Waiter")

    assert "Waiter" in message
    assert "@" not in message
    assert "+7" not in message


def test_hr_new_application_message_hides_student_contacts_by_default() -> None:
    message = format_hr_new_application(
        vacancy_title="Waiter",
        student_name="Ivan",
        include_contacts=False,
    )

    assert "Ivan" in message
    assert "Contacts:" not in message


def test_hr_new_application_message_can_include_backend_safe_contacts() -> None:
    message = format_hr_new_application(
        vacancy_title="Waiter",
        student_name="Ivan",
        include_contacts=True,
        contacts={"phone": "+79990000000", "telegram_username": "ivan_student"},
    )

    assert "Contacts:" in message
    assert "+79990000000" in message
    assert "@ivan_student" in message


def test_hr_vacancy_status_notifications_are_clear() -> None:
    approved = format_hr_vacancy_approved(vacancy_title="Cashier")
    rejected = format_hr_vacancy_rejected(vacancy_title="Cashier", reason="Needs moderation fixes")

    assert "Cashier" in approved
    assert "approved" in approved.lower()
    assert "Needs moderation fixes" in rejected


def test_admin_manual_moderation_notification_is_summary_only() -> None:
    message = format_admin_manual_moderation_required(vacancy_title="Courier", company_name="Fast Co")

    assert "Courier" in message
    assert "Fast Co" in message
    assert "contact" not in message.lower()
