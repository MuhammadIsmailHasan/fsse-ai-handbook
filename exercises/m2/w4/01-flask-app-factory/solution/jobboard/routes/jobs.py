"""Jobs blueprint: thin route functions over an in-memory store."""

from flask import Blueprint, current_app, request

from ..errors import error_body

jobs_bp = Blueprint("jobs", __name__, url_prefix="/api/v1/jobs")

BOOLEAN_TEXT = {"true": True, "false": False}


def store() -> list[dict]:
    return current_app.extensions["jobs_store"]


@jobs_bp.get("")
def list_jobs():
    jobs = store()
    city = request.args.get("city")
    remote_text = request.args.get("remote")

    if city:
        jobs = [job for job in jobs if (job["city"] or "").lower() == city.lower()]
    if remote_text is not None:
        if remote_text.lower() not in BOOLEAN_TEXT:
            return error_body("invalid_filter", "remote must be true or false"), 422
        remote = BOOLEAN_TEXT[remote_text.lower()]
        jobs = [job for job in jobs if job["remote"] is remote]

    return {"data": jobs, "meta": {"total": len(jobs)}}


@jobs_bp.get("/<int:job_id>")
def get_job(job_id: int):
    job = next((job for job in store() if job["id"] == job_id), None)
    if job is None:
        return error_body("job_not_found", f"Job {job_id} not found"), 404
    return {"data": job}


def validate_job(data: dict) -> tuple[dict, dict[str, str]]:
    errors: dict[str, str] = {}
    cleaned: dict = {}  # keys are added in the response's field order: title, company, city, remote
    for field in ("title", "company"):
        value = data.get(field)
        if not isinstance(value, str) or not value.strip():
            errors[field] = "required"
        else:
            cleaned[field] = value.strip()
    city = data.get("city")
    cleaned["city"] = city.strip() if isinstance(city, str) and city.strip() else None
    remote = data.get("remote", False)
    if not isinstance(remote, bool):
        errors["remote"] = "must be a boolean"
    cleaned["remote"] = remote
    return cleaned, errors


@jobs_bp.post("")
def create_job():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return error_body("invalid_json", "Body must be a JSON object"), 400

    cleaned, errors = validate_job(data)
    if errors:
        body = error_body("validation_failed", "Invalid job data")
        body["error"]["fields"] = errors
        return body, 422

    jobs = store()
    job = {"id": max((j["id"] for j in jobs), default=0) + 1, **cleaned}
    jobs.append(job)
    return {"data": job}, 201, {"Location": f"/api/v1/jobs/{job['id']}"}
