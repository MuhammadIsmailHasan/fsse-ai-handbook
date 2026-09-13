"""Composition root — reference solution. The one place that knows concrete adapters."""

from dataclasses import dataclass

import adapters
from ports import Clock, EventPublisher, UnitOfWork
from services import ApplicationService


@dataclass
class Container:
    applications: ApplicationService


def bootstrap(
    uow: UnitOfWork | None = None,
    publisher: EventPublisher | None = None,
    clock: Clock | None = None,
    max_active_free: int = 3,
) -> Container:
    return Container(
        applications=ApplicationService(
            uow=uow or adapters.InMemoryUnitOfWork(),
            publisher=publisher or adapters.LoggingPublisher(),
            clock=clock or adapters.system_clock,
            max_active_free=max_active_free,
        )
    )
