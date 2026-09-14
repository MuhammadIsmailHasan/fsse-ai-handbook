# M5 · W3 · 01 — IAM policy simulator

> 🚫🤖 **No-AI** · ⏱️ ~2 h · no AWS account needed

Most AWS security mistakes are IAM mistakes. Build a small evaluator for **identity-based policies** (the JSON you attach to users and roles) in `iam_sim.py`, plus a reviewer that flags dangerous grants.

## 1. `evaluate(policies, action, resource, context=None) -> Decision`
`Decision` is `"Allow"`, `"ExplicitDeny"` or `"ImplicitDeny"`. Rules (a simplified version of AWS's logic):
1. Collect statements from all policies (`Statement` may be one object or a list).
2. A statement **applies** when its action matches (`Action` or `NotAction`), its resource matches (`Resource` or `NotResource`) and all its `Condition`s pass.
3. Any applying `Deny` → `"ExplicitDeny"` (deny always wins). Else any applying `Allow` → `"Allow"`. Else `"ImplicitDeny"`.

Matching:
- **Actions** are case-**insensitive** (`s3:GetObject` = `S3:getobject`); wildcards `*` and `?` work (`s3:Get*`, `ec2:Describe*`, `*`).
- **Resources** (ARNs) are case-**sensitive** with the same wildcards (`arn:aws:s3:::revoshop-images/*`).
- `NotAction` / `NotResource` apply to everything **except** the listed patterns.
- Values may be a string or a list.

Conditions (keys are case-insensitive; a missing key makes the condition **fail**, except `...IfExists` variants which pass when the key is missing):
`StringEquals`, `StringNotEquals`, `StringLike`, `Bool`, `NumericLessThan`, `NumericGreaterThanEquals`, `IpAddress` (CIDR), and `StringEqualsIfExists`, `BoolIfExists`. Multiple values for one key = OR; multiple keys/operators = AND. Unknown operators → the statement does **not** apply.

## 2. `review(policy) -> list[Finding]`
`Finding(sid: str, severity: "high" | "medium", message: str)` — `sid` is the statement's `Sid` or `"#<index>"`. Only `Allow` statements are reviewed:

| Severity | Finding |
|---|---|
| high | `Action` is `*` (or contains `*`) — full admin |
| high | action `iam:PassRole` (or `iam:*`) with `Resource` `*` — privilege escalation |
| high | uses `NotAction` with `Allow` (grants everything else, including future services) |
| medium | a service-wide action wildcard like `s3:*` or `ec2:*` |
| medium | `Resource` `*` for an action that isn't `Describe*`/`List*`/`Get*` style read-only (`*:Describe*`, `*:List*`, `*:Get*`) |

Report findings in statement order; within a statement in the order of the table.

```bash
cd exercises
uv run pytest m5/w3/01-iam-policy-simulator
```
