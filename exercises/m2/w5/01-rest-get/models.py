"""Provided model."""

from datetime import date

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import BigInteger, Index, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)


class Job(db.Model):
    __tablename__ = "jobs"
    __table_args__ = (Index("ix_jobs_posted_id", "posted_on", "id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    company: Mapped[str] = mapped_column(String(200))
    city: Mapped[str | None] = mapped_column(String(100))
    remote: Mapped[bool]
    salary_max: Mapped[int | None] = mapped_column(BigInteger)
    posted_on: Mapped[date]
