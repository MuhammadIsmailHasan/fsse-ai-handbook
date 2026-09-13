"""Accounts built by composition — reference solution.

An Account HAS roles and HAS a plan. New combinations are data, not new classes,
and changing a role or plan doesn't replace the object.
"""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Role:
    name: str
    permissions: frozenset[str]


JOB_SEEKER = Role("job_seeker", frozenset({"applications:read", "applications:write", "jobs:read"}))
RECRUITER = Role("recruiter", frozenset({"jobs:read", "jobs:write", "candidates:read"}))
ADMIN = Role("admin", frozenset({"*"}))


@dataclass(frozen=True)
class Plan:
    name: str
    features: frozenset[str]
    limits: dict[str, int] = field(default_factory=dict, hash=False, compare=False)


FREE = Plan("free", frozenset({"tracker"}), {"applications": 20})
PRO = Plan("pro", frozenset({"tracker", "ai_match", "export"}), {"applications": 1000})


class Account:
    def __init__(self, email: str, roles: set[Role] | None = None, plan: Plan = FREE):
        self.email = email
        self.roles: set[Role] = set(roles or ())
        self.plan = plan

    def grant(self, role: Role) -> None:
        self.roles.add(role)

    def revoke(self, role: Role) -> None:
        self.roles.discard(role)

    def change_plan(self, plan: Plan) -> None:
        self.plan = plan

    def can(self, permission: str) -> bool:
        resource = permission.split(":", 1)[0]
        wanted = {permission, "*", f"{resource}:*"}
        return any(role.permissions & wanted for role in self.roles)

    def has_feature(self, feature: str) -> bool:
        return feature in self.plan.features

    def limit(self, name: str) -> int:
        return self.plan.limits.get(name, 0)
