from enum import Enum


class StrEnum(str, Enum):
    """String enum base for stable DB and serializer values."""


class UserRole(StrEnum):
    STUDENT = "student"
    HR = "hr"
    ADMIN = "admin"
    MODERATOR = "moderator"
    SUPPORT = "support"


class HRStatus(StrEnum):
    PENDING = "pending"
    ACTIVE = "active"
    BLOCKED = "blocked"


class VacancyStatus(StrEnum):
    DRAFT = "draft"
    AWAITING_PAYMENT = "awaiting_payment"
    MODERATION = "moderation"
    MANUAL_REVIEW = "manual_review"
    ACTIVE = "active"
    REJECTED = "rejected"
    ARCHIVED = "archived"
    EXPIRED = "expired"


class ApplicationStatus(StrEnum):
    SENT = "sent"
    VIEWED = "viewed"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    COMPLAINT = "complaint"
    CLOSED = "closed"


class PaymentStatus(StrEnum):
    PENDING = "pending"
    SUCCEEDED = "succeeded"
    CANCELED = "canceled"
    FAILED = "failed"
    REFUNDED = "refunded"


class SubscriptionStatus(StrEnum):
    ACTIVE = "active"
    EXPIRED = "expired"
    CANCELED = "canceled"


class ComplaintStatus(StrEnum):
    OPEN = "open"
    IN_REVIEW = "in_review"
    RESOLVED = "resolved"
    REJECTED = "rejected"


class SupportTicketStatus(StrEnum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"


class ModerationResult(StrEnum):
    APPROVED = "approved"
    MANUAL_REVIEW = "manual_review"
    REJECTED = "rejected"
