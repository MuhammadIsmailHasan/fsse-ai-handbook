"""Provided: the repository — the ONLY layer that talks to SQLAlchemy."""

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from .errors import DuplicateApplication
from .models import Application, db


class SqlApplicationRepository:
    def get_for_user(self, application_id: int, user_id: int) -> Application | None:
        return db.session.scalars(
            select(Application).where(Application.id == application_id, Application.user_id == user_id)
        ).one_or_none()

    def list_for_user(self, user_id: int) -> list[Application]:
        return list(
            db.session.scalars(
                select(Application).where(Application.user_id == user_id).order_by(Application.id.desc())
            )
        )

    def add(self, application: Application) -> None:
        db.session.add(application)

    def commit(self) -> None:
        try:
            db.session.commit()
        except IntegrityError as error:
            db.session.rollback()
            raise DuplicateApplication("you already applied for this role at this company") from error
