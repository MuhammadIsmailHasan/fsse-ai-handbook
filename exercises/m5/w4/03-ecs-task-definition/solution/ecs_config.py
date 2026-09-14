"""ECS task definition for RevoShop. See README.md."""

import re

DIGEST = re.compile(r"^[a-z0-9./:-]+@sha256:[a-f0-9]{64}$")
SECRET_WORDS = ("SECRET", "PASSWORD", "TOKEN", "KEY")
FARGATE_MEMORY = {
    256: {512, 1024, 2048},
    512: set(range(1024, 4097, 1024)),
    1024: set(range(2048, 8193, 1024)),
    2048: set(range(4096, 16385, 1024)),
    4096: set(range(8192, 30721, 1024)),
}


def _secret_like(name: str) -> bool:
    upper = name.upper()
    return any(word in upper for word in SECRET_WORDS) and not upper.endswith("_PUBLIC_KEY")


def _valid_secret_arn(arn: str, region: str) -> bool:
    return bool(
        re.fullmatch(rf"arn:aws:ssm:{re.escape(region)}:\d{{12}}:parameter/.+", arn)
        or re.fullmatch(rf"arn:aws:secretsmanager:{re.escape(region)}:\d{{12}}:secret:.+", arn)
    )


def task_definition(*, family, image, cpu, memory, execution_role_arn, task_role_arn, region, log_group, environment, secrets, container_port=5000, architecture="X86_64") -> dict:
    if not DIGEST.match(image):
        raise ValueError("image must be referenced by digest")
    if memory not in FARGATE_MEMORY.get(cpu, set()):
        raise ValueError(f"invalid Fargate size cpu={cpu} memory={memory}")
    if architecture not in ("X86_64", "ARM64"):
        raise ValueError("architecture must be X86_64 or ARM64")
    leaked = sorted(name for name in environment if _secret_like(name))
    if leaked:
        raise ValueError(f"secrets must not be plain environment variables: {', '.join(leaked)}")
    for name, arn in secrets.items():
        if not _valid_secret_arn(arn, region):
            raise ValueError(f"{name}: expected an SSM parameter or Secrets Manager ARN in {region}")
    duplicated = set(environment) & set(secrets)
    if duplicated:
        raise ValueError(f"defined twice: {', '.join(sorted(duplicated))}")

    health_script = f"import urllib.request; urllib.request.urlopen('http://127.0.0.1:{container_port}/api/v1/health/live', timeout=3)"
    return {
        "family": family,
        "requiresCompatibilities": ["FARGATE"],
        "networkMode": "awsvpc",
        "cpu": str(cpu),
        "memory": str(memory),
        "executionRoleArn": execution_role_arn,  # pulls the image, reads secrets, writes logs
        "taskRoleArn": task_role_arn,  # what the application itself may call
        "runtimePlatform": {"operatingSystemFamily": "LINUX", "cpuArchitecture": architecture},
        "volumes": [{"name": "tmp"}],
        "containerDefinitions": [
            {
                "name": "api",
                "image": image,
                "essential": True,
                "portMappings": [{"name": "http", "containerPort": container_port, "protocol": "tcp"}],
                "environment": [{"name": k, "value": v} for k, v in sorted(environment.items())],
                "secrets": [{"name": k, "valueFrom": v} for k, v in sorted(secrets.items())],
                "readonlyRootFilesystem": True,
                "mountPoints": [{"sourceVolume": "tmp", "containerPath": "/tmp", "readOnly": False}],
                "linuxParameters": {"initProcessEnabled": True},
                "stopTimeout": 30,
                "logConfiguration": {
                    "logDriver": "awslogs",
                    "options": {"awslogs-group": log_group, "awslogs-region": region, "awslogs-stream-prefix": "api"},
                },
                "healthCheck": {
                    "command": ["CMD", "python", "-c", health_script],
                    "interval": 15,
                    "timeout": 5,
                    "retries": 3,
                    "startPeriod": 30,
                },
            }
        ],
    }


def migration_overrides() -> dict:
    return {"containerOverrides": [{"name": "api", "command": ["flask", "db", "upgrade"]}]}


def deployment_configuration() -> dict:
    return {"deploymentCircuitBreaker": {"enable": True, "rollback": True}, "maximumPercent": 200, "minimumHealthyPercent": 100}
