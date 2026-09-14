"""Checks for cost_guard.py. Don't edit this file."""

import json
from datetime import date
from pathlib import Path

import pytest

from cost_guard import Estimate, Runway, Waste, budget_alerts, credit_runway, find_waste, monthly_cost

PRICES = json.loads((Path(__file__).parent / "prices.json").read_text())


def test_ec2_compose_design():
    estimate = monthly_cost(
        [
            {"kind": "ec2", "type": "t4g.small", "ebs_gb": 20},
            {"kind": "public_ipv4", "count": 1},
            {"kind": "rds", "type": "db.t4g.micro", "storage_gb": 20},
            {"kind": "s3", "gb": 10},
            {"kind": "data_transfer_out", "gb": 40},
            {"kind": "hosted_zone"},
        ],
        PRICES,
    )
    assert estimate == Estimate(
        lines=[
            ("rds:db.t4g.micro", 13.98),
            ("ec2:t4g.small", 13.86),
            ("public_ipv4", 3.65),
            ("hosted_zone", 0.5),
            ("s3", 0.23),
            ("data_transfer_out", 0.0),
        ],
        total=32.22,
    )


def test_ecs_design_with_traps():
    estimate = monthly_cost(
        [
            {"kind": "fargate", "vcpu": 0.25, "memory_gb": 0.5, "tasks": 2},
            {"kind": "alb"},
            {"kind": "nat_gateway", "processed_gb": 10},
            {"kind": "rds", "type": "db.t4g.micro", "storage_gb": 20, "multi_az": True},
            {"kind": "public_ipv4", "count": 2},
            {"kind": "secrets", "count": 3},
            {"kind": "logs", "ingest_gb": 2},
            {"kind": "data_transfer_out", "gb": 150},
            {"kind": "ec2", "type": "t4g.micro", "count": 2, "hours": 100, "ebs_gb": 8},
        ],
        PRICES,
    )
    lines = dict(estimate.lines)
    assert lines["nat_gateway"] == 33.3
    assert lines["rds:db.t4g.micro"] == 27.96
    assert lines["fargate"] == 18.02
    assert lines["alb"] == 16.43
    assert lines["public_ipv4"] == 7.3
    assert lines["data_transfer_out"] == 4.5
    assert lines["ec2:t4g.micro"] == 2.96
    assert lines["secrets"] == 1.2 and lines["logs"] == 1.0
    assert estimate.lines[0][0] == "nat_gateway"
    assert estimate.total == round(sum(lines.values()), 2) == 112.67


def test_unknown_inputs():
    with pytest.raises(ValueError):
        monthly_cost([{"kind": "ec2", "type": "m7i.48xlarge"}], PRICES)
    with pytest.raises(ValueError):
        monthly_cost([{"kind": "quantum"}], PRICES)


def test_credit_runway():
    assert credit_runway(100, 30, opened=date(2026, 9, 15), today=date(2026, 9, 15)) == Runway(date(2026, 12, 24), date(2027, 3, 15), date(2026, 12, 24), "credits")
    assert credit_runway(200, 20, opened=date(2026, 8, 31), today=date(2026, 9, 1)) == Runway(date(2027, 6, 28), date(2027, 2, 28), date(2027, 2, 28), "plan_end")
    assert credit_runway(100, 0, opened=date(2026, 3, 31), today=date(2026, 4, 1)) == Runway(None, date(2026, 9, 30), date(2026, 9, 30), "plan_end")
    assert credit_runway(10, 112.67, opened=date(2026, 9, 15), today=date(2026, 10, 1)).credits_exhausted == date(2026, 10, 3)


def test_budget_alerts():
    assert budget_alerts(25) == [("actual", 12.5), ("actual", 20.0), ("actual", 25.0), ("forecasted", 25.0)]
    assert budget_alerts(33.33)[1] == ("actual", 26.66)


def test_find_waste():
    inventory = [
        {"type": "ebs_volume", "id": "vol-old", "attached": False, "size_gb": 30},
        {"type": "ebs_volume", "id": "vol-root", "attached": True, "size_gb": 20},
        {"type": "elastic_ip", "id": "eipalloc-1", "associated": False},
        {"type": "elastic_ip", "id": "eipalloc-2", "associated": True},
        {"type": "nat_gateway", "id": "nat-lab", "tags": {"Env": "learning"}},
        {"type": "nat_gateway", "id": "nat-prod", "tags": {"Env": "production"}},
        {"type": "instance", "id": "i-stopped", "state": "stopped", "stopped_days": 12, "ebs_gb": 30},
        {"type": "instance", "id": "i-recent", "state": "stopped", "stopped_days": 2, "ebs_gb": 30},
        {"type": "snapshot", "id": "snap-old", "age_days": 90, "size_gb": 20},
        {"type": "snapshot", "id": "snap-keep", "age_days": 400, "size_gb": 20, "keep": True},
        {"type": "load_balancer", "id": "alb-empty", "targets": 0},
        {"type": "load_balancer", "id": "alb-live", "targets": 2},
    ]
    assert find_waste(inventory, PRICES) == [
        Waste("nat-lab", "NAT gateway outside production", 32.85),
        Waste("alb-empty", "load balancer without targets", 16.43),
        Waste("eipalloc-1", "idle public IPv4", 3.65),
        Waste("i-stopped", "stopped instance still paying for storage", 2.4),
        Waste("vol-old", "unattached volume", 2.4),
        Waste("snap-old", "old snapshot", 1.0),
    ]
