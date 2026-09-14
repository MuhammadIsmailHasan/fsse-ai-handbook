# M5 · W2 · 04 — GitHub OIDC → AWS: build and test a trust policy

> 🚫🤖 **No-AI** · ⏱️ ~90 min · no AWS account needed

With OIDC, GitHub Actions gets **short-lived** AWS credentials by presenting a signed token; AWS checks the token's claims against the IAM role's **trust policy**. A too-loose policy (`repo:you/*` or `*`) lets **other repositories or forks** deploy to your account. Write the policy generator **and** a small evaluator to prove who can assume the role.

## 1. `trust_policy(account_id, owner, repo, *, environments=(), branches=()) -> dict`
Returns an IAM policy document:
```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": {"Federated": "arn:aws:iam::<account_id>:oidc-provider/token.actions.githubusercontent.com"},
    "Action": "sts:AssumeRoleWithWebIdentity",
    "Condition": {
      "StringEquals": {"token.actions.githubusercontent.com:aud": "sts.amazonaws.com"},
      "StringLike": {"token.actions.githubusercontent.com:sub": ["repo:<owner>/<repo>:environment:production", "repo:<owner>/<repo>:ref:refs/heads/main"]}
    }
  }]
}
```
- `sub` patterns: one per environment (`repo:{owner}/{repo}:environment:{env}`) then one per branch (`repo:{owner}/{repo}:ref:refs/heads/{branch}`), in that order
- `account_id` must be 12 digits; `owner`, `repo`, environment and branch names must not contain `*`, `?` or `:` and must be non-empty → `ValueError`
- at least one environment or branch is required → `ValueError` (never trust a whole repository)

## 2. `allows(policy, claims) -> bool`
Simulate AWS's decision for a token with claims like `{"iss": "https://token.actions.githubusercontent.com", "aud": "sts.amazonaws.com", "sub": "repo:sari/revoshop:environment:production"}` and the action `sts:AssumeRoleWithWebIdentity`:
- a statement matches when `Effect` is `Allow`, `Action` equals (or is a list containing) the action, the `Principal.Federated` ARN ends with `oidc-provider/<iss host>`, and **every** condition passes
- condition keys look like `token.actions.githubusercontent.com:<claim>`; a missing claim fails the condition
- `StringEquals`: exact, case-sensitive; value may be a string or a list (any match)
- `StringLike`: `*` matches any sequence, `?` one character, everything else literal and case-sensitive; string or list
- unknown condition operators → the statement **doesn't** match (fail closed)
- any matching statement → `True`; otherwise `False`

Real GitHub `sub` formats: `repo:OWNER/REPO:environment:NAME`, `repo:OWNER/REPO:ref:refs/heads/BRANCH`, `repo:OWNER/REPO:ref:refs/tags/TAG`, `repo:OWNER/REPO:pull_request`.

```bash
cd exercises
uv run pytest m5/w2/04-oidc-trust-policy
```
