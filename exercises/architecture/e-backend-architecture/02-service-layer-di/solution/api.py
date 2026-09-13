"""Thin HTTP adapter — reference solution: parse request → call a use case → shape the response."""

from flask import Flask, jsonify, request

from domain import InvalidTransition
from services import ApplicationNotFound, LimitReached, ValidationFailed


def create_app(container) -> Flask:
    app = Flask(__name__)
    service = container.applications

    @app.post("/users/<int:user_id>/applications")
    def add(user_id: int):
        body = request.get_json(silent=True) or {}
        dto = service.add_application(user_id, body.get("plan", "free"), body.get("company", ""), body.get("role", ""))
        return jsonify(dto), 201

    @app.post("/users/<int:user_id>/applications/<int:application_id>/status")
    def move(user_id: int, application_id: int):
        body = request.get_json(silent=True) or {}
        return jsonify(service.move(user_id, application_id, body.get("status", "")))

    @app.get("/users/<int:user_id>/applications")
    def list_all(user_id: int):
        return jsonify({"data": service.list_applications(user_id)})

    def error(code: str, status: int, **extra):
        return jsonify({"error": {"code": code, **extra}}), status

    app.register_error_handler(ValidationFailed, lambda e: error("validation_failed", 422, field=e.field))
    app.register_error_handler(LimitReached, lambda e: error("limit_reached", 403))
    app.register_error_handler(ApplicationNotFound, lambda e: error("not_found", 404))
    app.register_error_handler(InvalidTransition, lambda e: error("invalid_transition", 409))
    return app
