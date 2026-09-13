"""Provided models."""

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey, Index, String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)


class Company(db.Model):
    __tablename__ = "companies"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    website: Mapped[str | None] = mapped_column(String(500))

    __table_args__ = (Index("ix_companies_name_lower", func.lower(name), unique=True),)


class Job(db.Model):
    __tablename__ = "jobs"
    id: Mapped[int] = mapped_column(primary_key=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id", ondelete="RESTRICT"), index=True)
    title: Mapped[str] = mapped_column(String(200))
