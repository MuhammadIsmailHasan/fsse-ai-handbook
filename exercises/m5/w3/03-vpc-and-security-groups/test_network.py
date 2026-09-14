"""Checks for network.py. Don't edit this file."""

import pytest

from network import Subnet, audit, can_reach, plan_subnets, route_problems, usable_ips


def test_plan_subnets():
    subnets = plan_subnets("10.20.0.0/16", ["ap-southeast-3a", "ap-southeast-3b"])
    assert [(s.name, s.cidr) for s in subnets] == [
        ("public-ap-southeast-3a", "10.20.0.0/24"),
        ("public-ap-southeast-3b", "10.20.1.0/24"),
        ("app-ap-southeast-3a", "10.20.2.0/24"),
        ("app-ap-southeast-3b", "10.20.3.0/24"),
        ("data-ap-southeast-3a", "10.20.4.0/24"),
        ("data-ap-southeast-3b", "10.20.5.0/24"),
    ]
    assert subnets[2] == Subnet("app-ap-southeast-3a", "app", "ap-southeast-3a", "10.20.2.0/24")
    small = plan_subnets("192.168.10.0/24", ["a", "b", "c"], tiers=("public", "data"), prefix=27)
    assert [s.cidr for s in small] == ["192.168.10.0/27", "192.168.10.32/27", "192.168.10.64/27", "192.168.10.96/27", "192.168.10.128/27", "192.168.10.160/27"]


@pytest.mark.parametrize(
    ("cidr", "azs", "prefix"),
    [("8.8.0.0/16", ["a"], 24), ("10.0.0.0/8", ["a"], 24), ("10.0.0.0/25", ["a"], 28), ("10.0.0.0/24", ["a"], 24), ("10.0.0.0/24", ["a", "b"], 25)],
)
def test_plan_subnets_rejects(cidr, azs, prefix):
    with pytest.raises(ValueError):
        plan_subnets(cidr, azs, prefix=prefix)


def test_usable_ips():
    assert usable_ips("10.20.0.0/24") == 251
    assert usable_ips("10.20.0.0/28") == 11


def test_route_problems():
    subnets = plan_subnets("10.20.0.0/16", ["a"])
    tables = {
        "public-a": {"10.20.0.0/16": "local", "0.0.0.0/0": "igw-0abc"},
        "app-a": {"10.20.0.0/16": "local", "0.0.0.0/0": "nat-0def"},
        "data-a": {"10.20.0.0/16": "local"},
    }
    assert route_problems(subnets, tables) == []
    broken = {
        "public-a": {"10.20.0.0/16": "local", "0.0.0.0/0": "nat-0def"},
        "app-a": {"10.20.0.0/16": "local", "0.0.0.0/0": "igw-0abc"},
        "data-a": {"10.20.0.0/16": "local", "0.0.0.0/0": "igw-0abc"},
    }
    assert route_problems(subnets, broken) == [
        "public-a: public subnet without internet gateway route",
        "app-a: private subnet routes to an internet gateway",
        "data-a: private subnet routes to an internet gateway",
        "data-a: data subnet has a default route",
    ]
    assert route_problems(subnets, {"public-a": tables["public-a"]}) == ["app-a: no route table", "data-a: no route table"]


GROUPS = {
    "sg-alb": [{"protocol": "tcp", "from_port": 443, "to_port": 443, "source": "0.0.0.0/0"}, {"protocol": "tcp", "from_port": 80, "to_port": 80, "source": "0.0.0.0/0"}],
    "sg-api": [{"protocol": "tcp", "from_port": 5000, "to_port": 5000, "source": "sg-alb"}],
    "sg-db": [{"protocol": "tcp", "from_port": 5432, "to_port": 5432, "source": "sg-api"}],
    "sg-admin": [{"protocol": "tcp", "from_port": 22, "to_port": 22, "source": "203.0.113.10/32"}],
    "sg-monitoring": [{"protocol": "-1", "from_port": 0, "to_port": 0, "source": "10.20.9.0/24"}],
}
MEMBERS = {
    "alb": {"groups": ["sg-alb"], "ip": "10.20.0.10"},
    "api-1": {"groups": ["sg-api", "sg-admin"], "ip": "10.20.2.15"},
    "db": {"groups": ["sg-db", "sg-monitoring"], "ip": "10.20.4.20"},
    "bastion": {"groups": [], "ip": "10.20.9.5"},
}


def test_can_reach():
    assert can_reach(GROUPS, MEMBERS, "internet:198.51.100.7", "alb", 443)
    assert not can_reach(GROUPS, MEMBERS, "internet:198.51.100.7", "api-1", 5000)
    assert can_reach(GROUPS, MEMBERS, "alb", "api-1", 5000)
    assert not can_reach(GROUPS, MEMBERS, "alb", "db", 5432)
    assert can_reach(GROUPS, MEMBERS, "api-1", "db", 5432)
    assert not can_reach(GROUPS, MEMBERS, "api-1", "db", 5433)
    assert not can_reach(GROUPS, MEMBERS, "api-1", "db", 5432, protocol="udp")
    assert can_reach(GROUPS, MEMBERS, "internet:203.0.113.10", "api-1", 22)
    assert not can_reach(GROUPS, MEMBERS, "internet:203.0.113.11", "api-1", 22)
    assert can_reach(GROUPS, MEMBERS, "bastion", "db", 9187, protocol="udp")


def test_audit():
    risky = {
        "sg-alb": GROUPS["sg-alb"],
        "sg-oops": [
            {"protocol": "tcp", "from_port": 22, "to_port": 22, "source": "0.0.0.0/0"},
            {"protocol": "tcp", "from_port": 5000, "to_port": 6500, "source": "::/0"},
            {"protocol": "-1", "from_port": 0, "to_port": 0, "source": "0.0.0.0/0"},
        ],
        "sg-db": GROUPS["sg-db"],
    }
    assert [(g, m.split(" ")[0]) for g, m in audit(risky)] == [
        ("sg-oops", "SSH"),
        ("sg-oops", "PostgreSQL"),
        ("sg-oops", "Redis"),
        ("sg-oops", "all"),
    ]
    assert audit(GROUPS) == []
