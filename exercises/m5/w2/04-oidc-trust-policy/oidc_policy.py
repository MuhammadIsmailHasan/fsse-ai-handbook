"""GitHub OIDC trust policies for AWS. See README.md."""


def trust_policy(account_id: str, owner: str, repo: str, *, environments: tuple[str, ...] | list[str] = (), branches: tuple[str, ...] | list[str] = ()) -> dict:
    raise NotImplementedError


def allows(policy: dict, claims: dict[str, str]) -> bool:
    raise NotImplementedError
