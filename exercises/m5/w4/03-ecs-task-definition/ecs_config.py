"""ECS task definition for RevoShop. See README.md."""


def task_definition(*, family, image, cpu, memory, execution_role_arn, task_role_arn, region, log_group, environment, secrets, container_port=5000, architecture="X86_64") -> dict:
    raise NotImplementedError


def migration_overrides() -> dict:
    raise NotImplementedError


def deployment_configuration() -> dict:
    raise NotImplementedError
