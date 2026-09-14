# M5 · W3 · 02 — Cost guard: estimate, runway and waste

> 🚫🤖 **No-AI** · ⏱️ ~90 min · no AWS account needed

On the AWS **free plan** your account **closes** when the credits run out or after six months, whichever comes first; on a paid plan the bill simply grows. Either way you need to know **what a design costs per month**, **how long your credits last**, and **what's quietly burning money**. Build that in `cost_guard.py` using the **sample** prices in `prices.json` (real prices vary — use the AWS Pricing Calculator for real decisions).

A month is **730 hours**.

## 1. `monthly_cost(resources, prices) -> Estimate`
Each resource is a dict with a `kind`:

| kind | fields | cost |
|---|---|---|
| `ec2` | `type`, `count` (default 1), `hours` (default 730), `ebs_gb` (gp3) | hourly(`ec2:<type>`) × hours × count + `ebs:gp3` × ebs_gb × count |
| `rds` | `type`, `storage_gb`, `multi_az` (default False) | hourly(`rds:<type>`) × 730 × (2 if multi_az) + `rds:gp3` × storage_gb × (2 if multi_az) |
| `fargate` | `vcpu`, `memory_gb`, `tasks` (default 1), `hours` (default 730) | (vcpu × `fargate:vcpu` + memory_gb × `fargate:gb`) × hours × tasks |
| `alb` | — | hourly(`alb`) × 730 (ignore LCU usage) |
| `nat_gateway` | `processed_gb` (default 0) | hourly × 730 + `nat_processed` × processed_gb |
| `public_ipv4` | `count` | hourly × 730 × count |
| `s3` | `gb` | `s3:standard` × gb |
| `data_transfer_out` | `gb` | first **100 GB free**, then per GB |
| `logs` | `ingest_gb` | `cloudwatch_logs_ingest` × gb |
| `secrets` | `count` | `secretsmanager:secret` × count |
| `hosted_zone` | `count` (default 1) | `route53:hosted_zone` × count |

Unknown `kind` or a missing price → `ValueError`. Return `Estimate(lines, total)` where `lines` is a list of `(label, cost)` — `label` is `kind` plus `:type` when present (e.g. `ec2:t4g.small`) — sorted by cost **descending** (ties by label), costs and total rounded to 2 decimals.

## 2. `credit_runway(credits, monthly_cost, opened, today) -> Runway`
- plan end = `opened` + 6 months (same day of month; if that day doesn't exist, the last day of that month)
- credits exhausted on `today + credits / (monthly_cost / 30)` days (whole days, rounded **down**); `None` if monthly cost is 0
- `Runway(credits_exhausted: date | None, plan_ends: date, account_closes: date, reason: "credits" | "plan_end")` — the free plan closes on whichever comes **first**

## 3. `budget_alerts(monthly_budget) -> list[tuple[str, float]]`
`[("actual", 50%), ("actual", 80%), ("actual", 100%), ("forecasted", 100%)]` as amounts rounded to 2 decimals.

## 4. `find_waste(inventory, prices) -> list[Waste]`
`Waste(resource_id, issue, monthly_cost)` sorted by monthly cost descending:
- `ebs_volume` with `attached: False` → `"unattached volume"` (gp3 × size_gb)
- `elastic_ip` with `associated: False` → `"idle public IPv4"`
- `nat_gateway` in an environment tagged `learning` or `staging` → `"NAT gateway outside production"`
- `instance` with `state: "stopped"` and `stopped_days >= 7` → `"stopped instance still paying for storage"` (gp3 × ebs_gb)
- `snapshot` with `age_days > 30` and no `keep: True` → `"old snapshot"` (snapshot × size_gb)
- `load_balancer` with `targets: 0` → `"load balancer without targets"`

```bash
cd exercises
uv run pytest m5/w3/02-cost-guard
```
