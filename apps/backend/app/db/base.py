from app.db.base_class import Base
from app.models import (  # noqa: F401
    Application,
    BalanceTransaction,
    Company,
    Complaint,
    Event,
    GuestVacancyView,
    HRProfile,
    ModerationLog,
    Payment,
    Referral,
    StudentProfile,
    Subscription,
    SupportTicket,
    Tariff,
    User,
    Vacancy,
    VacancyView,
)

metadata = Base.metadata
