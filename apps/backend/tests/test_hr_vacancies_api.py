from __future__ import annotations

from uuid import UUID

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.enums import HRStatus, PaymentStatus, UserRole, VacancyStatus
from app.models import Event, Payment, Tariff, User, Vacancy

from .test_applications_api import authenticate_user, create_hr_fixture, create_vacancy


def ensure_vacancy_publication_tariff(db_session: Session, amount: int = 149) -> Tariff:
    tariff = db_session.scalar(select(Tariff).where(Tariff.code == "vacancy_basic_30d"))
    if tariff is None:
        tariff = Tariff(
            code="vacancy_basic_30d",
            title="Vacancy Basic 30 Days",
            amount=amount,
            duration_days=30,
            is_active=True,
        )
        db_session.add(tariff)
        db_session.commit()
        db_session.refresh(tariff)
    return tariff


def build_vacancy_payload(
    *,
    title: str = "Evening Waiter",
    description: str = "Safe student-friendly evening shift.",
    requirements: str = "Polite communication.",
    conditions: str = "Flexible shifts and meals.",
) -> dict:
    return {
        "title": title,
        "category": "restaurant",
        "job_type": "shift",
        "schedule": "evening",
        "salary_text": "2500 RUB/shift",
        "salary_min": 2500,
        "salary_max": 3000,
        "district": "center",
        "address": "Lenina 1",
        "format": "offline",
        "description": description,
        "responsibilities": "Serve guests and keep tables tidy.",
        "requirements": requirements,
        "conditions": conditions,
        "experience_required": False,
        "photo_url": None,
    }


def test_non_hr_cannot_create_vacancy(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    response = client.post("/api/hr/vacancies", headers=auth_headers, json=build_vacancy_payload())

    assert response.status_code == 403
    assert response.json()["detail"] == "HR role required"


def test_blocked_hr_cannot_create_vacancy(
    client: TestClient,
    db_session: Session,
    settings,
) -> None:
    hr_headers = authenticate_user(client, settings, telegram_id=890001, username="blocked_hr")
    hr_user = db_session.scalar(select(User).where(User.telegram_id == 890001))
    hr_user.role = UserRole.HR
    db_session.flush()
    company_user, company = create_hr_fixture(db_session, telegram_id=890002, suffix="blockedhelper")
    db_session.delete(company_user.hr_profile)
    db_session.delete(company)
    db_session.flush()
    db_session.commit()
    hr_user.is_blocked = True
    db_session.commit()

    response = client.post("/api/hr/vacancies", headers=hr_headers, json=build_vacancy_payload())

    assert response.status_code == 403
    assert response.json()["detail"] == "User is blocked"


def test_hr_can_create_own_vacancy(
    client: TestClient,
    db_session: Session,
    settings,
) -> None:
    hr_user, _company = create_hr_fixture(db_session, telegram_id=890003, suffix="create")
    hr_headers = authenticate_user(client, settings, telegram_id=890003, username="hr_create")

    response = client.post("/api/hr/vacancies", headers=hr_headers, json=build_vacancy_payload())

    assert response.status_code == 201
    payload = response.json()
    assert payload["status"] == "draft"
    assert payload["payment_required"] is True
    vacancy = db_session.get(Vacancy, UUID(payload["id"]))
    assert vacancy is not None
    assert vacancy.hr_user_id == hr_user.id


def test_created_vacancy_does_not_appear_in_public_feed_before_payment(
    client: TestClient,
    db_session: Session,
    settings,
) -> None:
    create_hr_fixture(db_session, telegram_id=890004, suffix="feedbefore")
    hr_headers = authenticate_user(client, settings, telegram_id=890004, username="hr_feedbefore")
    create_response = client.post("/api/hr/vacancies", headers=hr_headers, json=build_vacancy_payload(title="Not Yet Public"))

    feed_response = client.get("/api/vacancies")

    assert create_response.status_code == 201
    titles = [item["title"] for item in feed_response.json()["items"]]
    assert "Not Yet Public" not in titles


def test_hr_can_list_own_vacancies(
    client: TestClient,
    db_session: Session,
    settings,
) -> None:
    hr_user, company = create_hr_fixture(db_session, telegram_id=890005, suffix="listown")
    create_vacancy(db_session, hr_user=hr_user, company=company, title="Own vacancy", status=VacancyStatus.DRAFT)
    hr_headers = authenticate_user(client, settings, telegram_id=890005, username="hr_listown")

    response = client.get("/api/hr/vacancies", headers=hr_headers)

    assert response.status_code == 200
    assert len(response.json()["items"]) == 1
    assert response.json()["items"][0]["title"] == "Own vacancy"


def test_hr_cannot_access_another_hr_vacancy(
    client: TestClient,
    db_session: Session,
    settings,
) -> None:
    owner_user, owner_company = create_hr_fixture(db_session, telegram_id=890006, suffix="owner")
    vacancy = create_vacancy(db_session, hr_user=owner_user, company=owner_company, title="Private vacancy", status=VacancyStatus.DRAFT)
    create_hr_fixture(db_session, telegram_id=890007, suffix="other")
    other_headers = authenticate_user(client, settings, telegram_id=890007, username="hr_otherowner")

    response = client.get(f"/api/hr/vacancies/{vacancy.id}", headers=other_headers)

    assert response.status_code == 404


def test_hr_can_create_publication_payment_for_own_vacancy(
    client: TestClient,
    db_session: Session,
    settings,
) -> None:
    ensure_vacancy_publication_tariff(db_session)
    hr_user, company = create_hr_fixture(db_session, telegram_id=890008, suffix="payment")
    vacancy = create_vacancy(db_session, hr_user=hr_user, company=company, title="Pay me", status=VacancyStatus.DRAFT)
    hr_headers = authenticate_user(client, settings, telegram_id=890008, username="hr_payment")

    response = client.post(f"/api/hr/vacancies/{vacancy.id}/publish-payment", headers=hr_headers)

    assert response.status_code == 201
    payload = response.json()
    assert payload["status"] == "pending"
    payment = db_session.get(Payment, UUID(payload["payment_id"]))
    assert payment is not None
    assert payment.purpose == "hr_vacancy_publication"


def test_non_owner_hr_cannot_create_payment_for_another_hr_vacancy(
    client: TestClient,
    db_session: Session,
    settings,
) -> None:
    owner_user, owner_company = create_hr_fixture(db_session, telegram_id=890009, suffix="payowner")
    vacancy = create_vacancy(db_session, hr_user=owner_user, company=owner_company, title="Pay owner", status=VacancyStatus.DRAFT)
    create_hr_fixture(db_session, telegram_id=890010, suffix="payother")
    other_headers = authenticate_user(client, settings, telegram_id=890010, username="hr_payother")

    response = client.post(f"/api/hr/vacancies/{vacancy.id}/publish-payment", headers=other_headers)

    assert response.status_code == 404


def test_mock_payment_confirmation_activates_approved_vacancy(
    client: TestClient,
    db_session: Session,
    settings,
) -> None:
    ensure_vacancy_publication_tariff(db_session)
    hr_user, company = create_hr_fixture(db_session, telegram_id=890011, suffix="approve")
    vacancy = create_vacancy(db_session, hr_user=hr_user, company=company, title="Approved vacancy", status=VacancyStatus.DRAFT)
    hr_headers = authenticate_user(client, settings, telegram_id=890011, username="hr_approve")
    payment_response = client.post(f"/api/hr/vacancies/{vacancy.id}/publish-payment", headers=hr_headers)
    payment_id = payment_response.json()["payment_id"]

    confirm_response = client.post("/api/payments/mock-confirm", headers=hr_headers, json={"payment_id": payment_id})

    assert confirm_response.status_code == 200
    db_session.refresh(vacancy)
    assert vacancy.status is VacancyStatus.ACTIVE


def test_activated_vacancy_appears_in_public_feed(
    client: TestClient,
    db_session: Session,
    settings,
) -> None:
    ensure_vacancy_publication_tariff(db_session)
    hr_user, company = create_hr_fixture(db_session, telegram_id=890012, suffix="feedafter")
    vacancy = create_vacancy(db_session, hr_user=hr_user, company=company, title="Public after payment", status=VacancyStatus.DRAFT)
    hr_headers = authenticate_user(client, settings, telegram_id=890012, username="hr_feedafter")
    payment_id = client.post(f"/api/hr/vacancies/{vacancy.id}/publish-payment", headers=hr_headers).json()["payment_id"]
    client.post("/api/payments/mock-confirm", headers=hr_headers, json={"payment_id": payment_id})

    response = client.get("/api/vacancies")

    assert response.status_code == 200
    titles = [item["title"] for item in response.json()["items"]]
    assert "Public after payment" in titles


def test_rejected_vacancy_does_not_appear_in_public_feed(
    client: TestClient,
    db_session: Session,
    settings,
) -> None:
    ensure_vacancy_publication_tariff(db_session)
    hr_user, company = create_hr_fixture(db_session, telegram_id=890013, suffix="reject")
    vacancy = create_vacancy(
        db_session,
        hr_user=hr_user,
        company=company,
        title="Casino shift",
        status=VacancyStatus.DRAFT,
    )
    hr_headers = authenticate_user(client, settings, telegram_id=890013, username="hr_rejectvac")
    payment_id = client.post(f"/api/hr/vacancies/{vacancy.id}/publish-payment", headers=hr_headers).json()["payment_id"]

    client.post("/api/payments/mock-confirm", headers=hr_headers, json={"payment_id": payment_id})
    feed_response = client.get("/api/vacancies")

    db_session.refresh(vacancy)
    assert vacancy.status is VacancyStatus.REJECTED
    titles = [item["title"] for item in feed_response.json()["items"]]
    assert "Casino shift" not in titles


def test_manual_review_vacancy_does_not_appear_in_public_feed(
    client: TestClient,
    db_session: Session,
    settings,
) -> None:
    ensure_vacancy_publication_tariff(db_session)
    hr_user, company = create_hr_fixture(db_session, telegram_id=890014, suffix="manual")
    vacancy = create_vacancy(
        db_session,
        hr_user=hr_user,
        company=company,
        title="Unclear employer role",
        status=VacancyStatus.DRAFT,
    )
    vacancy.description = "Unknown employer, high income, crypto trading opportunity."
    db_session.commit()
    hr_headers = authenticate_user(client, settings, telegram_id=890014, username="hr_manual")
    payment_id = client.post(f"/api/hr/vacancies/{vacancy.id}/publish-payment", headers=hr_headers).json()["payment_id"]

    client.post("/api/payments/mock-confirm", headers=hr_headers, json={"payment_id": payment_id})
    feed_response = client.get("/api/vacancies")

    db_session.refresh(vacancy)
    assert vacancy.status is VacancyStatus.MANUAL_REVIEW
    titles = [item["title"] for item in feed_response.json()["items"]]
    assert "Unclear employer role" not in titles


def test_duplicate_payment_confirmation_is_idempotent(
    client: TestClient,
    db_session: Session,
    settings,
) -> None:
    ensure_vacancy_publication_tariff(db_session)
    hr_user, company = create_hr_fixture(db_session, telegram_id=890015, suffix="idempotent")
    vacancy = create_vacancy(db_session, hr_user=hr_user, company=company, title="Idempotent vacancy", status=VacancyStatus.DRAFT)
    hr_headers = authenticate_user(client, settings, telegram_id=890015, username="hr_idempotent")
    payment_id = UUID(client.post(f"/api/hr/vacancies/{vacancy.id}/publish-payment", headers=hr_headers).json()["payment_id"])

    first = client.post("/api/payments/mock-confirm", headers=hr_headers, json={"payment_id": str(payment_id)})
    second = client.post("/api/payments/mock-confirm", headers=hr_headers, json={"payment_id": str(payment_id)})

    assert first.status_code == 200
    assert second.status_code == 200
    payment = db_session.get(Payment, payment_id)
    assert payment is not None
    assert payment.status is PaymentStatus.SUCCEEDED
    db_session.refresh(vacancy)
    assert vacancy.status is VacancyStatus.ACTIVE


def test_hr_safe_vacancy_response_may_include_hidden_contacts_for_owner(
    client: TestClient,
    db_session: Session,
    settings,
) -> None:
    hr_user, company = create_hr_fixture(db_session, telegram_id=890016, suffix="hidden")
    vacancy = create_vacancy(db_session, hr_user=hr_user, company=company, title="Hidden contacts vacancy", status=VacancyStatus.DRAFT)
    hr_headers = authenticate_user(client, settings, telegram_id=890016, username="hr_hidden")

    response = client.get(f"/api/hr/vacancies/{vacancy.id}", headers=hr_headers)

    assert response.status_code == 200
    payload = response.json()
    assert payload["hidden_contacts"]["contact_phone"] == company.contact_phone
    assert payload["hidden_contacts"]["contact_email"] == company.contact_email


def test_student_and_guest_vacancy_responses_still_never_include_hr_contacts(
    client: TestClient,
    db_session: Session,
    settings,
) -> None:
    ensure_vacancy_publication_tariff(db_session)
    hr_user, company = create_hr_fixture(db_session, telegram_id=890017, suffix="publicsafe")
    vacancy = create_vacancy(db_session, hr_user=hr_user, company=company, title="Public safe vacancy", status=VacancyStatus.DRAFT)
    hr_headers = authenticate_user(client, settings, telegram_id=890017, username="hr_publicsafe")
    payment_id = client.post(f"/api/hr/vacancies/{vacancy.id}/publish-payment", headers=hr_headers).json()["payment_id"]
    client.post("/api/payments/mock-confirm", headers=hr_headers, json={"payment_id": payment_id})

    list_response = client.get("/api/vacancies")
    detail_response = client.get(f"/api/vacancies/{vacancy.id}", headers={"X-Guest-Id": "guest-hr-safe"})

    for payload in [list_response.json()["items"][0], detail_response.json()]:
        assert "contact_phone" not in payload
        assert "contact_email" not in payload
        assert "contact_telegram" not in payload
        assert "hidden_contacts" not in payload


def test_vacancy_lifecycle_events_are_logged(
    client: TestClient,
    db_session: Session,
    settings,
) -> None:
    ensure_vacancy_publication_tariff(db_session)
    hr_user, company = create_hr_fixture(db_session, telegram_id=890018, suffix="events")
    hr_headers = authenticate_user(client, settings, telegram_id=890018, username="hr_events_vac")
    create_response = client.post("/api/hr/vacancies", headers=hr_headers, json=build_vacancy_payload(title="Events vacancy"))
    vacancy_id = UUID(create_response.json()["id"])
    payment_id = client.post(f"/api/hr/vacancies/{vacancy_id}/publish-payment", headers=hr_headers).json()["payment_id"]
    client.post("/api/payments/mock-confirm", headers=hr_headers, json={"payment_id": payment_id})

    event_names = {
        event.event_name
        for event in db_session.scalars(select(Event).where(Event.user_id == hr_user.id)).all()
    }
    assert "vacancy_created" in event_names
    assert "vacancy_payment_created" in event_names
    assert "vacancy_payment_succeeded" in event_names
    assert "vacancy_submitted_to_moderation" in event_names
    assert any(name in event_names for name in {"vacancy_approved", "vacancy_rejected", "vacancy_manual_review"})
