"""M2 · W3 · 07 — Add type hints, run mypy --strict, fix the None bugs."""


def first_or_none(items):
    return items[0] if items else None


def format_rupiah(amount):
    return "Rp " + f"{amount:,}".replace(",", ".")


def salary_label(repo, application_id):
    application = repo.get(application_id)
    return format_rupiah(application["salary"])


def advance(repo, application_id, status):
    application = repo.get(application_id)
    updated = {**application, "status": status}
    repo.save(updated)
    return updated
