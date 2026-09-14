"""Cost estimation, credit runway and waste detection. See README.md."""

import calendar
from dataclasses import dataclass
from datetime import date, timedelta

HOURS = 730
FREE_TRANSFER_GB = 100


@dataclass(frozen=True)
class Estimate:
    lines: list[tuple[str, float]]
    total: float


@dataclass(frozen=True)
class Runway:
    credits_exhausted: date | None
    plan_ends: date
    account_closes: date
    reason: str


@dataclass(frozen=True)
class Waste:
    resource_id: str
    issue: str
    monthly_cost: float


def _price(prices: dict, table: str, key: str) -> float:
    try:
        return float(prices[table][key])
    except KeyError:
        raise ValueError(f"no price for {table}:{key}") from None


def _cost(resource: dict, prices: dict) -> float:
    kind = resource["kind"]
    hourly = lambda key: _price(prices, "hourly", key)  # noqa: E731
    per_gb = lambda key: _price(prices, "monthly_per_gb", key)  # noqa: E731
    each = lambda key: _price(prices, "monthly_each", key)  # noqa: E731
    count = resource.get("count", 1)
    match kind:
        case "ec2":
            return (hourly(f"ec2:{resource['type']}") * resource.get("hours", HOURS) + per_gb("ebs:gp3") * resource.get("ebs_gb", 0)) * count
        case "rds":
            copies = 2 if resource.get("multi_az") else 1
            return (hourly(f"rds:{resource['type']}") * HOURS + per_gb("rds:gp3") * resource.get("storage_gb", 0)) * copies
        case "fargate":
            per_hour = resource["vcpu"] * hourly("fargate:vcpu") + resource["memory_gb"] * hourly("fargate:gb")
            return per_hour * resource.get("hours", HOURS) * resource.get("tasks", 1)
        case "alb":
            return hourly("alb") * HOURS
        case "nat_gateway":
            return hourly("nat_gateway") * HOURS + per_gb("nat_processed") * resource.get("processed_gb", 0)
        case "public_ipv4":
            return hourly("public_ipv4") * HOURS * count
        case "s3":
            return per_gb("s3:standard") * resource["gb"]
        case "data_transfer_out":
            return per_gb("data_transfer_out") * max(0, resource["gb"] - FREE_TRANSFER_GB)
        case "logs":
            return per_gb("cloudwatch_logs_ingest") * resource["ingest_gb"]
        case "secrets":
            return each("secretsmanager:secret") * count
        case "hosted_zone":
            return each("route53:hosted_zone") * count
    raise ValueError(f"unknown resource kind: {kind}")


def monthly_cost(resources: list[dict], prices: dict) -> Estimate:
    lines = []
    for resource in resources:
        label = resource["kind"] + (f":{resource['type']}" if "type" in resource else "")
        lines.append((label, round(_cost(resource, prices), 2)))
    lines.sort(key=lambda line: (-line[1], line[0]))
    return Estimate(lines, round(sum(cost for _, cost in lines), 2))


def _add_months(start: date, months: int) -> date:
    month_index = start.month - 1 + months
    year, month = start.year + month_index // 12, month_index % 12 + 1
    return date(year, month, min(start.day, calendar.monthrange(year, month)[1]))


def credit_runway(credits: float, monthly_cost: float, opened: date, today: date) -> Runway:
    plan_ends = _add_months(opened, 6)
    exhausted = None if monthly_cost <= 0 else today + timedelta(days=int(credits / (monthly_cost / 30)))
    if exhausted is not None and exhausted < plan_ends:
        return Runway(exhausted, plan_ends, exhausted, "credits")
    return Runway(exhausted, plan_ends, plan_ends, "plan_end")


def budget_alerts(monthly_budget: float) -> list[tuple[str, float]]:
    return [
        ("actual", round(monthly_budget * 0.5, 2)),
        ("actual", round(monthly_budget * 0.8, 2)),
        ("actual", round(monthly_budget, 2)),
        ("forecasted", round(monthly_budget, 2)),
    ]


def find_waste(inventory: list[dict], prices: dict) -> list[Waste]:
    waste: list[Waste] = []
    hourly = lambda key: _price(prices, "hourly", key) * HOURS  # noqa: E731
    per_gb = lambda key: _price(prices, "monthly_per_gb", key)  # noqa: E731
    for item in inventory:
        kind, rid = item["type"], item["id"]
        if kind == "ebs_volume" and not item.get("attached", True):
            waste.append(Waste(rid, "unattached volume", per_gb("ebs:gp3") * item["size_gb"]))
        elif kind == "elastic_ip" and not item.get("associated", True):
            waste.append(Waste(rid, "idle public IPv4", hourly("public_ipv4")))
        elif kind == "nat_gateway" and item.get("tags", {}).get("Env") in ("learning", "staging"):
            waste.append(Waste(rid, "NAT gateway outside production", hourly("nat_gateway")))
        elif kind == "instance" and item.get("state") == "stopped" and item.get("stopped_days", 0) >= 7:
            waste.append(Waste(rid, "stopped instance still paying for storage", per_gb("ebs:gp3") * item.get("ebs_gb", 0)))
        elif kind == "snapshot" and item.get("age_days", 0) > 30 and not item.get("keep"):
            waste.append(Waste(rid, "old snapshot", per_gb("ebs:snapshot") * item["size_gb"]))
        elif kind == "load_balancer" and item.get("targets", 0) == 0:
            waste.append(Waste(rid, "load balancer without targets", hourly("alb")))
    waste = [Waste(w.resource_id, w.issue, round(w.monthly_cost, 2)) for w in waste]
    return sorted(waste, key=lambda w: (-w.monthly_cost, w.resource_id))
