"""M2 · W4 · 03 — Typed SQLAlchemy 2.0 models."""

import enum  # noqa: F401
from datetime import datetime  # noqa: F401

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData  # noqa: F401
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column  # noqa: F401


class Base(DeclarativeBase):
    pass  # YOUR CODE HERE: add a MetaData with the naming convention


db = SQLAlchemy(model_class=Base)


# YOUR CODE HERE: ApplicationStatus, User, Company, Application
