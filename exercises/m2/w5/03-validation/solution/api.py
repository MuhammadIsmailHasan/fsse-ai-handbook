"""Reference solution."""

from flask import Flask, request
from marshmallow import ValidationError

from schemas import ApplicationCreateSchema, ApplicationResponseSchema, flatten_errors


def create_app() -> Flask:
    app = Flask(__name__)

    @app.post("/applications")
    def create_application():
        payload = request.get_json(silent=True)
        if not isinstance(payload, dict):
            return {"error": {"code": "invalid_json", "message": "Body must be a JSON object"}}, 400
        try:
            data = ApplicationCreateSchema().load(payload)
        except ValidationError as error:
            return {
                "error": {
                    "code": "validation_failed",
                    "message": "Some fields are invalid",
                    "fields": flatten_errors(error.messages),
                }
            }, 422
        stored = {**data, "id": 1, "user_id": 7, "private_notes": "secret"}  # pretend the service saved it
        return {"data": ApplicationResponseSchema().dump(stored)}, 201

    return app
