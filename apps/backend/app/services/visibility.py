from app.core.enums import ApplicationStatus, UserRole
from app.models import Application, User, Vacancy


def can_hr_view_student_contacts(hr_user: User, application: Application, vacancy: Vacancy) -> bool:
    hr_profile = hr_user.hr_profile
    if hr_user.role is not UserRole.HR or hr_profile is None:
        return False
    if application.status is not ApplicationStatus.ACCEPTED:
        return False
    if application.hr_user_id != hr_user.id:
        return False
    if application.vacancy_id != vacancy.id:
        return False
    if vacancy.hr_user_id != hr_user.id:
        return False
    if vacancy.company_id != hr_profile.company_id:
        return False
    return True


def serialize_vacancy_for_student(vacancy: Vacancy) -> dict:
    return {
        "id": str(vacancy.id),
        "title": vacancy.title,
        "company_name": vacancy.company.name if vacancy.company else None,
        "category": vacancy.category,
        "job_type": vacancy.job_type,
        "schedule": vacancy.schedule,
        "salary_text": vacancy.salary_text,
        "district": vacancy.district,
        "address": vacancy.address,
        "format": vacancy.format,
        "description": vacancy.description,
        "requirements": vacancy.requirements,
        "conditions": vacancy.conditions,
        "is_promoted": vacancy.is_promoted,
        "published_at": vacancy.published_at.isoformat() if vacancy.published_at else None,
    }


def serialize_application_for_student(application: Application) -> dict:
    vacancy = application.vacancy
    return {
        "id": str(application.id),
        "vacancy_id": str(application.vacancy_id),
        "vacancy_title": vacancy.title if vacancy else None,
        "company_name": vacancy.company.name if vacancy and vacancy.company else None,
        "status": application.status.value,
        "created_at": application.created_at.isoformat() if application.created_at else None,
    }


def serialize_application_for_hr(application: Application, hr_user: User) -> dict:
    student = application.student_user
    profile = student.student_profile if student else None
    vacancy = application.vacancy
    contacts = None
    if can_hr_view_student_contacts(hr_user, application, vacancy):
        contacts = {
            "phone": student.phone,
            "email": student.email,
            "telegram_username": student.username,
        }
    return {
        "id": str(application.id),
        "vacancy_id": str(application.vacancy_id),
        "vacancy_title": vacancy.title if vacancy else None,
        "status": application.status.value,
        "student": {
            "first_name": student.first_name if student else None,
            "university": profile.university if profile else None,
            "course": profile.course if profile else None,
            "speciality": profile.speciality if profile else None,
            "preferred_schedule": profile.preferred_schedule if profile else None,
            "experience_text": profile.experience_text if profile else None,
            "student_comment": application.student_comment,
        },
        "contacts": contacts,
        "created_at": application.created_at.isoformat() if application.created_at else None,
    }
