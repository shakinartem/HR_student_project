from datetime import UTC, datetime
from uuid import uuid4

from app.core.enums import ApplicationStatus, HRStatus, UserRole, VacancyStatus
from app.models import (
    Application,
    Company,
    HRProfile,
    StudentProfile,
    User,
    Vacancy,
)
from app.services.visibility import (
    can_hr_view_student_contacts,
    serialize_application_for_hr,
    serialize_application_for_student,
    serialize_vacancy_for_student,
)


def build_hr_user(*, role: UserRole = UserRole.HR, company_id=None, user_id=None) -> User:
    hr_user = User(
        id=user_id or uuid4(),
        telegram_id=10,
        role=role,
        username="hr_user",
        first_name="Hannah",
        last_name="Recruiter",
        phone="+79990001111",
        email="hr@example.com",
    )
    hr_user.hr_profile = HRProfile(
        id=uuid4(),
        user=hr_user,
        company_id=company_id or uuid4(),
        position="Recruiter",
        verified_status=HRStatus.ACTIVE,
    )
    return hr_user


def build_application(*, status: ApplicationStatus = ApplicationStatus.SENT, owner_hr: User | None = None):
    company = Company(
        id=owner_hr.hr_profile.company_id if owner_hr else uuid4(),
        name="Verhoff",
        inn="6450000001",
        description="Student-friendly employer",
        contact_name="Hidden HR",
        contact_phone="+79990002222",
        contact_email="company@example.com",
        contact_telegram="hidden_hr",
        status="active",
    )
    hr_user = owner_hr or build_hr_user(company_id=company.id)
    student_user = User(
        id=uuid4(),
        telegram_id=20,
        role=UserRole.STUDENT,
        username="student_username",
        first_name="Ivan",
        last_name="Student",
        phone="+79990000000",
        email="student@example.com",
    )
    student_user.student_profile = StudentProfile(
        id=uuid4(),
        user=student_user,
        university="SGTU",
        course=2,
        speciality="Computer Science",
        preferred_job_types=["shift"],
        preferred_schedule=["evening"],
        preferred_districts=["center"],
        experience_text="Worked part-time for two months",
        profile_completed=True,
    )
    vacancy = Vacancy(
        id=uuid4(),
        company=company,
        company_id=company.id,
        hr_user=hr_user,
        hr_user_id=hr_user.id,
        title="Waiter evening shift",
        category="restaurant",
        job_type="shift",
        schedule="evening",
        salary_text="2500 RUB/shift",
        district="center",
        address="Lenina 1",
        format="offline",
        description="Serve guests",
        responsibilities="Serve guests",
        requirements="Polite communication",
        conditions="Flexible shifts",
        experience_required=False,
        status=VacancyStatus.ACTIVE,
        moderation_status="approved",
        is_promoted=False,
        published_at=datetime(2026, 7, 1, tzinfo=UTC),
    )
    application = Application(
        id=uuid4(),
        vacancy=vacancy,
        vacancy_id=vacancy.id,
        student_user=student_user,
        student_user_id=student_user.id,
        hr_user=hr_user,
        hr_user_id=hr_user.id,
        status=status,
        student_comment="I can start this week",
        created_at=datetime(2026, 7, 2, tzinfo=UTC),
    )
    return hr_user, student_user, company, vacancy, application


def test_hr_cannot_view_student_contacts_before_acceptance() -> None:
    hr_user, _, _, vacancy, application = build_application(status=ApplicationStatus.SENT)

    assert can_hr_view_student_contacts(hr_user, application, vacancy) is False


def test_hr_can_view_student_contacts_after_acceptance_for_own_vacancy() -> None:
    hr_user, _, _, vacancy, application = build_application(status=ApplicationStatus.ACCEPTED)

    assert can_hr_view_student_contacts(hr_user, application, vacancy) is True


def test_other_hr_cannot_view_student_contacts_for_foreign_vacancy() -> None:
    owner_hr = build_hr_user()
    _, _, _, vacancy, application = build_application(
        status=ApplicationStatus.ACCEPTED,
        owner_hr=owner_hr,
    )
    foreign_hr = build_hr_user(company_id=uuid4(), user_id=uuid4())

    assert can_hr_view_student_contacts(foreign_hr, application, vacancy) is False


def test_admin_is_not_treated_as_hr_contact_viewer_by_accident() -> None:
    _, _, _, vacancy, application = build_application(status=ApplicationStatus.ACCEPTED)
    admin_user = build_hr_user(role=UserRole.ADMIN)

    assert can_hr_view_student_contacts(admin_user, application, vacancy) is False


def test_student_vacancy_serializer_never_returns_hr_contacts() -> None:
    _, _, company, vacancy, _ = build_application(status=ApplicationStatus.ACCEPTED)

    payload = serialize_vacancy_for_student(vacancy)

    assert payload["company_name"] == company.name
    assert "contact_phone" not in payload
    assert "contact_email" not in payload
    assert "contact_telegram" not in payload
    assert "hr_phone" not in payload
    assert "hr_email" not in payload
    assert "hr_telegram" not in payload


def test_student_application_serializer_never_returns_hr_contacts() -> None:
    _, _, _, _, application = build_application(status=ApplicationStatus.ACCEPTED)

    payload = serialize_application_for_student(application)

    assert payload["status"] == ApplicationStatus.ACCEPTED.value
    assert "contacts" not in payload
    assert "hr_phone" not in payload
    assert "hr_email" not in payload
    assert "hr_telegram" not in payload


def test_hr_application_serializer_hides_student_contacts_before_acceptance() -> None:
    hr_user, _, _, _, application = build_application(status=ApplicationStatus.SENT)

    payload = serialize_application_for_hr(application, hr_user)

    assert payload["contacts"] is None
    assert payload["student"]["first_name"] == "Ivan"
    assert "phone" not in payload["student"]
    assert "email" not in payload["student"]
    assert "telegram_username" not in payload["student"]


def test_hr_application_serializer_returns_student_contacts_after_acceptance() -> None:
    hr_user, student_user, _, _, application = build_application(status=ApplicationStatus.ACCEPTED)

    payload = serialize_application_for_hr(application, hr_user)

    assert payload["contacts"] == {
        "phone": student_user.phone,
        "email": student_user.email,
        "telegram_username": student_user.username,
    }
