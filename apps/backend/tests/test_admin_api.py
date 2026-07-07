from __future__ import annotations

from datetime import UTC, datetime, timedelta
from uuid import UUID

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.enums import ApplicationStatus, ComplaintStatus, HRStatus, PaymentStatus, UserRole, VacancyStatus
from app.models import Complaint, HRProfile, Payment, User, Vacancy

from .test_applications_api import (
    authenticate_user,
    create_application,
    create_hr_fixture,
    create_vacancy,
    ensure_student_user,
    setup_student_ready_for_application,
)
from .test_hr_vacancies_api import ensure_vacancy_publication_tariff


def test_non_admin_gets_403_for_admin_routes(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    response = client.get("/api/admin/users", headers=auth_headers)

    assert response.status_code == 403
    assert response.json()["detail"] == "Admin role required"


def test_admin_can_list_users(
    client: TestClient,
    admin_headers: dict[str, str],
    db_session: Session,
) -> None:
    ensure_student_user(db_session, telegram_id=777123, username="user_list")

    response = client.get("/api/admin/users", headers=admin_headers)

    assert response.status_code == 200
    items = response.json()["items"]
    assert any(item["telegram_id"] == 777123 for item in items)


def test_admin_can_get_user_detail(
    client: TestClient,
    admin_headers: dict[str, str],
    db_session: Session,
) -> None:
    user = ensure_student_user(db_session, telegram_id=777124, username="detail_user")

    response = client.get(f"/api/admin/users/{user.id}", headers=admin_headers)

    assert response.status_code == 200
    payload = response.json()
    assert payload["id"] == str(user.id)
    assert payload["telegram_id"] == 777124


def test_admin_can_block_and_unblock_user(
    client: TestClient,
    admin_headers: dict[str, str],
    db_session: Session,
) -> None:
    user = ensure_student_user(db_session, telegram_id=777125, username="block_user")

    blocked = client.patch(
        f"/api/admin/users/{user.id}",
        headers=admin_headers,
        json={"is_blocked": True},
    )
    unblocked = client.patch(
        f"/api/admin/users/{user.id}",
        headers=admin_headers,
        json={"is_blocked": False},
    )

    assert blocked.status_code == 200
    assert blocked.json()["is_blocked"] is True
    assert unblocked.status_code == 200
    assert unblocked.json()["is_blocked"] is False


def test_admin_can_mute_and_unmute_user(
    client: TestClient,
    admin_headers: dict[str, str],
    db_session: Session,
) -> None:
    user = ensure_student_user(db_session, telegram_id=777126, username="mute_user")
    mute_until = (datetime.now(UTC) + timedelta(hours=24)).isoformat()

    muted = client.patch(
        f"/api/admin/users/{user.id}",
        headers=admin_headers,
        json={"mute_until": mute_until},
    )
    unmuted = client.patch(
        f"/api/admin/users/{user.id}",
        headers=admin_headers,
        json={"mute_until": None},
    )

    assert muted.status_code == 200
    assert muted.json()["mute_until"] is not None
    assert unmuted.status_code == 200
    assert unmuted.json()["mute_until"] is None


def test_admin_can_list_hr_profiles(
    client: TestClient,
    admin_headers: dict[str, str],
    db_session: Session,
) -> None:
    hr_user, _company = create_hr_fixture(db_session, telegram_id=890111, suffix="adminhr")

    response = client.get("/api/admin/hr-profiles", headers=admin_headers)

    assert response.status_code == 200
    items = response.json()["items"]
    assert any(item["user"]["id"] == str(hr_user.id) for item in items)


def test_admin_can_approve_and_block_hr_profile(
    client: TestClient,
    admin_headers: dict[str, str],
    db_session: Session,
) -> None:
    hr_user, company = create_hr_fixture(db_session, telegram_id=890112, suffix="approvehr")
    hr_profile = db_session.scalar(select(HRProfile).where(HRProfile.user_id == hr_user.id))
    assert hr_profile is not None
    hr_profile.verified_status = HRStatus.PENDING
    db_session.commit()

    approved = client.patch(
        f"/api/admin/hr-profiles/{hr_profile.id}/status",
        headers=admin_headers,
        json={"verified_status": "active"},
    )
    blocked = client.patch(
        f"/api/admin/hr-profiles/{hr_profile.id}/status",
        headers=admin_headers,
        json={"verified_status": "blocked"},
    )

    assert company.name
    assert approved.status_code == 200
    assert approved.json()["verified_status"] == "active"
    assert blocked.status_code == 200
    assert blocked.json()["verified_status"] == "blocked"


def test_admin_can_list_moderation_queue(
    client: TestClient,
    admin_headers: dict[str, str],
    db_session: Session,
) -> None:
    hr_user, company = create_hr_fixture(db_session, telegram_id=890113, suffix="modqueue")
    create_vacancy(
        db_session,
        hr_user=hr_user,
        company=company,
        title="Needs moderation",
        status=VacancyStatus.MANUAL_REVIEW,
    )

    response = client.get("/api/admin/moderation/vacancies", headers=admin_headers)

    assert response.status_code == 200
    assert any(item["title"] == "Needs moderation" for item in response.json()["items"])


def test_admin_can_approve_vacancy_from_manual_review_to_active(
    client: TestClient,
    admin_headers: dict[str, str],
    db_session: Session,
) -> None:
    hr_user, company = create_hr_fixture(db_session, telegram_id=890114, suffix="approvevac")
    vacancy = create_vacancy(
        db_session,
        hr_user=hr_user,
        company=company,
        title="Approve me",
        status=VacancyStatus.MANUAL_REVIEW,
    )

    response = client.post(f"/api/admin/moderation/vacancies/{vacancy.id}/approve", headers=admin_headers)

    assert response.status_code == 200
    assert response.json()["status"] == "active"
    assert response.json()["moderation_status"] == "approved"


def test_admin_can_reject_vacancy(
    client: TestClient,
    admin_headers: dict[str, str],
    db_session: Session,
) -> None:
    hr_user, company = create_hr_fixture(db_session, telegram_id=890115, suffix="rejectvac")
    vacancy = create_vacancy(
        db_session,
        hr_user=hr_user,
        company=company,
        title="Reject me",
        status=VacancyStatus.MODERATION,
    )

    response = client.post(
        f"/api/admin/moderation/vacancies/{vacancy.id}/reject",
        headers=admin_headers,
        json={"reason": "Unsafe wording"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "rejected"
    assert response.json()["moderation_status"] == "rejected"


def test_admin_can_list_complaints(
    client: TestClient,
    admin_headers: dict[str, str],
    db_session: Session,
    settings,
) -> None:
    student_user = setup_student_ready_for_application(db_session)
    hr_user, company = create_hr_fixture(db_session, telegram_id=890116, suffix="complaints")
    vacancy = create_vacancy(db_session, hr_user=hr_user, company=company, title="Complaint vacancy")
    application = create_application(db_session, vacancy=vacancy, student_user=student_user)
    hr_headers = authenticate_user(client, settings, telegram_id=890116, username="hr_complaints")
    client.post(
        f"/api/hr/applications/{application.id}/complain",
        headers=hr_headers,
        json={"reason": "No-show"},
    )

    response = client.get("/api/admin/complaints", headers=admin_headers)

    assert response.status_code == 200
    assert any(item["application_id"] == str(application.id) for item in response.json()["items"])


def test_admin_can_update_complaint_status(
    client: TestClient,
    admin_headers: dict[str, str],
    db_session: Session,
) -> None:
    reporter = ensure_student_user(db_session, telegram_id=777127, username="complaint_reporter")
    target = ensure_student_user(db_session, telegram_id=777128, username="complaint_target")
    complaint = Complaint(
        reporter_user_id=reporter.id,
        target_user_id=target.id,
        reason="Spam",
        status=ComplaintStatus.OPEN,
    )
    db_session.add(complaint)
    db_session.commit()
    db_session.refresh(complaint)

    response = client.patch(
        f"/api/admin/complaints/{complaint.id}/status",
        headers=admin_headers,
        json={"status": "resolved", "admin_comment": "Handled"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "resolved"
    assert response.json()["admin_comment"] == "Handled"


def test_admin_can_list_payments_read_only(
    client: TestClient,
    admin_headers: dict[str, str],
    db_session: Session,
    settings,
) -> None:
    ensure_vacancy_publication_tariff(db_session)
    hr_user, company = create_hr_fixture(db_session, telegram_id=890117, suffix="payments")
    vacancy = create_vacancy(db_session, hr_user=hr_user, company=company, title="Paid vacancy", status=VacancyStatus.DRAFT)
    hr_headers = authenticate_user(client, settings, telegram_id=890117, username="hr_payments")
    payment_id = client.post(f"/api/hr/vacancies/{vacancy.id}/publish-payment", headers=hr_headers).json()["payment_id"]
    client.post("/api/payments/mock-confirm", headers=hr_headers, json={"payment_id": payment_id})

    response = client.get("/api/admin/payments", headers=admin_headers)

    assert response.status_code == 200
    assert any(item["id"] == payment_id for item in response.json()["items"])
    assert all("provider_payment_id" in item for item in response.json()["items"])


def test_admin_stats_returns_expected_counters(
    client: TestClient,
    admin_headers: dict[str, str],
    db_session: Session,
    settings,
) -> None:
    student_user = setup_student_ready_for_application(db_session)
    hr_user, company = create_hr_fixture(db_session, telegram_id=890118, suffix="stats")
    manual_review_vacancy = create_vacancy(
        db_session,
        hr_user=hr_user,
        company=company,
        title="Review vacancy",
        status=VacancyStatus.MANUAL_REVIEW,
    )
    active_vacancy = create_vacancy(
        db_session,
        hr_user=hr_user,
        company=company,
        title="Active vacancy",
        status=VacancyStatus.ACTIVE,
    )
    create_application(db_session, vacancy=active_vacancy, student_user=student_user, status=ApplicationStatus.SENT)
    complaint = Complaint(
        reporter_user_id=student_user.id,
        target_user_id=hr_user.id,
        vacancy_id=manual_review_vacancy.id,
        reason="Unsafe",
        status=ComplaintStatus.OPEN,
    )
    db_session.add(complaint)
    db_session.commit()

    payment = Payment(
        user_id=hr_user.id,
        amount=149,
        currency="RUB",
        provider="mock",
        provider_payment_id="manual-admin-stats",
        status=PaymentStatus.SUCCEEDED,
        purpose="hr_vacancy_publication",
        entity_type="vacancy",
        entity_id=str(active_vacancy.id),
    )
    db_session.add(payment)
    db_session.commit()

    response = client.get("/api/admin/stats", headers=admin_headers)

    assert response.status_code == 200
    payload = response.json()
    assert payload["total_users"] >= 3
    assert payload["students"] >= 1
    assert payload["hr_users"] >= 1
    assert payload["active_vacancies"] >= 1
    assert payload["applications"] >= 1
    assert payload["succeeded_payments"] >= 1
    assert payload["open_complaints"] >= 1
    assert payload["manual_review_vacancies"] >= 1
