# M5 · W3 · 03 — VPC planner and security-group reachability

> 🚫🤖 **No-AI** · ⏱️ ~2 h · no AWS account needed

Plan RevoShop's network before clicking in the console: subnets per tier and Availability Zone, correct routes, and security groups that let **only** the right traffic through. Write `network.py`.

## 1. `plan_subnets(vpc_cidr, azs, *, tiers=("public", "app", "data"), prefix=24) -> list[Subnet]`
- `Subnet(name, tier, az, cidr)` with `name = f"{tier}-{az}"`
- the VPC must be a private (RFC 1918) network with a prefix between **/16 and /24**, and `prefix` must be longer than the VPC's → otherwise `ValueError`
- allocate consecutive subnets from the start of the VPC: all AZs of the first tier, then the next tier (for `10.20.0.0/16`, AZs `a,b`: `public-a 10.20.0.0/24`, `public-b 10.20.1.0/24`, `app-a 10.20.2.0/24`, …)
- not enough space → `ValueError`

`usable_ips(cidr) -> int` — AWS reserves **5** addresses in every subnet.

## 2. `route_problems(subnets, route_tables) -> list[str]`
`route_tables` maps a subnet name to its routes: `{"0.0.0.0/0": "igw-123", "10.20.0.0/16": "local"}`.
- every subnet must have a route table → `"<name>: no route table"`
- **public** subnets need `0.0.0.0/0 → igw-*` → `"<name>: public subnet without internet gateway route"`
- **app** and **data** subnets must not route to an internet gateway → `"<name>: private subnet routes to an internet gateway"`
- **data** subnets must have no `0.0.0.0/0` route at all → `"<name>: data subnet has a default route"`
Messages in subnet order, then check order.

## 3. `can_reach(groups, members, source, target, port, protocol="tcp") -> bool`
- `groups`: security group id → list of ingress rules `{"protocol": "tcp" | "udp" | "-1", "from_port": int, "to_port": int, "source": "sg-…" or CIDR}` (`"-1"` = all protocols and ports)
- `members`: resource id → `{"groups": [sg ids], "ip": "10.20.2.15"}`
- `source` is a resource id **or** `"internet:<ip>"`; security groups are stateful and allow all egress
- reachable if **any** rule of **any** group of the target matches protocol, port range and source (a source SG matches when the source resource belongs to it; a CIDR matches the source IP)

## 4. `audit(groups) -> list[tuple[str, str]]`
`(group_id, message)` for ingress rules open to `0.0.0.0/0` or `::/0` that allow **all traffic**, or include port **22, 3389, 5432, 3306 or 6379**. Ports 80 and 443 open to the world are fine. Order: groups in dict order, rules in order.

```bash
cd exercises
uv run pytest m5/w3/03-vpc-and-security-groups
```
