"""Reference solution."""

import enum
from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import BigInteger, CheckConstraint, DateTime, Enum, ForeignKey, Index, MetaData, String, UniqueConstraint, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=NAMING_CONVENTION)


db = SQLAlchemy(model_class=Base)


class ApplicationStatus(enum.StrEnum):
    WISHLIST = "wishlist"
    APPLIED = "applied"
    INTERVIEW = "interview"
    OFFER = "offer"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"


def timestamp_column(**kwargs) -> Mapped[datetime]:
    return mapped_column(DateTime(timezone=True), server_default=func.now(), **kwargs)


class User(db.Model):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(320))
    full_name: Mapped[str] = mapped_column(String(200))
    created_at: Mapped[datetime] = timestamp_column()

    __table_args__ = (Index("ix_users_email_lower", func.lower(email), unique=True),)

    def __repr__(self) -> str:
        return f"<User id={self.id} {self.email!r}>"


class Company(db.Model):
    __tablename__ = "companies"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), unique=True)
    website: Mapped[str | None] = mapped_column(String(500))
    created_at: Mapped[datetime] = timestamp_column()


class Application(db.Model):
    __tablename__ = "applications"
    __table_args__ = (
        CheckConstraint("length(trim(role_title)) > 0", name="role_title_not_blank"),
        CheckConstraint("salary_expectation >= 0", name="salary_non_negative"),
        UniqueConstraint("user_id", "company_id", "role_title", name="uq_applications_user_company_role"),
        Index("ix_applications_user_created", "user_id", "created_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id", ondelete="RESTRICT"))
    role_title: Mapped[str] = mapped_column(String(200))
    status: Mapped[ApplicationStatus] = mapped_column(
        Enum(
            ApplicationStatus,
            native_enum=False,
            create_constraint=True,  # without this, SQLAlchemy 2.x does NOT add the CHECK constraint
            length=30,
            values_callable=lambda members: [member.value for member in members],
            name="application_status",
        ),
        default=ApplicationStatus.APPLIED,
        server_default=ApplicationStatus.APPLIED.value,
    )
    salary_expectation: Mapped[int | None] = mapped_column(BigInteger)
    created_at: Mapped[datetime] = timestamp_column()
    updated_at: Mapped[datetime] = timestamp_column(onupdate=func.now())

    ACTIVE_STATUSES = frozenset({ApplicationStatus.APPLIED, ApplicationStatus.INTERVIEW})

    @property
    def is_active(self) -> bool:
        return self.status in self.ACTIVE_STATUSES

    def __repr__(self) -> str:
        return f"<Application id={self.id} {self.role_title!r} status={self.status}>"
