"""M2 · W4 · 06 — YOUR business layer. No Flask, no SQLAlchemy imports here."""

from collections.abc import Callable  # noqa: F401
from datetime import datetime  # noqa: F401

from .errors import ApplicationNotFound, InvalidTransition, ValidationFailed  # noqa: F401
from .models import Application  # noqa: F401


class ApplicationService:
    # YOUR CODE HERE
    pass
