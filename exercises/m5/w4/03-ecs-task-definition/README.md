# M5 · W4 · 03 — ECS Fargate task definition for RevoShop

> 🚫🤖 **No-AI** · ⏱️ ~2 h · AWS is mocked with **moto**

A task definition is to ECS what `compose.yaml` is to Docker Compose — with more ways to get production details wrong. Generate RevoShop's task definition in `ecs_config.py` so every setting is reviewed, validated and tested, then register it (against moto).

## 1. `task_definition(**kwargs) -> dict` (keyword arguments for `ecs.register_task_definition`)
Arguments: `family`, `image`, `cpu`, `memory`, `execution_role_arn`, `task_role_arn`, `region`, `log_group`, `environment: dict[str, str]`, `secrets: dict[str, str]` (name → ARN), `container_port=5000`, `architecture="X86_64"`.

The result must contain:
- `family`, `requiresCompatibilities: ["FARGATE"]`, `networkMode: "awsvpc"`, `cpu`/`memory` as **strings**, `executionRoleArn`, `taskRoleArn`
- `runtimePlatform: {"operatingSystemFamily": "LINUX", "cpuArchitecture": architecture}`
- `volumes: [{"name": "tmp"}]`
- one container definition named **`api`**:
  - `image`, `essential: True`
  - `portMappings: [{"name": "http", "containerPort": port, "protocol": "tcp"}]`
  - `environment`: list of `{"name", "value"}` sorted by name
  - `secrets`: list of `{"name", "valueFrom"}` sorted by name
  - `readonlyRootFilesystem: True` and `mountPoints: [{"sourceVolume": "tmp", "containerPath": "/tmp", "readOnly": False}]`
  - `linuxParameters: {"initProcessEnabled": True}`, `stopTimeout: 30`
  - `logConfiguration`: driver `awslogs` with options `awslogs-group`, `awslogs-region`, `awslogs-stream-prefix: "api"`
  - `healthCheck`: `command` `["CMD", "python", "-c", <script>]` where the script requests `http://127.0.0.1:<port>/api/v1/health/live`; `interval: 15`, `timeout: 5`, `retries: 3`, `startPeriod: 30`

Validation (`ValueError`):
- `image` must be a digest reference (`@sha256:` + 64 hex)
- `(cpu, memory)` must be a valid Fargate combination: 256 → 512/1024/2048 · 512 → 1024…4096 · 1024 → 2048…8192 · 2048 → 4096…16384 · 4096 → 8192…30720 (MiB, multiples of **1024** except the 256-CPU sizes)
- `architecture` in `X86_64` / `ARM64`
- no **secret-looking names** in `environment` (`SECRET`, `PASSWORD`, `TOKEN`, `KEY` — but not `_PUBLIC_KEY`)
- every `secrets` value must be an SSM parameter ARN (`arn:aws:ssm:<region>:<account>:parameter/…`) or a Secrets Manager ARN (`arn:aws:secretsmanager:<region>:<account>:secret:…`) **in the same region**
- no name may appear in both `environment` and `secrets`

## 2. `migration_overrides() -> dict`
`{"containerOverrides": [{"name": "api", "command": ["flask", "db", "upgrade"]}]}` — for `ecs.run_task` so migrations run as a one-off task with the **same** task definition.

## 3. `deployment_configuration() -> dict`
`{"deploymentCircuitBreaker": {"enable": True, "rollback": True}, "maximumPercent": 200, "minimumHealthyPercent": 100}` — new tasks start before old ones stop, and a failing deployment rolls back automatically.

```bash
cd exercises
uv run pytest m5/w4/03-ecs-task-definition
```
