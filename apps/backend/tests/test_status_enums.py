from app.core.enums import (
    ApplicationStatus,
    HRStatus,
    ModerationResult,
    PaymentStatus,
    SubscriptionStatus,
    SupportTicketStatus,
    UserRole,
    VacancyStatus,
)


def test_user_roles_match_documented_values() -> None:
    assert {role.value for role in UserRole} == {
        "student",
        "hr",
        "admin",
        "moderator",
        "support",
    }


def test_vacancy_statuses_match_documented_values() -> None:
    assert {status.value for status in VacancyStatus} == {
        "draft",
        "awaiting_payment",
        "moderation",
        "manual_review",
        "active",
        "rejected",
        "archived",
        "expired",
    }


def test_application_statuses_match_contact_visibility_rules() -> None:
    assert {status.value for status in ApplicationStatus} == {
        "sent",
        "viewed",
        "accepted",
        "rejected",
        "complaint",
        "closed",
    }


def test_hr_and_subscription_statuses_match_documented_values() -> None:
    assert {status.value for status in HRStatus} == {"pending", "active", "blocked"}
    assert {status.value for status in SubscriptionStatus} == {
        "active",
        "expired",
        "canceled",
    }


def test_payment_support_and_moderation_statuses_match_documented_values() -> None:
    assert {status.value for status in PaymentStatus} == {
        "pending",
        "succeeded",
        "canceled",
        "failed",
        "refunded",
    }
    assert {status.value for status in SupportTicketStatus} == {
        "open",
        "in_progress",
        "resolved",
        "closed",
    }
    assert {result.value for result in ModerationResult} == {
        "approved",
        "manual_review",
        "rejected",
    }
