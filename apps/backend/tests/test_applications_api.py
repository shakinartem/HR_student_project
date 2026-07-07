from __future__ import annotations

from datetime import UTC, datetime, timedelta
from uuid import UUID

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.enums import ApplicationStatus, ComplaintStatus, HRStatus, SubscriptionStatus, UserRole, VacancyStatus
from app.models import Application, Complaint, Event, HRProfile, StudentProfile, Subscription, User, Vacancy
from app.models.organization import Company

from .test_student_finance_api import ensure_student_monthly_tariff


def get_user_by_telegram_id(db_session: Session, telegram_id: int) -> User:
    return db_session.scalar(select(User).where(User.telegram_id == telegram_id))


def ensure_student_user(
    db_session: Session,
    *,
    telegram_id: int = 777001,
    username: str = "student_user",
    first_name: str = "Student",
    last_name: str = "User",
) -> User:
    user = get_user_by_telegram_id(db_session, telegram_id)
    if user is None:
        user = User(
            telegram_id=telegram_id,
            role=UserRole.STUDENT,
            username=username,
            first_name=first_name,
            last_name=last_name,
            phone="+79990000000",
            email=f"{username}@example.com",
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
    return user


def ensure_student_profile_completed(db_session: Session, *, user: User) -> StudentProfile:
    profile = user.student_profile
    if profile is None:
        profile = StudentProfile(
            user_id=user.id,
            university="SGTU",
            course=2,
            speciality="Computer Science",
            preferred_job_types=["part_time"],
            preferred_schedule=["evening"],
            preferred_districts=["center"],
            experience_text="Worked two months as a waiter.",
            profile_completed=True,
        )
        db_session.add(profile)
        db_session.commit()
        db_session.refresh(profile)
    return profile


def ensure_active_subscription(db_session: Session, *, user: User) -> Subscription:
    subscription = db_session.scalar(select(Subscription).where(Subscription.user_id == user.id))
    now = datetime.now(UTC)
    if subscription is None:
        subscription = Subscription(
            user_id=user.id,
            starts_at=now,
            expires_at=now + timedelta(days=30),
            status=SubscriptionStatus.ACTIVE,
        )
        db_session.add(subscription)
    else:
        subscription.starts_at = now
        subscription.expires_at = now + timedelta(days=30)
        subscription.status = SubscriptionStatus.ACTIVE
    db_session.commit()
    db_session.refresh(subscription)
    return subscription


def create_hr_fixture(
    db_session: Session,
    *,
    telegram_id: int,
    suffix: str,
) -> tuple[User, Company]:
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
    user = User(
        telegram_id=telegram_id,
        role=UserRole.HR,
        username=f"hr_{suffix}",
        first_name="HR",
        last_name="Owner",
        phone="+79991111111",
        email=f"hr-{suffix}@example.com",
    )
    db_session.add_all([company, user])
    db_session.flush()
    db_session.add(
        HRProfile(
            user_id=user.id,
            company_id=company.id,
            position="Recruiter",
            verified_status=HRStatus.ACTIVE,
        )
    )
    db_session.commit()
    db_session.refresh(user)
    db_session.refresh(company)
    return user, company


def create_vacancy(
    db_session: Session,
    *,
    hr_user: User,
    company: Company,
    title: str,
    status: VacancyStatus = VacancyStatus.ACTIVE,
) -> Vacancy:
    vacancy = Vacancy(
        company_id=company.id,
        hr_user_id=hr_user.id,
        title=title,
        category="restaurant",
        job_type="shift",
        schedule="evening",
        salary_text="2500 RUB/shift",
        salary_min=2500,
        salary_max=None,
        district="center",
        address="Public address",
        format="offline",
        description="Safe public description",
        responsibilities="Public responsibilities",
        requirements="Public requirements",
        conditions="Public conditions",
        experience_required=False,
        status=status,
        moderation_status="approved" if status is VacancyStatus.ACTIVE else "manual_review",
        is_promoted=False,
        published_at=datetime.now(UTC),
    )
    db_session.add(vacancy)
    db_session.commit()
    db_session.refresh(vacancy)
    return vacancy


def create_application(
    db_session: Session,
    *,
    vacancy: Vacancy,
    student_user: User,
    status: ApplicationStatus = ApplicationStatus.SENT,
) -> Application:
    application = Application(
        vacancy_id=vacancy.id,
        student_user_id=student_user.id,
        hr_user_id=vacancy.hr_user_id,
        status=status,
        student_comment="I can start this week.",
        accepted_at=datetime.now(UTC) if status is ApplicationStatus.ACCEPTED else None,
        rejected_at=datetime.now(UTC) if status is ApplicationStatus.REJECTED else None,
    )
    db_session.add(application)
    db_session.commit()
    db_session.refresh(application)
    return application


def authenticate_user(client: TestClient, settings, *, telegram_id: int, username: str) -> dict[str, str]:
    from .conftest import build_init_data

    init_data = build_init_data(bot_token=settings.telegram_bot_token, telegram_id=telegram_id, username=username)
    response = client.post("/api/auth/telegram", json={"init_data": init_data})
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def setup_student_ready_for_application(db_session: Session) -> User:
    ensure_student_monthly_tariff(db_session)
    student_user = ensure_student_user(db_session)
    ensure_student_profile_completed(db_session, user=student_user)
    ensure_active_subscription(db_session, user=student_user)
    return student_user


def test_guest_cannot_apply(client: TestClient, db_session: Session) -> None:
    hr_user, company = create_hr_fixture(db_session, telegram_id=880001, suffix="guest")
    vacancy = create_vacancy(db_session, hr_user=hr_user, company=company, title="Guest blocked vacancy")

    response = client.post(f"/api/vacancies/{vacancy.id}/apply", json={"student_comment": "Hello"})

    assert response.status_code == 401


def test_student_without_active_subscription_cannot_apply(
    client: TestClient,
    auth_headers: dict[str, str],
    db_session: Session,
) -> None:
    student_user = get_user_by_telegram_id(db_session, 777001)
    ensure_student_profile_completed(db_session, user=student_user)
    hr_user, company = create_hr_fixture(db_session, telegram_id=880002, suffix="nosub")
    vacancy = create_vacancy(db_session, hr_user=hr_user, company=company, title="Requires subscription")

    response = client.post(
        f"/api/vacancies/{vacancy.id}/apply",
        headers=auth_headers,
        json={"student_comment": "Ready to work."},
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Active subscription required"


def test_student_with_active_subscription_can_apply(
    client: TestClient,
    auth_headers: dict[str, str],
    db_session: Session,
) -> None:
    setup_student_ready_for_application(db_session)
    hr_user, company = create_hr_fixture(db_session, telegram_id=880003, suffix="apply")
    vacancy = create_vacancy(db_session, hr_user=hr_user, company=company, title="Can apply vacancy")

    response = client.post(
        f"/api/vacancies/{vacancy.id}/apply",
        headers=auth_headers,
        json={"student_comment": "I can start this week."},
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["vacancy_id"] == str(vacancy.id)
    assert payload["status"] == "sent"
    assert "contacts" not in payload
    assert "hr_phone" not in payload


def test_student_cannot_apply_to_inactive_vacancy(
    client: TestClient,
    auth_headers: dict[str, str],
    db_session: Session,
) -> None:
    setup_student_ready_for_application(db_session)
    hr_user, company = create_hr_fixture(db_session, telegram_id=880004, suffix="inactive")
    vacancy = create_vacancy(
        db_session,
        hr_user=hr_user,
        company=company,
        title="Inactive vacancy",
        status=VacancyStatus.DRAFT,
    )

    response = client.post(
        f"/api/vacancies/{vacancy.id}/apply",
        headers=auth_headers,
        json={"student_comment": "Interested."},
    )

    assert response.status_code == 404


def test_student_cannot_apply_to_vacancy_without_approved_moderation(
    client: TestClient,
    auth_headers: dict[str, str],
    db_session: Session,
) -> None:
    student = setup_student_ready_for_application(db_session)
    hr_user, company = create_hr_fixture(db_session, telegram_id=8800042, suffix="moderation")
    vacancy = create_vacancy(
        db_session,
        hr_user=hr_user,
        company=company,
        title="Moderation vacancy",
        status=VacancyStatus.ACTIVE,
        moderation_status="manual_review",
    )
    db_session.commit()

    response = client.post(
        f"/api/vacancies/{vacancy.id}/apply",
        headers=auth_headers,
        json={"student_comment": "Interested."},
    )

    assert response.status_code == 404


def test_hr_cannot_access_applications_of_another_company(
    client: TestClient,
    db_session: Session,
    settings,
) -> None:
    student_user = setup_student_ready_for_application(db_session)
    owner_hr, owner_company = create_hr_fixture(db_session, telegram_id=880021, suffix="owner_apps")
    vacancy = create_vacancy(db_session, hr_user=owner_hr, company=owner_company, title="Foreign vacancy")
    create_application(db_session, vacancy=vacancy, student_user=student_user)
    other_hr, _ = create_hr_fixture(db_session, telegram_id=880022, suffix="other_apps")
    hr_headers = authenticate_user(client, settings, telegram_id=880022, username="hr_other_apps")

    response_list = client.get("/api/hr/applications", headers=hr_headers)
    assert response_list.status_code == 200
    assert response_list.json()["items"] == []


def test_student_cannot_apply_twice_to_same_vacancy(
    client: TestClient,
    auth_headers: dict[str, str],
    db_session: Session,
) -> None:
    student_user = setup_student_ready_for_application(db_session)
    hr_user, company = create_hr_fixture(db_session, telegram_id=880005, suffix="twice")
    vacancy = create_vacancy(db_session, hr_user=hr_user, company=company, title="One-time vacancy")
    create_application(db_session, vacancy=vacancy, student_user=student_user)

    response = client.post(
        f"/api/vacancies/{vacancy.id}/apply",
        headers=auth_headers,
        json={"student_comment": "Interested."},
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "Application already exists"


def test_muted_student_cannot_apply(
    client: TestClient,
    auth_headers: dict[str, str],
    db_session: Session,
) -> None:
    student_user = setup_student_ready_for_application(db_session)
    student_user.mute_until = datetime.now(UTC) + timedelta(hours=1)
    db_session.commit()
    hr_user, company = create_hr_fixture(db_session, telegram_id=880006, suffix="muted")
    vacancy = create_vacancy(db_session, hr_user=hr_user, company=company, title="Muted blocked")

    response = client.post(
        f"/api/vacancies/{vacancy.id}/apply",
        headers=auth_headers,
        json={"student_comment": "Interested."},
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Muted student cannot apply"


def test_blocked_student_cannot_apply(
    client: TestClient,
    auth_headers: dict[str, str],
    db_session: Session,
) -> None:
    student_user = setup_student_ready_for_application(db_session)
    student_user.is_blocked = True
    db_session.commit()
    hr_user, company = create_hr_fixture(db_session, telegram_id=880007, suffix="blocked")
    vacancy = create_vacancy(db_session, hr_user=hr_user, company=company, title="Blocked student vacancy")

    response = client.post(
        f"/api/vacancies/{vacancy.id}/apply",
        headers=auth_headers,
        json={"student_comment": "Interested."},
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "User is blocked"


def test_student_application_list_has_no_hr_contacts(
    client: TestClient,
    auth_headers: dict[str, str],
    db_session: Session,
) -> None:
    student_user = setup_student_ready_for_application(db_session)
    hr_user, company = create_hr_fixture(db_session, telegram_id=880008, suffix="list")
    vacancy = create_vacancy(db_session, hr_user=hr_user, company=company, title="List vacancy")
    create_application(db_session, vacancy=vacancy, student_user=student_user, status=ApplicationStatus.ACCEPTED)

    response = client.get("/api/student/applications", headers=auth_headers)

    assert response.status_code == 200
    payload = response.json()["items"][0]
    assert payload["status"] == "accepted"
    assert "contacts" not in payload
    assert "hr_phone" not in payload
    assert "hr_email" not in payload


def test_hr_can_list_applications_for_own_vacancies(
    client: TestClient,
    db_session: Session,
    settings,
) -> None:
    student_user = setup_student_ready_for_application(db_session)
    hr_user, company = create_hr_fixture(db_session, telegram_id=880009, suffix="owner")
    vacancy = create_vacancy(db_session, hr_user=hr_user, company=company, title="Owned vacancy")
    create_application(db_session, vacancy=vacancy, student_user=student_user)
    hr_headers = authenticate_user(client, settings, telegram_id=880009, username="hr_owner")

    response = client.get("/api/hr/applications", headers=hr_headers)

    assert response.status_code == 200
    items = response.json()["items"]
    assert len(items) == 1
    assert items[0]["vacancy_id"] == str(vacancy.id)
    assert items[0]["contacts"] is None


def test_hr_cannot_list_applications_for_another_hr(
    client: TestClient,
    db_session: Session,
    settings,
) -> None:
    student_user = setup_student_ready_for_application(db_session)
    owner_hr, owner_company = create_hr_fixture(db_session, telegram_id=880010, suffix="owner2")
    vacancy = create_vacancy(db_session, hr_user=owner_hr, company=owner_company, title="Foreign vacancy")
    create_application(db_session, vacancy=vacancy, student_user=student_user)
    other_hr, _ = create_hr_fixture(db_session, telegram_id=880011, suffix="other")
    hr_headers = authenticate_user(client, settings, telegram_id=880011, username="hr_other")

    response = client.get("/api/hr/applications", headers=hr_headers)

    assert response.status_code == 200
    assert response.json()["items"] == []


def test_hr_application_before_accept_has_contacts_null(
    client: TestClient,
    db_session: Session,
    settings,
) -> None:
    student_user = setup_student_ready_for_application(db_session)
    hr_user, company = create_hr_fixture(db_session, telegram_id=880012, suffix="detail")
    vacancy = create_vacancy(db_session, hr_user=hr_user, company=company, title="Detail vacancy")
    application = create_application(db_session, vacancy=vacancy, student_user=student_user)
    hr_headers = authenticate_user(client, settings, telegram_id=880012, username="hr_detail")

    response = client.get(f"/api/hr/applications/{application.id}", headers=hr_headers)

    assert response.status_code == 200
    payload = response.json()
    assert payload["contacts"] is None
    assert payload["student"]["first_name"] == student_user.first_name


def test_hr_accept_changes_status_to_accepted_and_reveals_contacts(
    client: TestClient,
    db_session: Session,
    settings,
) -> None:
    student_user = setup_student_ready_for_application(db_session)
    hr_user, company = create_hr_fixture(db_session, telegram_id=880013, suffix="accept")
    vacancy = create_vacancy(db_session, hr_user=hr_user, company=company, title="Accept vacancy")
    application = create_application(db_session, vacancy=vacancy, student_user=student_user)
    hr_headers = authenticate_user(client, settings, telegram_id=880013, username="hr_accept")

    response = client.post(f"/api/hr/applications/{application.id}/accept", headers=hr_headers)

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "accepted"
    assert payload["contacts"] == {
        "phone": student_user.phone,
        "email": student_user.email,
        "telegram_username": student_user.username,
    }


def test_hr_cannot_accept_application_for_another_hr(
    client: TestClient,
    db_session: Session,
    settings,
) -> None:
    student_user = setup_student_ready_for_application(db_session)
    owner_hr, owner_company = create_hr_fixture(db_session, telegram_id=880014, suffix="owner3")
    vacancy = create_vacancy(db_session, hr_user=owner_hr, company=owner_company, title="Protected vacancy")
    application = create_application(db_session, vacancy=vacancy, student_user=student_user)
    other_hr, _ = create_hr_fixture(db_session, telegram_id=880015, suffix="other3")
    hr_headers = authenticate_user(client, settings, telegram_id=880015, username="hr_other3")

    response = client.post(f"/api/hr/applications/{application.id}/accept", headers=hr_headers)

    assert response.status_code == 404


def test_hr_reject_changes_status_to_rejected(
    client: TestClient,
    db_session: Session,
    settings,
) -> None:
    student_user = setup_student_ready_for_application(db_session)
    hr_user, company = create_hr_fixture(db_session, telegram_id=880016, suffix="reject")
    vacancy = create_vacancy(db_session, hr_user=hr_user, company=company, title="Reject vacancy")
    application = create_application(db_session, vacancy=vacancy, student_user=student_user)
    hr_headers = authenticate_user(client, settings, telegram_id=880016, username="hr_reject")

    response = client.post(f"/api/hr/applications/{application.id}/reject", headers=hr_headers)

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "rejected"
    assert payload["contacts"] is None


def test_hr_complaint_creates_complaint_row(
    client: TestClient,
    db_session: Session,
    settings,
) -> None:
    student_user = setup_student_ready_for_application(db_session)
    hr_user, company = create_hr_fixture(db_session, telegram_id=880017, suffix="complaint")
    vacancy = create_vacancy(db_session, hr_user=hr_user, company=company, title="Complaint vacancy")
    application = create_application(db_session, vacancy=vacancy, student_user=student_user)
    hr_headers = authenticate_user(client, settings, telegram_id=880017, username="hr_complaint")

    response = client.post(
        f"/api/hr/applications/{application.id}/complain",
        headers=hr_headers,
        json={"reason": "No-show at interview"},
    )

    assert response.status_code == 201
    complaint = db_session.scalar(select(Complaint).where(Complaint.application_id == application.id))
    assert complaint is not None
    assert complaint.status is ComplaintStatus.OPEN


def test_student_still_does_not_see_hr_contacts_after_hr_accepts(
    client: TestClient,
    auth_headers: dict[str, str],
    db_session: Session,
    settings,
) -> None:
    student_user = setup_student_ready_for_application(db_session)
    hr_user, company = create_hr_fixture(db_session, telegram_id=880018, suffix="student-safe")
    vacancy = create_vacancy(db_session, hr_user=hr_user, company=company, title="Safe visibility vacancy")
    application = create_application(db_session, vacancy=vacancy, student_user=student_user)
    hr_headers = authenticate_user(client, settings, telegram_id=880018, username="hr_safe")

    client.post(f"/api/hr/applications/{application.id}/accept", headers=hr_headers)
    response = client.get("/api/student/applications", headers=auth_headers)

    assert response.status_code == 200
    payload = response.json()["items"][0]
    assert payload["status"] == "accepted"
    assert "contacts" not in payload
    assert "contact_phone" not in payload


def test_application_lifecycle_events_are_logged(
    client: TestClient,
    auth_headers: dict[str, str],
    db_session: Session,
    settings,
) -> None:
    student_user = setup_student_ready_for_application(db_session)
    hr_user, company = create_hr_fixture(db_session, telegram_id=880019, suffix="events")
    vacancy = create_vacancy(db_session, hr_user=hr_user, company=company, title="Events vacancy")

    create_response = client.post(
        f"/api/vacancies/{vacancy.id}/apply",
        headers=auth_headers,
        json={"student_comment": "Ready to work."},
    )
    application_id = UUID(create_response.json()["id"])
    hr_headers = authenticate_user(client, settings, telegram_id=880019, username="hr_events")
    client.post(f"/api/hr/applications/{application_id}/accept", headers=hr_headers)
    client.post(
        f"/api/hr/applications/{application_id}/complain",
        headers=hr_headers,
        json={"reason": "Duplicate profile"},
    )

    other_vacancy = create_vacancy(db_session, hr_user=hr_user, company=company, title="Reject events vacancy")
    rejected_application = create_application(db_session, vacancy=other_vacancy, student_user=student_user)
    client.post(f"/api/hr/applications/{rejected_application.id}/reject", headers=hr_headers)

    event_names = {
        event.event_name
        for event in db_session.scalars(select(Event).where(Event.user_id.in_([student_user.id, hr_user.id]))).all()
    }
    assert "application_created" in event_names
    assert "application_accepted" in event_names
    assert "application_rejected" in event_names
    assert "complaint_created" in event_names
