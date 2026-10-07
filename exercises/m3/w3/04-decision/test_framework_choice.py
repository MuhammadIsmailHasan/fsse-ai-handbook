from framework_choice import choose_framework

NONE = dict(
    existing_flask_app=False,
    needs_async_io=False,
    ai_streaming=False,
    needs_auto_docs=False,
    team_knows_fastapi=False,
    server_rendered_pages=False,
)


def pick(**changes):
    return choose_framework(**{**NONE, **changes})


def test_server_rendered_pages_always_flask():
    assert pick(server_rendered_pages=True) == "flask"
    assert pick(server_rendered_pages=True, ai_streaming=True, needs_async_io=True) == "flask"


def test_existing_app_with_no_reason_to_move_is_kept():
    assert pick(existing_flask_app=True) == "keep-flask"
    assert pick(existing_flask_app=True, needs_auto_docs=True, team_knows_fastapi=True) == "keep-flask"


def test_new_ai_service_with_streaming_and_docs_is_fastapi():
    assert pick(ai_streaming=True, needs_auto_docs=True) == "fastapi"


def test_new_app_with_nothing_special_is_flask():
    assert pick() == "flask"


def test_async_io_plus_team_skill_is_enough_for_a_new_app():
    assert pick(needs_async_io=True, team_knows_fastapi=True) == "fastapi"


def test_docs_and_skill_alone_are_not_enough():
    assert pick(needs_auto_docs=True, team_knows_fastapi=True) == "flask"


def test_existing_app_pays_a_migration_cost():
    # 2 (streaming) - 2 (migration) = 0 → stay
    assert pick(existing_flask_app=True, ai_streaming=True) == "keep-flask"
    # 2 + 1 + 1 - 2 = 2 → still stay
    assert pick(existing_flask_app=True, ai_streaming=True,
                needs_auto_docs=True, team_knows_fastapi=True) == "keep-flask"


def test_existing_app_with_strong_reasons_moves():
    # 2 + 2 + 1 - 2 = 3 → move
    assert pick(existing_flask_app=True, ai_streaming=True,
                needs_async_io=True, needs_auto_docs=True) == "fastapi"
