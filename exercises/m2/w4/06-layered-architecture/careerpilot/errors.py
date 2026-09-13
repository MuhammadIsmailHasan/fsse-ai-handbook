"""Provided: domain errors. Services raise these; the app factory maps them to HTTP."""


class AppError(Exception):
    status_code = 500
    code = "internal_error"


class ValidationFailed(AppError):
    status_code = 422
    code = "validation_failed"

    def __init__(self, fields: dict[str, str]):
        super().__init__("validation failed")
        self.fields = fields


class ApplicationNotFound(AppError):
    status_code = 404
    code = "application_not_found"

    def __init__(self, application_id: int):
        super().__init__(f"application {application_id} not found")


class DuplicateApplication(AppError):
    status_code = 409
    code = "duplicate_application"


class InvalidTransition(AppError):
    status_code = 409
    code = "invalid_transition"
