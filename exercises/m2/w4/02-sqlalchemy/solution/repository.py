"""Reference solution."""

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError

from models import Application, Company, db


class DuplicateApplication(Exception):
    pass


def get_for_user(application_id: int, user_id: int) -> Application | None:
    return db.session.scalars(
        select(Application).where(Application.id == application_id, Application.user_id == user_id)
    ).one_or_none()


def list_applications(
    user_id: int, statuses: list[str] | None = None, page: int = 1, per_page: int = 20
) -> tuple[list[Application], int]:
    stmt = select(Application).where(Application.user_id == user_id)
    if statuses:
        stmt = stmt.where(Application.status.in_(statuses))

    total = db.session.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    items = db.session.scalars(
        stmt.order_by(Application.created_at.desc(), Application.id.desc())
        .limit(per_page)
        .offset((page - 1) * per_page)
    ).all()
    return list(items), total


def count_by_status(user_id: int) -> dict[str, int]:
    rows = db.session.execute(
        select(Application.status, func.count()).where(Application.user_id == user_id).group_by(Application.status)
    ).all()
    return {status: count for status, count in rows}


def create_application_with_company(user_id: int, company_name: str, role_title: str) -> Application:
    try:
        company = db.session.scalars(
            select(Company).where(func.lower(Company.name) == company_name.strip().lower())
        ).one_or_none()
        if company is None:
            company = Company(name=company_name.strip())
            db.session.add(company)
            db.session.flush()  # company.id is generated, still uncommitted

        application = Application(user_id=user_id, company_id=company.id, role_title=role_title)
        db.session.add(application)
        db.session.commit()  # one commit for the whole unit of work
        return application
    except IntegrityError as error:
        db.session.rollback()  # discard the new company too, and make the session usable again
        raise DuplicateApplication(f"{company_name} / {role_title}") from error
