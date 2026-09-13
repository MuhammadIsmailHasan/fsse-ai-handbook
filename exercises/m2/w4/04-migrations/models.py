"""The TARGET model after your migration (for reference and autogenerate)."""

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import BigInteger, CheckConstraint, MetaData, String
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


class Application(db.Model):
    __tablename__ = "applications"
    __table_args__ = (CheckConstraint("salary_min <= salary_max", name="salary_range_valid"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    company_name: Mapped[str] = mapped_column(String(200))
    role_title: Mapped[str] = mapped_column(String(200))
    status: Mapped[str] = mapped_column(String(30), server_default="applied")
    salary_min: Mapped[int | None] = mapped_column(BigInteger)
    salary_max: Mapped[int | None] = mapped_column(BigInteger)
