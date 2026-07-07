from __future__ import annotations

from datetime import UTC, datetime, timedelta
from pathlib import Path
import sys

from sqlalchemy import select

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.core.enums import ApplicationStatus, HRStatus, SubscriptionStatus, UserRole, VacancyStatus
from app.core.config import get_settings
from app.db.session import get_session_factory
from app.models import (
    Application,
    Company,
    HRProfile,
    StudentProfile,
    Subscription,
    Tariff,
    User,
    Vacancy,
)


VACANCY_SEEDS = [
    {
        "title": "Waiter evening shift",
        "category": "restaurant",
        "job_type": "shift",
        "schedule": "evening",
        "salary_text": "2500 RUB/shift",
        "district": "center",
        "requirements": "Polite communication",
        "conditions": "Flexible shifts",
    },
    {
        "title": "Barista trainee",
        "category": "cafe",
        "job_type": "part_time",
        "schedule": "morning",
        "salary_text": "2200 RUB/shift",
        "district": "volga",
        "requirements": "Fast learner",
        "conditions": "Training provided",
    },
    {
        "title": "Weekend promoter",
        "category": "marketing",
        "job_type": "weekend",
        "schedule": "weekend",
        "salary_text": "1800 RUB/day",
        "district": "center",
        "requirements": "Confident speech",
        "conditions": "Short shifts",
    },
    {
        "title": "Evening courier",
        "category": "delivery",
        "job_type": "shift",
        "schedule": "evening",
        "salary_text": "2800 RUB/shift",
        "district": "leninsky",
        "requirements": "Punctuality",
        "conditions": "Meal compensation",
    },
    {
        "title": "Quest room administrator",
        "category": "entertainment",
        "job_type": "part_time",
        "schedule": "flex",
        "salary_text": "2400 RUB/shift",
        "district": "center",
        "requirements": "Customer care",
        "conditions": "Creative team",
    },
    {
        "title": "Call center operator",
        "category": "support",
        "job_type": "part_time",
        "schedule": "day",
        "salary_text": "2300 RUB/shift",
        "district": "kirovsky",
        "requirements": "Clear speech",
        "conditions": "Hybrid after training",
    },
    {
        "title": "Warehouse assistant",
        "category": "logistics",
        "job_type": "shift",
        "schedule": "day",
        "salary_text": "2600 RUB/shift",
        "district": "zavodskoy",
        "requirements": "Physical stamina",
        "conditions": "Uniform provided",
    },
    {
        "title": "Sales intern",
        "category": "sales",
        "job_type": "internship",
        "schedule": "flex",
        "salary_text": "20000 RUB/month",
        "district": "center",
        "requirements": "Interest in sales",
        "conditions": "Mentorship",
    },
    {
        "title": "Event animator",
        "category": "events",
        "job_type": "project",
        "schedule": "weekend",
        "salary_text": "3000 RUB/event",
        "district": "oktyabrsky",
        "requirements": "Energy and teamwork",
        "conditions": "Project-based work",
    },
    {
        "title": "Retail consultant",
        "category": "retail",
        "job_type": "shift",
        "schedule": "day",
        "salary_text": "2500 RUB/shift",
        "district": "frunzensky",
        "requirements": "Friendly attitude",
        "conditions": "Bonus program",
    },
]


def get_or_create_user(session, *, telegram_id: int, role: UserRole, username: str, first_name: str, last_name: str, phone: str | None, email: str | None) -> User:
    user = session.scalar(select(User).where(User.telegram_id == telegram_id))
    if user is None:
        user = User(
            telegram_id=telegram_id,
            role=role,
            username=username,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            email=email,
        )
        session.add(user)
        session.flush()
    return user


def get_or_create_company(session, *, name: str, inn: str, description: str) -> Company:
    company = session.scalar(select(Company).where(Company.name == name))
    if company is None:
        company = Company(
            name=name,
            inn=inn,
            description=description,
            status="active",
            contact_name="Hidden HR Contact",
            contact_phone="+79990002222",
            contact_email=f"{name.lower().replace(' ', '_')}@example.com",
            contact_telegram=f"{name.lower().replace(' ', '_')}_hr",
        )
        session.add(company)
        session.flush()
    return company


def ensure_hr_profile(session, *, user: User, company: Company, position: str) -> HRProfile:
    if user.hr_profile is None:
        profile = HRProfile(
            user=user,
            company=company,
            position=position,
            verified_status=HRStatus.ACTIVE,
        )
        session.add(profile)
        user.hr_profile = profile
        session.flush()
    return user.hr_profile


def ensure_student_profile(session, *, user: User, university: str, course: int, speciality: str, experience_text: str, muted: bool = False) -> StudentProfile:
    if user.student_profile is None:
        profile = StudentProfile(
            user=user,
            university=university,
            course=course,
            speciality=speciality,
            preferred_job_types=["shift", "part_time"],
            preferred_schedule=["evening", "weekend"],
            preferred_districts=["center"],
            experience_text=experience_text,
            profile_completed=True,
        )
        session.add(profile)
        user.student_profile = profile
    if muted:
        user.mute_until = datetime.now(UTC) + timedelta(days=1)
    session.flush()
    return user.student_profile


def ensure_subscription(session, *, user: User, active: bool) -> Subscription | None:
    existing = session.scalar(select(Subscription).where(Subscription.user_id == user.id))
    if not active:
        return existing
    if existing is None:
        now = datetime.now(UTC)
        existing = Subscription(
            user=user,
            starts_at=now,
            expires_at=now + timedelta(days=30),
            status=SubscriptionStatus.ACTIVE,
        )
        session.add(existing)
        session.flush()
    return existing


def ensure_tariff(session) -> Tariff:
    tariff = session.scalar(select(Tariff).where(Tariff.code == "student_monthly_access"))
    if tariff is None:
        tariff = Tariff(
            code="student_monthly_access",
            title="Student Monthly Access",
            amount=get_settings().student_monthly_tariff_rub,
            duration_days=30,
            is_active=True,
        )
        session.add(tariff)
        session.flush()
    return tariff


def ensure_vacancies(session, *, companies: list[Company], hr_users: list[User]) -> list[Vacancy]:
    existing = session.scalars(select(Vacancy).order_by(Vacancy.created_at)).all()
    if len(existing) >= len(VACANCY_SEEDS):
        return existing

    vacancies: list[Vacancy] = []
    for index, seed in enumerate(VACANCY_SEEDS):
        company = companies[index % len(companies)]
        hr_user = hr_users[index % len(hr_users)]
        vacancy = Vacancy(
            company=company,
            hr_user=hr_user,
            title=seed["title"],
            category=seed["category"],
            job_type=seed["job_type"],
            schedule=seed["schedule"],
            salary_text=seed["salary_text"],
            district=seed["district"],
            address="Public campus-friendly location",
            format="offline",
            description=f"{seed['title']} for students",
            responsibilities=seed["requirements"],
            requirements=seed["requirements"],
            conditions=seed["conditions"],
            experience_required=False,
            status=VacancyStatus.ACTIVE,
            moderation_status="approved",
            is_promoted=False,
            published_at=datetime.now(UTC),
        )
        session.add(vacancy)
        vacancies.append(vacancy)

    session.flush()
    return vacancies


def ensure_applications(session, *, vacancies: list[Vacancy], students: list[User], hr_users: list[User]) -> None:
    if session.scalar(select(Application.id).limit(1)) is not None:
        return

    sent_application = Application(
        vacancy=vacancies[0],
        student_user=students[0],
        hr_user=hr_users[0],
        status=ApplicationStatus.SENT,
        student_comment="Available on weekdays",
    )
    accepted_application = Application(
        vacancy=vacancies[1],
        student_user=students[0],
        hr_user=hr_users[1],
        status=ApplicationStatus.ACCEPTED,
        student_comment="Can start immediately",
        accepted_at=datetime.now(UTC),
    )
    rejected_application = Application(
        vacancy=vacancies[2],
        student_user=students[1],
        hr_user=hr_users[2],
        status=ApplicationStatus.REJECTED,
        student_comment="Interested in weekend shifts",
        rejected_at=datetime.now(UTC),
    )
    session.add_all([sent_application, accepted_application, rejected_application])
    session.flush()


def main() -> None:
    settings = get_settings()
    admin_ids = settings.admin_telegram_ids or [900001]
    SessionLocal = get_session_factory()
    with SessionLocal() as session:
        admin_user = get_or_create_user(
            session,
            telegram_id=admin_ids[0],
            role=UserRole.ADMIN,
            username="admin_user",
            first_name="Admin",
            last_name="User",
            phone="+79990009999",
            email="admin@example.com",
        )

        company_specs = [
            ("Verhoff", "6450000001", "Restaurant jobs for students"),
            ("Coffee Point", "6450000002", "Cafe and barista shifts"),
            ("Quest Room", "6450000003", "Entertainment and quest jobs"),
        ]
        companies = [get_or_create_company(session, name=name, inn=inn, description=description) for name, inn, description in company_specs]

        hr_users = [
            get_or_create_user(
                session,
                telegram_id=1001 + index,
                role=UserRole.HR,
                username=username,
                first_name=first_name,
                last_name="HR",
                phone=f"+7999000111{index}",
                email=f"{username}@example.com",
            )
            for index, (username, first_name) in enumerate(
                [
                    ("verhoff_hr", "Verhoff"),
                    ("coffee_hr", "Coffee"),
                    ("quest_hr", "Quest"),
                ]
            )
        ]

        for hr_user, company, position in zip(hr_users, companies, ["Recruiter", "Manager", "Coordinator"], strict=True):
            ensure_hr_profile(session, user=hr_user, company=company, position=position)

        student_users = [
            get_or_create_user(
                session,
                telegram_id=2001,
                role=UserRole.STUDENT,
                username="active_student",
                first_name="Active",
                last_name="Student",
                phone="+79990000001",
                email="active.student@example.com",
            ),
            get_or_create_user(
                session,
                telegram_id=2002,
                role=UserRole.STUDENT,
                username="inactive_student",
                first_name="Inactive",
                last_name="Student",
                phone="+79990000002",
                email="inactive.student@example.com",
            ),
            get_or_create_user(
                session,
                telegram_id=2003,
                role=UserRole.STUDENT,
                username="muted_student",
                first_name="Muted",
                last_name="Student",
                phone="+79990000003",
                email="muted.student@example.com",
            ),
        ]

        ensure_student_profile(
            session,
            user=student_users[0],
            university="SGTU",
            course=2,
            speciality="Computer Science",
            experience_text="Worked two months as a waiter",
        )
        ensure_student_profile(
            session,
            user=student_users[1],
            university="SSU",
            course=3,
            speciality="Marketing",
            experience_text="No formal experience yet",
        )
        ensure_student_profile(
            session,
            user=student_users[2],
            university="SEU",
            course=1,
            speciality="Management",
            experience_text="Volunteer event helper",
            muted=True,
        )

        ensure_subscription(session, user=student_users[0], active=True)
        ensure_subscription(session, user=student_users[1], active=False)
        ensure_subscription(session, user=student_users[2], active=False)
        ensure_tariff(session)
        vacancies = ensure_vacancies(session, companies=companies, hr_users=hr_users)
        ensure_applications(session, vacancies=vacancies, students=student_users, hr_users=hr_users)

        session.commit()
        print(
            "Seed data ready:",
            {
                "admin_user_id": str(admin_user.id),
                "companies": len(companies),
                "hr_users": len(hr_users),
                "students": len(student_users),
                "vacancies": len(vacancies),
            },
        )


if __name__ == "__main__":
    main()
