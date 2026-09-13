"""Reference solution."""

import base64
import binascii
import json
import math
from datetime import date
from urllib.parse import urlencode

from flask import Blueprint, request
from sqlalchemy import func, select, tuple_

from app import ApiError
from models import Job, db

jobs_bp = Blueprint("jobs", __name__, url_prefix="/api/v1/jobs")

SORTABLE = {"posted_on": Job.posted_on, "salary_max": Job.salary_max, "title": Job.title}
LIST_PARAMS = {"city", "remote", "min_salary", "sort", "page", "per_page"}
FEED_PARAMS = {"limit", "cursor"}


def serialize(job: Job) -> dict:
    return {
        "id": job.id,
        "title": job.title,
        "company": job.company,
        "city": job.city,
        "remote": job.remote,
        "salary_max": job.salary_max,
        "posted_on": job.posted_on.isoformat(),
    }


def int_param(name: str, default: int, minimum: int, maximum: int | None, errors: dict) -> int:
    raw = request.args.get(name)
    if raw is None:
        return default
    if not raw.lstrip("-").isdigit():
        errors[name] = "must be an integer"
        return default
    value = int(raw)
    if value < minimum or (maximum is not None and value > maximum):
        errors[name] = f"must be between {minimum} and {maximum}" if maximum else f"must be >= {minimum}"
    return value


def reject_unknown(allowed: set[str], errors: dict) -> None:
    for name in request.args:
        if name not in allowed:
            errors[name] = "unknown parameter"


def raise_if(errors: dict) -> None:
    if errors:
        raise ApiError(422, "invalid_query", "Invalid query parameters", errors)


def order_clauses(sort: str, errors: dict) -> list:
    clauses, last_desc = [], True
    for part in sort.split(","):
        descending = part.startswith("-")
        column = SORTABLE.get(part.removeprefix("-"))
        if column is None:
            errors["sort"] = f"unknown sort field {part!r}"
            return []
        clauses.append((column.desc() if descending else column.asc()).nulls_last())
        last_desc = descending
    clauses.append(Job.id.desc() if last_desc else Job.id.asc())  # unique tie-breaker
    return clauses


@jobs_bp.get("")
def list_jobs():
    errors: dict[str, str] = {}
    reject_unknown(LIST_PARAMS, errors)

    stmt = select(Job)
    if city := request.args.get("city"):
        stmt = stmt.where(func.lower(Job.city) == city.lower())
    if (remote := request.args.get("remote")) is not None:
        if remote not in ("true", "false"):
            errors["remote"] = "must be true or false"
        else:
            stmt = stmt.where(Job.remote.is_(remote == "true"))
    if "min_salary" in request.args:
        min_salary = int_param("min_salary", 0, 0, None, errors)
        stmt = stmt.where(Job.salary_max >= min_salary)

    clauses = order_clauses(request.args.get("sort", "-posted_on"), errors)
    page = int_param("page", 1, 1, None, errors)
    per_page = int_param("per_page", 20, 1, 100, errors)
    raise_if(errors)

    total = db.session.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    jobs = db.session.scalars(stmt.order_by(*clauses).limit(per_page).offset((page - 1) * per_page)).all()
    total_pages = math.ceil(total / per_page) if total else 0

    def link(target_page: int) -> str:
        params = [(k, v) for k, v in request.args.items(multi=True) if k not in ("page", "per_page")]
        params += [("page", target_page), ("per_page", per_page)]
        return f"{request.path}?{urlencode(params)}"

    return {
        "data": [serialize(job) for job in jobs],
        "meta": {"page": page, "per_page": per_page, "total": total, "total_pages": total_pages},
        "links": {
            "self": link(page),
            "next": link(page + 1) if page < total_pages else None,
            "prev": link(page - 1) if page > 1 else None,
        },
    }


def encode_cursor(job: Job) -> str:
    raw = json.dumps({"p": job.posted_on.isoformat(), "i": job.id}).encode()
    return base64.urlsafe_b64encode(raw).decode().rstrip("=")


def decode_cursor(cursor: str) -> tuple[date, int]:
    try:
        padded = cursor + "=" * (-len(cursor) % 4)
        data = json.loads(base64.urlsafe_b64decode(padded))
        return date.fromisoformat(data["p"]), int(data["i"])
    except (binascii.Error, ValueError, KeyError, TypeError):
        raise ApiError(422, "invalid_query", "Invalid cursor", {"cursor": "invalid"}) from None


@jobs_bp.get("/feed")
def feed():
    errors: dict[str, str] = {}
    reject_unknown(FEED_PARAMS, errors)
    limit = int_param("limit", 20, 1, 100, errors)
    raise_if(errors)

    stmt = select(Job).order_by(Job.posted_on.desc(), Job.id.desc()).limit(limit + 1)
    if cursor := request.args.get("cursor"):
        stmt = stmt.where(tuple_(Job.posted_on, Job.id) < decode_cursor(cursor))

    jobs = db.session.scalars(stmt).all()
    has_more = len(jobs) > limit            # fetched one extra row to know if there's a next page
    jobs = jobs[:limit]
    return {
        "data": [serialize(job) for job in jobs],
        "meta": {"limit": limit, "next_cursor": encode_cursor(jobs[-1]) if has_more and jobs else None},
    }


@jobs_bp.get("/<int:job_id>")
def get_job(job_id: int):
    job = db.session.get(Job, job_id)
    if job is None:
        raise ApiError(404, "job_not_found", f"Job {job_id} not found")
    return {"data": serialize(job)}
