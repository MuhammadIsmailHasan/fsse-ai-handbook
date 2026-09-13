"""Provided models (you'll write models yourself in lesson 03)."""

from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey, Index, String, UniqueConstraint, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)


class Company(db.Model):
    __tablename__ = "companies"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200))

    __table_args__ = (Index("companies_name_lower_key", func.lower(name), unique=True),)


class Application(db.Model):
    __tablename__ = "applications"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(index=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), index=True)
    role_title: Mapped[str] = mapped_column(String(200))
    status: Mapped[str] = mapped_column(String(30), default="applied")
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    __table_args__ = (UniqueConstraint("user_id", "company_id", "role_title", name="applications_unique_role"),)
