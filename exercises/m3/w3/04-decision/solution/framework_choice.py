"""Module 3 · W3 — Flask or FastAPI? (solution)"""


def choose_framework(
    *,
    existing_flask_app: bool,
    needs_async_io: bool,
    ai_streaming: bool,
    needs_auto_docs: bool,
    team_knows_fastapi: bool,
    server_rendered_pages: bool,
) -> str:
    if server_rendered_pages:
        return "flask"
    if existing_flask_app and not (needs_async_io or ai_streaming):
        return "keep-flask"

    score = (
        2 * needs_async_io
        + 2 * ai_streaming
        + needs_auto_docs
        + team_knows_fastapi
    )
    if existing_flask_app:
        score -= 2

    if score >= 3:
        return "fastapi"
    return "keep-flask" if existing_flask_app else "flask"
