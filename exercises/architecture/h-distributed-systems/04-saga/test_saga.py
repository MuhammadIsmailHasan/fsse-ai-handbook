from saga import run_saga


def booking_steps(fail_on=None):
    """A booking saga: reserve stock, charge payment, create shipment.
    If `fail_on` matches a step name, that step's action raises."""

    def make(name):
        def action(ctx):
            if name == fail_on:
                raise RuntimeError(f"{name} failed")
            ctx.setdefault("done", []).append(name)

        def compensate(ctx):
            ctx.setdefault("undone", []).append(name)

        return {"name": name, "action": action, "compensate": compensate}

    return [make("reserve_stock"), make("charge_payment"), make("create_shipment")]


def test_full_success_commits_everything():
    ctx: dict = {}
    result = run_saga(booking_steps(), ctx)
    assert result["status"] == "committed"
    assert result["committed"] == ["reserve_stock", "charge_payment", "create_shipment"]
    assert result["compensated"] == []
    assert result["failed_at"] is None
    assert ctx["done"] == ["reserve_stock", "charge_payment", "create_shipment"]
    assert "undone" not in ctx  # nothing compensated


def test_midway_failure_undoes_earlier_steps_in_reverse():
    ctx: dict = {}
    result = run_saga(booking_steps(fail_on="create_shipment"), ctx)
    assert result["status"] == "aborted"
    assert result["failed_at"] == "create_shipment"
    # The two earlier steps committed, then were undone newest-first.
    assert result["committed"] == ["reserve_stock", "charge_payment"]
    assert result["compensated"] == ["charge_payment", "reserve_stock"]
    assert ctx["undone"] == ["charge_payment", "reserve_stock"]


def test_first_step_failure_compensates_nothing():
    ctx: dict = {}
    result = run_saga(booking_steps(fail_on="reserve_stock"), ctx)
    assert result["status"] == "aborted"
    assert result["failed_at"] == "reserve_stock"
    assert result["committed"] == []
    assert result["compensated"] == []  # nothing had completed yet
