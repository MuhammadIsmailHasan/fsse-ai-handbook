"""Checks for ecs_config.py (registration uses moto). Don't edit this file."""

import boto3
import pytest
from moto import mock_aws

from ecs_config import deployment_configuration, migration_overrides, task_definition

REGION = "ap-southeast-1"
ACCOUNT = "123456789012"
IMAGE = "ghcr.io/sari/revoshop@sha256:" + "c" * 64


def base(**overrides):
    kwargs = dict(
        family="revoshop-api-production",
        image=IMAGE,
        cpu=512,
        memory=1024,
        execution_role_arn=f"arn:aws:iam::{ACCOUNT}:role/revoshop-task-execution",
        task_role_arn=f"arn:aws:iam::{ACCOUNT}:role/revoshop-task",
        region=REGION,
        log_group="/ecs/revoshop-api-production",
        environment={"WEB_CONCURRENCY": "2", "APP_ENV": "production", "REDIS_URL": "redis://revoshop-redis:6379/0"},
        secrets={
            "JWT_SECRET_KEY": f"arn:aws:ssm:{REGION}:{ACCOUNT}:parameter/revoshop/production/JWT_SECRET_KEY",
            "DATABASE_URL": f"arn:aws:ssm:{REGION}:{ACCOUNT}:parameter/revoshop/production/DATABASE_URL",
            "MIDTRANS_SERVER_KEY": f"arn:aws:secretsmanager:{REGION}:{ACCOUNT}:secret:revoshop/midtrans-AbCdEf",
        },
    )
    kwargs.update(overrides)
    return kwargs


@pytest.fixture(autouse=True)
def credentials(monkeypatch):
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "testing")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "testing")


def test_task_definition_shape():
    td = task_definition(**base())
    assert td["family"] == "revoshop-api-production"
    assert td["requiresCompatibilities"] == ["FARGATE"] and td["networkMode"] == "awsvpc"
    assert (td["cpu"], td["memory"]) == ("512", "1024")
    assert td["executionRoleArn"].endswith("role/revoshop-task-execution") and td["taskRoleArn"].endswith("role/revoshop-task")
    assert td["runtimePlatform"] == {"operatingSystemFamily": "LINUX", "cpuArchitecture": "X86_64"}
    assert td["volumes"] == [{"name": "tmp"}]
    (container,) = td["containerDefinitions"]
    assert container["name"] == "api" and container["image"] == IMAGE and container["essential"] is True
    assert container["portMappings"] == [{"name": "http", "containerPort": 5000, "protocol": "tcp"}]
    assert [e["name"] for e in container["environment"]] == ["APP_ENV", "REDIS_URL", "WEB_CONCURRENCY"]
    assert [s["name"] for s in container["secrets"]] == ["DATABASE_URL", "JWT_SECRET_KEY", "MIDTRANS_SERVER_KEY"]
    assert container["readonlyRootFilesystem"] is True
    assert container["mountPoints"] == [{"sourceVolume": "tmp", "containerPath": "/tmp", "readOnly": False}]
    assert container["linuxParameters"] == {"initProcessEnabled": True} and container["stopTimeout"] == 30
    assert container["logConfiguration"] == {
        "logDriver": "awslogs",
        "options": {"awslogs-group": "/ecs/revoshop-api-production", "awslogs-region": REGION, "awslogs-stream-prefix": "api"},
    }
    check = container["healthCheck"]
    assert check["command"][:3] == ["CMD", "python", "-c"] and "http://127.0.0.1:5000/api/v1/health/live" in check["command"][3]
    assert (check["interval"], check["timeout"], check["retries"], check["startPeriod"]) == (15, 5, 3, 30)
    arm = task_definition(**base(architecture="ARM64", container_port=8000, cpu=256, memory=512))
    assert arm["runtimePlatform"]["cpuArchitecture"] == "ARM64"
    assert "127.0.0.1:8000" in arm["containerDefinitions"][0]["healthCheck"]["command"][3]


@pytest.mark.parametrize(
    "overrides",
    [
        {"image": "ghcr.io/sari/revoshop:latest"},
        {"cpu": 256, "memory": 4096},
        {"cpu": 512, "memory": 512},
        {"cpu": 1024, "memory": 3000},
        {"cpu": 300, "memory": 1024},
        {"architecture": "arm64"},
        {"environment": {"POSTGRES_PASSWORD": "x"}},
        {"environment": {"github_token": "x"}},
        {"secrets": {"JWT_SECRET_KEY": "super-secret-literal"}},
        {"secrets": {"JWT_SECRET_KEY": f"arn:aws:ssm:us-east-1:{ACCOUNT}:parameter/revoshop/production/JWT_SECRET_KEY"}},
        {"secrets": {"X": f"arn:aws:s3:::bucket/key"}},
        {"environment": {"DATABASE_URL": "postgresql://x"}},
    ],
)
def test_validation(overrides):
    with pytest.raises(ValueError):
        task_definition(**base(**overrides))


def test_public_keys_allowed_in_environment():
    task_definition(**base(environment={"VAPID_PUBLIC_KEY": "abc"}))


def test_sizes():
    for cpu, memory in [(256, 2048), (512, 4096), (1024, 8192), (2048, 16384), (4096, 30720)]:
        task_definition(**base(cpu=cpu, memory=memory))


def test_overrides_and_deployment_configuration():
    assert migration_overrides() == {"containerOverrides": [{"name": "api", "command": ["flask", "db", "upgrade"]}]}
    assert deployment_configuration() == {"deploymentCircuitBreaker": {"enable": True, "rollback": True}, "maximumPercent": 200, "minimumHealthyPercent": 100}


@mock_aws
def test_registers_with_the_ecs_api():
    ecs = boto3.client("ecs", region_name=REGION)
    response = ecs.register_task_definition(**task_definition(**base()))
    arn = response["taskDefinition"]["taskDefinitionArn"]
    described = ecs.describe_task_definition(taskDefinition=arn)["taskDefinition"]
    assert described["family"] == "revoshop-api-production" and described["revision"] == 1
    container = described["containerDefinitions"][0]
    assert container["image"] == IMAGE
    assert {s["name"] for s in container["secrets"]} == {"DATABASE_URL", "JWT_SECRET_KEY", "MIDTRANS_SERVER_KEY"}
    second = ecs.register_task_definition(**task_definition(**base(image="ghcr.io/sari/revoshop@sha256:" + "d" * 64)))
    assert second["taskDefinition"]["revision"] == 2
