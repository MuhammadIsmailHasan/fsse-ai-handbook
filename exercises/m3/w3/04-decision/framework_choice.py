"""Module 3 · W3 — Flask or FastAPI? Turn a decision guide into code.

choose_framework(...) returns "flask", "keep-flask" or "fastapi".

Rules, in this order:
1. server_rendered_pages           → "flask"   (HTML templates are Flask's home turf)
2. existing_flask_app and NOT (needs_async_io or ai_streaming)
                                    → "keep-flask"   (a rewrite has a cost; nothing needs it)
3. Otherwise score FastAPI:
       +2 needs_async_io
       +2 ai_streaming
       +1 needs_auto_docs
       +1 team_knows_fastapi
       -2 if existing_flask_app     (migration cost)
   score >= 3                        → "fastapi"
   score <  3 and existing_flask_app → "keep-flask"
   score <  3 and a new app          → "flask"
"""


def choose_framework(
    *,
    existing_flask_app: bool,
    needs_async_io: bool,
    ai_streaming: bool,
    needs_auto_docs: bool,
    team_knows_fastapi: bool,
    server_rendered_pages: bool,
) -> str:
    # YOUR CODE HERE
    return ""
