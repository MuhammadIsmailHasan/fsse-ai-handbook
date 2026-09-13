"""Reference solution."""

from flask import Blueprint, request
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError

from errors import Conflict, NotFound, ValidationFailed
from models import Company, db

companies_bp = Blueprint("companies", __name__, url_prefix="/api/v1/companies")
FIELDS = {"name", "website"}


def serialize(company: Company) -> dict:
    return {"id": company.id, "name": company.name, "website": company.website}


def json_object() -> dict:
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        raise ValidationFailed({"body": "must be a JSON object"})
    return data


def clean(data: dict, *, partial: bool) -> dict:
    errors, cleaned = {}, {}
    for name in data:
        if name not in FIELDS:
            errors[name] = "unknown field"
    if "name" in data:
        name = data["name"]
        if not isinstance(name, str) or not 1 <= len(name.strip()) <= 200:
            errors["name"] = "must be 1-200 characters"
        else:
            cleaned["name"] = name.strip()
    elif not partial:
        errors["name"] = "required"
    if "website" in data:
        website = data["website"]
        if website is not None and not (isinstance(website, str) and website.startswith("https://")):
            errors["website"] = "must be null or an https:// URL"
        else:
            cleaned["website"] = website
    if errors:
        raise ValidationFailed(errors)
    return cleaned


def get_or_404(company_id: int) -> Company:
    company = db.session.get(Company, company_id)
    if company is None:
        raise NotFound(f"Company {company_id} not found", code="company_not_found")
    return company


def commit_or_conflict(code: str, message: str) -> None:
    try:
        db.session.commit()
    except IntegrityError as error:
        db.session.rollback()  # make the session usable again
        raise Conflict(message, code=code) from error


@companies_bp.get("")
def list_companies():
    stmt = select(Company).order_by(func.lower(Company.name), Company.id)
    if q := request.args.get("q"):
        stmt = stmt.where(Company.name.ilike(f"%{q}%"))  # bound parameter, safe from injection
    return {"data": [serialize(c) for c in db.session.scalars(stmt)]}


@companies_bp.get("/<int:company_id>")
def get_company(company_id: int):
    return {"data": serialize(get_or_404(company_id))}


@companies_bp.post("")
def create_company():
    cleaned = clean(json_object(), partial=False)
    company = Company(name=cleaned["name"], website=cleaned.get("website"))
    db.session.add(company)
    commit_or_conflict("company_exists", f"A company named {cleaned['name']!r} already exists")
    return {"data": serialize(company)}, 201, {"Location": f"/api/v1/companies/{company.id}"}


@companies_bp.patch("/<int:company_id>")
def update_company(company_id: int):
    company = get_or_404(company_id)
    for field, value in clean(json_object(), partial=True).items():
        setattr(company, field, value)
    commit_or_conflict("company_exists", "A company with that name already exists")
    return {"data": serialize(company)}


@companies_bp.delete("/<int:company_id>")
def delete_company(company_id: int):
    company = get_or_404(company_id)
    db.session.delete(company)
    commit_or_conflict("company_in_use", "Jobs still reference this company")
    return "", 204
