"""Checks workflows/ci-cd.yml and workflows/deploy.yml. Don't edit this file."""

import re
from pathlib import Path

import pytest
import yaml

HERE = Path(__file__).parent / "workflows"
SHA = re.compile(r"^[\w.-]+/[\w.-]+@[0-9a-f]{40}$")


def load(name: str) -> dict:
    data = yaml.safe_load((HERE / name).read_text())
    assert isinstance(data, dict), f"{name} is empty"
    if True in data:  # YAML 1.1 parses the key `on` as True
        data["on"] = data.pop(True)
    return data


@pytest.fixture()
def cicd():
    return load("ci-cd.yml")


@pytest.fixture()
def deploy():
    return load("deploy.yml")


def jobs(workflow):
    assert workflow.get("jobs"), "no jobs defined"
    return workflow["jobs"]


def steps(job):
    return job.get("steps", [])


def uses(job, prefix):
    return [s for s in steps(job) if s.get("uses", "").startswith(prefix)]


def all_steps(*workflows):
    return [s for w in workflows for j in jobs(w).values() for s in steps(j)]


def test_triggers_permissions_concurrency(cicd):
    on = cicd["on"]
    assert on["pull_request"]["branches"] == ["main"]
    assert on["push"]["branches"] == ["main"] and on["push"]["tags"] == ["v*.*.*"]
    assert "workflow_dispatch" in on
    assert cicd["permissions"] == {"contents": "read"}
    assert cicd["concurrency"]["group"] == "${{ github.workflow }}-${{ github.ref }}"
    assert cicd["concurrency"]["cancel-in-progress"] == "${{ github.event_name == 'pull_request' }}"


def test_hygiene_pinned_actions_timeouts_no_injection(cicd, deploy):
    for workflow in (cicd, deploy):
        for name, job in jobs(workflow).items():
            if "steps" in job:
                assert job.get("runs-on") == "ubuntu-latest", name
                assert isinstance(job.get("timeout-minutes"), int), f"{name} needs timeout-minutes"
    for step in all_steps(cicd, deploy):
        if "uses" in step:
            assert SHA.match(step["uses"]), f"pin {step['uses']} to a full commit SHA"
            if step["uses"].startswith("actions/checkout@"):
                assert step.get("with", {}).get("persist-credentials") is False
        if "run" in step:
            assert "${{" not in step["run"], f"move expressions out of run: {step['run']!r}"
    text = (HERE / "ci-cd.yml").read_text() + (HERE / "deploy.yml").read_text()
    assert "AWS_ACCESS_KEY_ID" not in text and "AWS_SECRET_ACCESS_KEY" not in text


def test_lint_job(cicd):
    lint = jobs(cicd)["lint"]
    python = uses(lint, "actions/setup-python@")
    assert python and python[0]["with"] == {"python-version": "3.12", "cache": "pip"}
    runs = [s["run"].strip() for s in steps(lint) if "run" in s]
    assert "pip install -r requirements-dev.txt" in runs and "ruff check ." in runs
    assert uses(lint, "actions/checkout@")


def test_test_job_uses_real_services(cicd):
    test = jobs(cicd)["test"]
    assert test["needs"] in ("lint", ["lint"])
    pg, redis = test["services"]["postgres"], test["services"]["redis"]
    assert pg["image"] == "postgres:16-alpine"
    assert pg["env"] == {"POSTGRES_PASSWORD": "postgres", "POSTGRES_DB": "test"}
    assert "5432:5432" in pg["ports"] and "pg_isready" in pg["options"]
    assert redis["image"] == "redis:8-alpine" and "6379:6379" in redis["ports"] and "redis-cli ping" in redis["options"]
    assert test["env"] == {"DATABASE_URL": "postgresql://postgres:postgres@localhost:5432/test", "REDIS_URL": "redis://localhost:6379/0"}
    runs = [s["run"].strip() for s in steps(test) if "run" in s]
    assert "python -m pytest --junitxml=reports/junit.xml" in runs
    upload = uses(test, "actions/upload-artifact@")
    assert upload and upload[0]["if"] == "always()" and upload[0]["with"]["path"].rstrip("/") == "reports"


def test_build_job(cicd):
    build = jobs(cicd)["build"]
    assert build["needs"] in ("test", ["test"])
    assert build["permissions"] == {"contents": "read", "packages": "write"}
    assert build["outputs"]["image"] == "ghcr.io/${{ github.repository }}@${{ steps.build.outputs.digest }}"
    assert uses(build, "docker/setup-buildx-action@")
    login = uses(build, "docker/login-action@")
    assert login and login[0]["if"] == "github.event_name != 'pull_request'"
    assert login[0]["with"] == {"registry": "ghcr.io", "username": "${{ github.actor }}", "password": "${{ secrets.GITHUB_TOKEN }}"}
    meta = uses(build, "docker/metadata-action@")
    assert meta and meta[0]["id"] == "meta" and meta[0]["with"]["images"] == "ghcr.io/${{ github.repository }}"
    tags = {line.strip() for line in meta[0]["with"]["tags"].splitlines() if line.strip()}
    assert tags == {"type=sha", "type=ref,event=branch", "type=ref,event=pr", "type=semver,pattern={{version}}", "type=semver,pattern={{major}}.{{minor}}"}
    push = uses(build, "docker/build-push-action@")
    assert push and push[0]["id"] == "build"
    w = push[0]["with"]
    assert w["target"] == "prod"
    assert w["push"] == "${{ github.event_name != 'pull_request' }}"
    assert w["tags"] == "${{ steps.meta.outputs.tags }}" and w["labels"] == "${{ steps.meta.outputs.labels }}"
    assert w["cache-from"] == "type=gha" and w["cache-to"] == "type=gha,mode=max"


@pytest.mark.parametrize(("job_name", "environment", "condition"), [
    ("deploy-staging", "staging", "github.ref == 'refs/heads/main'"),
    ("deploy-production", "production", "startsWith(github.ref, 'refs/tags/v')"),
])
def test_deploy_jobs_call_the_reusable_workflow(cicd, job_name, environment, condition):
    job = jobs(cicd)[job_name]
    assert job["needs"] in ("build", ["build"])
    assert job["if"] == condition
    assert job["uses"] == "./.github/workflows/deploy.yml"
    assert job["with"] == {"environment": environment, "image": "${{ needs.build.outputs.image }}"}
    assert job["secrets"] == "inherit"
    assert job["permissions"] == {"contents": "read", "id-token": "write"}
    others = [name for name, j in jobs(cicd).items() if name not in ("build", "deploy-staging", "deploy-production")]
    for name in others:
        assert "id-token" not in (jobs(cicd)[name].get("permissions") or {}), f"{name} must not get an OIDC token"


def test_reusable_deploy_workflow(deploy):
    call = deploy["on"]["workflow_call"]
    for name in ("environment", "image"):
        assert call["inputs"][name]["required"] is True and call["inputs"][name]["type"] == "string"
    assert deploy["permissions"] == {"contents": "read"}
    job = jobs(deploy)["deploy"]
    assert job["environment"] == "${{ inputs.environment }}"
    assert job["concurrency"]["group"] == "deploy-${{ inputs.environment }}"
    assert job["concurrency"].get("cancel-in-progress") in (False, None)
    assert job["permissions"] == {"contents": "read", "id-token": "write"}
    aws = uses(job, "aws-actions/configure-aws-credentials@")
    assert aws and aws[0]["with"] == {"role-to-assume": "${{ vars.AWS_ROLE_ARN }}", "aws-region": "${{ vars.AWS_REGION }}"}
    deploy_step = [s for s in steps(job) if "deploy.sh" in s.get("run", "")]
    assert deploy_step and deploy_step[0]["env"] == {"IMAGE": "${{ inputs.image }}"} and '"$IMAGE"' in deploy_step[0]["run"]
    smoke = [s for s in steps(job) if "tests/smoke" in s.get("run", "")]
    assert smoke and smoke[0]["env"] == {"REVOSHOP_URL": "${{ vars.APP_URL }}"}
    order = [i for i, s in enumerate(steps(job)) if s in (aws[0], deploy_step[0], smoke[0])]
    assert order == sorted(order), "configure credentials → deploy → smoke test"
