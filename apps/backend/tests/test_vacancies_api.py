from __future__ import annotations

from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.enums import HRStatus, UserRole, VacancyStatus
from app.models import Company, HRProfile, User, Vacancy, VacancyView


def create_hr_with_company(db_session: Session, *, suffix: str = "main") -> tuple[Company, User]:
    telegram_id = 300000 + sum(ord(char) for char in suffix)
    company = Company(
        name=f"Company {suffix}",
        inn=f"6450000{suffix}",
        description="Public company description",
        contact_name="Hidden Contact",
        contact_phone="+79990000000",
        contact_email=f"hidden-{suffix}@example.com",
        contact_telegram=f"hidden_{suffix}",
        status="active",
    )
    hr_user = User(
        telegram_id=telegram_id,
        role=UserRole.HR,
        username=f"hr_{suffix}",
        first_name="HR",
        last_name="Owner",
        phone="+79991111111",
        email=f"hr-{suffix}@example.com",
    )
    db_session.add_all([company, hr_user])
    db_session.flush()
    db_session.add(
        HRProfile(
            user=hr_user,
            company=company,
            position="Recruiter",
            verified_status=HRStatus.ACTIVE,
        )
    )
    db_session.flush()
    return company, hr_user


def create_vacancy(
    db_session: Session,
    *,
    company: Company,
    hr_user: User,
    title: str,
    status: VacancyStatus = VacancyStatus.ACTIVE,
    published_at: datetime | None = None,
    expires_at: datetime | None = None,
    job_type: str = "shift",
    district: str = "center",
    salary_min: int | None = 2500,
    salary_text: str = "2500 RUB/shift",
    is_promoted: bool = False,
    moderation_status: str = "approved",
    vacancy_format: str = "offline",
) -> Vacancy:
    vacancy = Vacancy(
        company=company,
        hr_user=hr_user,
        title=title,
        category="restaurant",
        job_type=job_type,
        schedule="evening",
        salary_text=salary_text,
        salary_min=salary_min,
        salary_max=None,
        district=district,
        address="Public address",
        format=vacancy_format,
        description="Safe public description",
        responsibilities="Public responsibilities",
        requirements="Public requirements",
        conditions="Public conditions",
        experience_required=False,
        status=status,
        moderation_status=moderation_status,
        is_promoted=is_promoted,
        published_at=published_at or datetime.now(UTC),
        expires_at=expires_at,
    )
    db_session.add(vacancy)
    db_session.flush()
    return vacancy


def seed_vacancies(db_session: Session) -> dict[str, Vacancy]:
    company, hr_user = create_hr_with_company(db_session)
    now = datetime.now(UTC)
    vacancies = {
        "promoted_active": create_vacancy(
            db_session,
            company=company,
            hr_user=hr_user,
            title="Promoted active vacancy",
            is_promoted=True,
            published_at=now - timedelta(hours=1),
            salary_min=3200,
            district="center",
            job_type="shift",
        ),
        "recent_active": create_vacancy(
            db_session,
            company=company,
            hr_user=hr_user,
            title="Recent active vacancy",
            is_promoted=False,
            published_at=now,
            salary_min=2800,
            district="leninsky",
            job_type="part_time",
        ),
        "old_active": create_vacancy(
            db_session,
            company=company,
            hr_user=hr_user,
            title="Old active vacancy",
            published_at=now - timedelta(days=1),
            salary_min=1800,
            district="kirovsky",
            job_type="weekend",
        ),
        "draft": create_vacancy(
            db_session,
            company=company,
            hr_user=hr_user,
            title="Draft vacancy",
            status=VacancyStatus.DRAFT,
            moderation_status="manual_review",
        ),
        "awaiting_payment": create_vacancy(
            db_session,
            company=company,
            hr_user=hr_user,
            title="Awaiting payment vacancy",
            status=VacancyStatus.AWAITING_PAYMENT,
            moderation_status="manual_review",
        ),
        "moderation": create_vacancy(
            db_session,
            company=company,
            hr_user=hr_user,
            title="Moderation vacancy",
            status=VacancyStatus.MODERATION,
            moderation_status="manual_review",
        ),
        "manual_review": create_vacancy(
            db_session,
            company=company,
            hr_user=hr_user,
            title="Manual review vacancy",
            status=VacancyStatus.MANUAL_REVIEW,
            moderation_status="manual_review",
        ),
        "rejected": create_vacancy(
            db_session,
            company=company,
            hr_user=hr_user,
            title="Rejected vacancy",
            status=VacancyStatus.REJECTED,
            moderation_status="rejected",
        ),
        "archived": create_vacancy(
            db_session,
            company=company,
            hr_user=hr_user,
            title="Archived vacancy",
            status=VacancyStatus.ARCHIVED,
        ),
        "expired_status": create_vacancy(
            db_session,
            company=company,
            hr_user=hr_user,
            title="Expired vacancy",
            status=VacancyStatus.EXPIRED,
        ),
        "expired_time": create_vacancy(
            db_session,
            company=company,
            hr_user=hr_user,
            title="Time expired vacancy",
            status=VacancyStatus.ACTIVE,
            expires_at=now - timedelta(minutes=1),
        ),
    }
    db_session.commit()
    return vacancies


def test_active_vacancies_appear_in_feed_and_non_active_do_not(
    client: TestClient,
    db_session: Session,
) -> None:
    vacancies = seed_vacancies(db_session)

    response = client.get("/api/vacancies")

    assert response.status_code == 200
    titles = [item["title"] for item in response.json()["items"]]
    assert vacancies["promoted_active"].title in titles
    assert vacancies["recent_active"].title in titles
    assert vacancies["old_active"].title in titles
    assert vacancies["draft"].title not in titles
    assert vacancies["awaiting_payment"].title not in titles
    assert vacancies["moderation"].title not in titles
    assert vacancies["manual_review"].title not in titles
    assert vacancies["rejected"].title not in titles
    assert vacancies["archived"].title not in titles
    assert vacancies["expired_status"].title not in titles
    assert vacancies["expired_time"].title not in titles


def test_feed_response_has_no_hr_or_hidden_contact_fields(client: TestClient, db_session: Session) -> None:
    seed_vacancies(db_session)

    response = client.get("/api/vacancies")

    assert response.status_code == 200
    item = response.json()["items"][0]
    forbidden_fields = {
        "contact_phone",
        "contact_email",
        "contact_telegram",
        "hr_phone",
        "hr_email",
        "hr_telegram",
        "hidden_contacts",
    }
    assert forbidden_fields.isdisjoint(item.keys())


def test_vacancy_detail_has_no_hr_contact_fields(client: TestClient, db_session: Session) -> None:
    vacancies = seed_vacancies(db_session)

    response = client.get(
        f"/api/vacancies/{vacancies['recent_active'].id}",
        headers={"X-Guest-Id": "guest-1"},
    )

    assert response.status_code == 200
    payload = response.json()
    forbidden_fields = {
        "contact_phone",
        "contact_email",
        "contact_telegram",
        "hr_phone",
        "hr_email",
        "hr_telegram",
        "hidden_contacts",
    }
    assert forbidden_fields.isdisjoint(payload.keys())
    assert payload["company_name"] == "Company main"


def test_missing_guest_id_for_anonymous_detail_returns_400(client: TestClient, db_session: Session) -> None:
    vacancies = seed_vacancies(db_session)

    response = client.get(f"/api/vacancies/{vacancies['recent_active'].id}")

    assert response.status_code == 400
    assert response.json()["detail"] == "Anonymous vacancy preview requires X-Guest-Id header"


def test_guest_with_guest_id_can_view_three_unique_vacancies_but_fourth_is_blocked(client: TestClient, db_session: Session) -> None:
    vacancies = seed_vacancies(db_session)
    view_ids = [
        vacancies["promoted_active"].id,
        vacancies["recent_active"].id,
        vacancies["old_active"].id,
    ]

    for vacancy_id in view_ids:
        response = client.get(f"/api/vacancies/{vacancy_id}", headers={"X-Guest-Id": "guest-2"})
        assert response.status_code == 200

    blocked = client.get(
        f"/api/vacancies/{vacancies['draft'].id}",
        headers={"X-Guest-Id": "guest-2"},
    )
    assert blocked.status_code == 404

    extra_company, extra_hr = create_hr_with_company(db_session, suffix="extra")
    extra_vacancy = create_vacancy(
        db_session,
        company=extra_company,
        hr_user=extra_hr,
        title="Fourth active vacancy",
        status=VacancyStatus.ACTIVE,
    )
    db_session.commit()

    blocked = client.get(f"/api/vacancies/{extra_vacancy.id}", headers={"X-Guest-Id": "guest-2"})
    assert blocked.status_code == 403
    assert blocked.json()["detail"]["code"] == "GUEST_VIEW_LIMIT_REACHED"


def test_reopening_already_viewed_vacancy_does_not_consume_extra_view(client: TestClient, db_session: Session) -> None:
    vacancies = seed_vacancies(db_session)

    first = client.get(f"/api/vacancies/{vacancies['recent_active'].id}", headers={"X-Guest-Id": "guest-3"})
    second = client.get(f"/api/vacancies/{vacancies['recent_active'].id}", headers={"X-Guest-Id": "guest-3"})
    third = client.get(f"/api/vacancies/{vacancies['promoted_active'].id}", headers={"X-Guest-Id": "guest-3"})
    fourth = client.get(f"/api/vacancies/{vacancies['old_active'].id}", headers={"X-Guest-Id": "guest-3"})

    assert first.status_code == 200
    assert second.status_code == 200
    assert third.status_code == 200
    assert fourth.status_code == 200


def test_post_view_cannot_bypass_guest_limit(client: TestClient, db_session: Session) -> None:
    vacancies = seed_vacancies(db_session)
    guest_headers = {"X-Guest-Id": "guest-4"}
    for vacancy_id in [
        vacancies["promoted_active"].id,
        vacancies["recent_active"].id,
        vacancies["old_active"].id,
    ]:
        assert client.post(f"/api/vacancies/{vacancy_id}/view", headers=guest_headers).status_code == 200

    extra_company, extra_hr = create_hr_with_company(db_session, suffix="view")
    extra_vacancy = create_vacancy(
        db_session,
        company=extra_company,
        hr_user=extra_hr,
        title="Blocked by POST view",
        status=VacancyStatus.ACTIVE,
    )
    db_session.commit()

    blocked = client.post(f"/api/vacancies/{extra_vacancy.id}/view", headers=guest_headers)
    assert blocked.status_code == 403
    assert blocked.json()["detail"]["code"] == "GUEST_VIEW_LIMIT_REACHED"


def test_authenticated_user_views_are_tracked_by_user_id(
    client: TestClient,
    auth_headers: dict[str, str],
    db_session: Session,
) -> None:
    vacancies = seed_vacancies(db_session)

    response = client.get(f"/api/vacancies/{vacancies['recent_active'].id}", headers=auth_headers)

    assert response.status_code == 200
    user = db_session.scalar(select(User).where(User.telegram_id == 777001))
    views = db_session.scalars(select(VacancyView).where(VacancyView.user_id == user.id)).all()
    assert len(views) == 1
    assert views[0].vacancy_id == vacancies["recent_active"].id


def test_filters_work_for_job_type_district_and_salary_min(client: TestClient, db_session: Session) -> None:
    seed_vacancies(db_session)

    response = client.get(
        "/api/vacancies",
        params={
            "job_type": "part_time",
            "district": "leninsky",
            "salary_min": 2500,
        },
    )

    assert response.status_code == 200
    items = response.json()["items"]
    assert len(items) == 1
    assert items[0]["job_type"] == "part_time"
    assert items[0]["district"] == "leninsky"
    assert items[0]["salary_min"] == 2800


def test_promoted_vacancies_sort_before_non_promoted_by_default(client: TestClient, db_session: Session) -> None:
    seed_vacancies(db_session)

    response = client.get("/api/vacancies")

    assert response.status_code == 200
    items = response.json()["items"]
    assert items[0]["is_promoted"] is True
    assert items[0]["title"] == "Promoted active vacancy"
