"""Reference solution."""

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import joinedload, selectinload

from models import Application, db


def dashboard(user_id: int, now: datetime) -> list[dict]:
    stmt = (
        select(Application)
        .where(Application.user_id == user_id)
        .options(
            joinedload(Application.company),        # many-to-one → JOIN in the main query
            selectinload(Application.skills),        # collection → 1 extra IN query
            selectinload(Application.interviews),    # collection → 1 extra IN query
        )
        .order_by(Application.created_at.desc(), Application.id.desc())
    )
    applications = db.session.scalars(stmt).unique().all()   # 3 statements, all loading done here

    rows = []
    for application in applications:                          # no queries in this loop
        upcoming = [i.starts_at for i in application.interviews if i.starts_at >= now]
        rows.append(
            {
                "id": application.id,
                "role_title": application.role_title,
                "company": application.company.name,
                "skills": sorted(skill.name for skill in application.skills),
                "next_interview": min(upcoming).isoformat() if upcoming else None,
            }
        )
    return rows
