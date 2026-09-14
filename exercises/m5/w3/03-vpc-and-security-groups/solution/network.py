"""VPC planning and security-group analysis. See README.md."""

import ipaddress
from dataclasses import dataclass


@dataclass(frozen=True)
class Subnet:
    name: str
    tier: str
    az: str
    cidr: str


def plan_subnets(vpc_cidr: str, azs: list[str], *, tiers=("public", "app", "data"), prefix: int = 24) -> list[Subnet]:
    vpc = ipaddress.ip_network(vpc_cidr)
    if not vpc.is_private or not 16 <= vpc.prefixlen <= 24:
        raise ValueError("VPC must be an RFC 1918 network between /16 and /24")
    if prefix <= vpc.prefixlen:
        raise ValueError("subnet prefix must be longer than the VPC prefix")
    blocks = vpc.subnets(new_prefix=prefix)
    subnets = []
    for tier in tiers:
        for az in azs:
            try:
                block = next(blocks)
            except StopIteration:
                raise ValueError("not enough address space for all subnets") from None
            subnets.append(Subnet(f"{tier}-{az}", tier, az, str(block)))
    return subnets


def usable_ips(cidr: str) -> int:
    return ipaddress.ip_network(cidr).num_addresses - 5  # network, VPC router, DNS, future use, broadcast


def route_problems(subnets: list[Subnet], route_tables: dict[str, dict[str, str]]) -> list[str]:
    problems = []
    for subnet in subnets:
        routes = route_tables.get(subnet.name)
        if routes is None:
            problems.append(f"{subnet.name}: no route table")
            continue
        igw_targets = [dest for dest, target in routes.items() if target.startswith("igw-")]
        if subnet.tier == "public" and not routes.get("0.0.0.0/0", "").startswith("igw-"):
            problems.append(f"{subnet.name}: public subnet without internet gateway route")
        if subnet.tier in ("app", "data") and igw_targets:
            problems.append(f"{subnet.name}: private subnet routes to an internet gateway")
        if subnet.tier == "data" and "0.0.0.0/0" in routes:
            problems.append(f"{subnet.name}: data subnet has a default route")
    return problems


def _rule_matches(rule: dict, port: int, protocol: str) -> bool:
    if rule["protocol"] == "-1":
        return True
    return rule["protocol"] == protocol and rule["from_port"] <= port <= rule["to_port"]


def can_reach(groups: dict, members: dict, source: str, target: str, port: int, protocol: str = "tcp") -> bool:
    if source.startswith("internet:"):
        source_ip, source_groups = source.split(":", 1)[1], set()
    else:
        source_ip, source_groups = members[source]["ip"], set(members[source]["groups"])
    for group_id in members[target]["groups"]:
        for rule in groups.get(group_id, []):
            if not _rule_matches(rule, port, protocol):
                continue
            origin = rule["source"]
            if origin.startswith("sg-"):
                if origin in source_groups:
                    return True
            elif ipaddress.ip_address(source_ip) in ipaddress.ip_network(origin, strict=False):
                return True
    return False


SENSITIVE_PORTS = {22: "SSH", 3389: "RDP", 5432: "PostgreSQL", 3306: "MySQL", 6379: "Redis"}


def audit(groups: dict) -> list[tuple[str, str]]:
    findings = []
    for group_id, rules in groups.items():
        for rule in rules:
            if rule["source"] not in ("0.0.0.0/0", "::/0"):
                continue
            if rule["protocol"] == "-1":
                findings.append((group_id, f"all traffic open to {rule['source']}"))
                continue
            for port, name in SENSITIVE_PORTS.items():
                if rule["from_port"] <= port <= rule["to_port"]:
                    findings.append((group_id, f"{name} ({port}) open to {rule['source']}"))
    return findings
