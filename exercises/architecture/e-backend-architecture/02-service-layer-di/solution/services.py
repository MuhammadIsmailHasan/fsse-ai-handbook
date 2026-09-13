"""Use cases — reference solution. Depends only on the domain and on ports (protocols)."""

from domain import Application
from ports import Clock, EventPublisher, UnitOfWork


class ValidationFailed(Exception):
    def __init__(self, field: str):
        super().__init__(f"{field} is required")
        self.field = field


class LimitReached(Exception):
    pass


class ApplicationNotFound(Exception):
    pass


def to_dto(application: Application) -> dict:
    return {
        "id": application.id,
        "company": application.company,
        "role": application.role,
        "status": application.status,
        "updated_at": application.updated_at.isoformat(),
    }


class ApplicationService:
    def __init__(self, uow: UnitOfWork, publisher: EventPublisher, clock: Clock, max_active_free: int = 3):
        self.uow, self.publisher, self.clock, self.max_active_free = uow, publisher, clock, max_active_free

    def add_application(self, user_id: int, plan: str, company: str, role: str) -> dict:
        company, role = (company or "").strip(), (role or "").strip()
        if not company:
            raise ValidationFailed("company")
        if not role:
            raise ValidationFailed("role")
        with self.uow:
            active = [a for a in self.uow.applications.list_for_user(user_id) if a.is_active]
            if plan == "free" and len(active) >= self.max_active_free:
                raise LimitReached()
            now = self.clock()
            application = Application(user_id=user_id, company=company, role=role, created_at=now, updated_at=now)
            self.uow.applications.add(application)
            self.uow.commit()
            dto = to_dto(application)
        self.publisher.publish("application_added", {"application_id": application.id, "user_id": user_id})
        return dto

    def move(self, user_id: int, application_id: int, new_status: str) -> dict:
        with self.uow:
            application = self.uow.applications.get(application_id)
            if application is None or application.user_id != user_id:
                raise ApplicationNotFound()
            previous = application.status
            application.move_to(new_status)
            application.updated_at = self.clock()
            self.uow.commit()
            dto = to_dto(application)
        self.publisher.publish(
            "application_status_changed",
            {"application_id": application_id, "user_id": user_id, "from": previous, "to": new_status},
        )
        return dto

    def list_applications(self, user_id: int) -> list[dict]:
        with self.uow:
            return [to_dto(a) for a in self.uow.applications.list_for_user(user_id)]
