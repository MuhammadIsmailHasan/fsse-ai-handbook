---
title: "Parameter Store & Secrets Manager"
summary: Manage runtime configuration and secrets on AWS — Parameter Store and KMS, path-scoped IAM, Secrets Manager rotation, injection into ECS and EC2, caching in code, rollout of changes and auditing.
type: lesson
source: original
roles: { be: recommended, fe: optional, fs: recommended, ai: recommended, ops: core }
durationMinutes: 150
tags: [aws, ssm, secrets-manager, kms, configuration, security]
---

::part[Learn the Concept]{n="1"}

## 🎯 What you'll learn

- **SSM Parameter Store**: `String`, `StringList`, `SecureString`, standard vs advanced tiers
- **KMS**: AWS managed vs customer managed keys, and what `kms:Decrypt` really grants
- **Hierarchical paths** (`/revoshop/production/...`) and **IAM scoping** by path
- **Secrets Manager**: JSON secrets, **automatic rotation**, RDS-managed passwords, cross-account sharing
- **Getting values into apps**: ECS `secrets`, EC2 fetch scripts, Lambda extension, SDK with caching
- **Rolling out changes**: when running apps see new values
- **Auditing** with CloudTrail and cost comparison

## 🧠 The big idea

Parameter Store is a **labeled filing cabinet**: drawers by application and environment (`/revoshop/production/`), some folders locked with a key (SecureString + KMS), and a guard (IAM) who checks which drawers you may open. Secrets Manager is the **bank's safety-deposit service**: more expensive per box, but it can **change the lock combination on a schedule** (rotation) and tell every authorized person the new one.

## ❓ Why does this matter?

RevoShop's `JWT_SECRET_KEY`, database credentials and Midtrans server key must reach ECS tasks, EC2 hosts and Lambdas without living in Git, images, task definitions or chat. You also need to know **who read them** and how to **change** them without an outage.

## 💥 What happens if we DON'T?

- Secrets as plain `environment` in the task definition → visible to anyone with `ecs:DescribeTaskDefinition`.
- One IAM policy `ssm:GetParameter*` on `*` → the staging task can read production secrets.
- The database password is rotated, but running tasks keep the old one → every new connection fails after the old password expires.
- Parameters named `jwt`, `JWT`, `prod-jwt-new-final` — nobody knows which one is used.

## 📖 How it works, step by step

### 1. Parameter Store

| Type | Use |
|---|---|
| `String` | non-secret config (`APP_ENV`, `WEB_CONCURRENCY`, `API_IMAGE` digest) |
| `StringList` | comma-separated lists |
| `SecureString` | secrets, encrypted with KMS |

| Tier | Limits | Cost |
|---|---|---|
| **Standard** | 10,000 parameters, 4 KB values | no charge for storage (API interactions have limits/pricing for higher throughput) |
| **Advanced** | larger values (8 KB), policies (expiration, notifications) | charged per parameter per month |

```bash
aws ssm put-parameter --name /revoshop/production/JWT_SECRET_KEY --type SecureString --value "$(openssl rand -hex 32)" --overwrite
aws ssm get-parameters-by-path --path /revoshop/production/ --recursive --with-decryption
aws ssm get-parameter-history --name /revoshop/production/JWT_SECRET_KEY   # versions and who changed them
```

Naming convention: `/<app>/<environment>/<NAME>` in uppercase env-var style → trivial mapping to environment variables (exercise 05).

### 2. KMS in one paragraph

SecureString values are encrypted with a KMS key: the **AWS managed key** `alias/aws/ssm` (simple, no key policy to manage) or a **customer managed key** (you control the key policy, can grant cross-account use, rotation settings; costs per key per month plus requests). Reading a SecureString needs **both** `ssm:GetParameter*` on the parameter **and** `kms:Decrypt` on the key — scope `kms:Decrypt` with `kms:ViaService` or to the specific key ARN.

### 3. IAM by path

```json
{
  "Effect": "Allow",
  "Action": ["ssm:GetParameters", "ssm:GetParameter"],
  "Resource": "arn:aws:ssm:ap-southeast-1:123456789012:parameter/revoshop/production/*"
}
```

- Staging roles get `/revoshop/staging/*` only.
- Humans who deploy don't need to *read* production secrets — only CI/roles that inject them.
- Deny `ssm:PutParameter` on production paths for everyone except a small admin group or the IaC pipeline.

### 4. Secrets Manager

| Feature | Detail |
|---|---|
| Secret value | text or JSON (`{"username": …, "password": …}`) |
| Rotation | Lambda-based rotation on a schedule; **RDS/Aurora managed master passwords** rotate without you writing Lambda code |
| Versions | staging labels `AWSCURRENT`, `AWSPREVIOUS`, `AWSPENDING` during rotation |
| Replication | multi-region secrets |
| Cost | per secret per month + per 10,000 API calls |

Rule of thumb: **Secrets Manager** for credentials that should rotate (database passwords, third-party credentials with rotation APIs); **Parameter Store SecureString** for static secrets and configuration (JWT signing key, feature flags).

### 5. Getting values into running code

| Platform | Mechanism | Picks up changes |
|---|---|---|
| **ECS** | task definition `secrets` → env vars at task start (JSON keys supported: `arn:…:secret:name-AbCdEf:password::`) | only **new tasks** — force a new deployment |
| **EC2** | fetch at deploy time (Lab 3 `fetch-env.sh`) into a `600` file | next deploy |
| **Lambda** | AWS Parameters and Secrets Lambda Extension (local cache) or SDK + in-memory cache | after cache TTL |
| **App code (any)** | SDK with a TTL cache and stale fallback (exercise 05) | after TTL |

### 6. Rotating without outages

**Database password rotation (two users)**: keep two database users (or rely on managed rotation's versioning); rotate one while the app uses the other; roll tasks; rotate the other.

**JWT signing key rotation**: sign with the new key, verify with both new and old for longer than the longest token lifetime, then remove the old key.

**Third-party API key (Midtrans)**: create the new key in the provider dashboard → update the parameter → force a new ECS deployment → verify payments → revoke the old key.

### 7. Auditing and hygiene

- CloudTrail records `GetParameter`, `GetSecretValue`, `PutParameter` with the calling principal — useful after incidents (values are not logged).
- Tag parameters/secrets (`Project`, `Env`, `Owner`, `Rotation=90d`).
- Never pass secrets on command lines in shared environments (visible in process lists and shell history) — read them from files, stdin or SDKs.

## ⚖️ Trade-offs

| Choice | ✅ | ❌ |
|---|---|---|
| Parameter Store Standard | simple, practically free for small apps | no built-in rotation; 4 KB values |
| Secrets Manager | rotation, JSON secrets, RDS integration | per-secret monthly cost |
| AWS managed KMS key | zero management | no key policy control or cross-account sharing |
| Customer managed KMS key | control, cross-account, audit per key | cost and key policy responsibility |
| Inject at start (ECS) | no code changes | changes need new tasks |
| Load in code with cache | changes picked up without redeploys | code, caching and failure handling |

## ✅ When to use it / 🚫 When NOT to use it

- ✅ Every environment-specific value that isn't compiled into the image.
- ✅ Secrets Manager for rotating credentials; Parameter Store for the rest.
- 🚫 Don't use either as a general key-value database or for high-frequency reads without caching.
- 🚫 Don't store secrets in `String` parameters "just for now".

## 🏆 Best practices

- [ ] Consistent hierarchy `/app/env/NAME`; environments strictly separated.
- [ ] SecureString (or Secrets Manager) for every secret; `String` only for non-secret config.
- [ ] IAM scoped by path and environment; `kms:Decrypt` scoped by key or `kms:ViaService`.
- [ ] Rotation plan per secret; managed rotation for RDS master passwords.
- [ ] Inject via platform mechanisms; force new deployments after changes (or use TTL caching in code).
- [ ] Least people/roles can read production secrets; CI deploys without humans reading values.
- [ ] Tags and CloudTrail monitoring; parameter history for change tracking.
- [ ] Manage parameter *definitions* in IaC (values from a secure source, not committed).

## 🏭 How it's used in industry

- Parameter Store and Secrets Manager are the default secret stores for AWS-native workloads; HashiCorp Vault is common in multi-cloud or large enterprises.
- Rotation of database credentials is increasingly handled by managed integrations rather than custom scripts.
- Security audits check that task definitions, Lambda environment variables and repositories contain no plain secrets.

## ⚠️ Common mistakes

- Updating a parameter and forgetting running ECS tasks still have the old value.
- Policies granting `ssm:GetParametersByPath` on `/` (every parameter in the account).
- Using the same parameter for staging and production.
- Logging configuration dictionaries at startup (with secrets inside).

:::revoshop
1. **Your parameter tree.** Write the full list for RevoShop: `/revoshop/production/{DATABASE_URL, JWT_SECRET_KEY, MIDTRANS_SERVER_KEY, MIDTRANS_CLIENT_KEY, MIDTRANS_IS_PRODUCTION, WEB_CONCURRENCY}` and the staging equivalents. Mark each as `String` or `SecureString`, and decide whether `DATABASE_URL` stays a full URL in SSM or becomes a Secrets Manager reference to the RDS-managed secret (exercise 05's `resolve_references`).
2. **Midtrans client key.** `MIDTRANS_CLIENT_KEY` is used by frontends to open the Snap popup — is it a secret? What happens if you store it as SecureString anyway?
3. **Rotation drill for JWT.** Flask-JWT-Extended signs with `JWT_SECRET_KEY` in `config/base.py`. Plan a rotation that doesn't log out all users: which setting holds the old key, how long do you keep it (hint: `JWT_REFRESH_TOKEN_EXPIRES` is 7 days in production), and what code change does verification with two keys need (`@jwt.decode_key_loader`)?
4. **Lab 3 → Lab 4.** On EC2 you wrote `.env.production` from SSM at deploy time. On ECS, the task definition's `secrets` do the same at task start. After changing `/revoshop/production/MIDTRANS_SERVER_KEY`, what command makes production pick it up, and how do you verify without printing the key?
5. **Audit.** Find your own `GetParametersByPath` calls from Lab 3 in CloudTrail event history. Which principal made them (the instance role session name contains the instance ID)?
:::

::part[Explain & Design]{n="2"}

## 🗣️ Explain it

Explain the filing cabinet vs safety-deposit service analogy, and why "we changed the parameter" doesn't mean "production uses the new value".

## 📐 Design it

Design RevoShop's configuration and secrets system for staging and production on ECS: stores and types per value, KMS keys, IAM policies for the execution role, the task role, the GitHub OIDC deploy roles and a human admin, rotation procedures for the RDS password and the JWT key, and how a changed value is rolled out and verified.

:::quiz
Show a possible design

| Value | Store | Notes |
|---|---|---|
| RDS master password | Secrets Manager (RDS-managed, rotation on) | used only by the migration task definition |
| `revoshop_app` DB password | Secrets Manager `revoshop/production/db-app` with a rotation Lambda **or** SSM SecureString rotated quarterly with a two-user procedure | injected as `DB_PASSWORD`; app builds `DATABASE_URL` with host from a `String` parameter |
| `JWT_SECRET_KEY` (+ `JWT_PREVIOUS_SECRET_KEY` during rotation) | SSM SecureString | yearly rotation with dual verification for 7+ days |
| `MIDTRANS_SERVER_KEY` | SSM SecureString | rotated on staff changes |
| `MIDTRANS_CLIENT_KEY`, `APP_ENV`, `WEB_CONCURRENCY`, `DB_HOST` | SSM String | not secrets |

- **KMS:** AWS managed `alias/aws/ssm` for simplicity (single account); a customer managed key if staging and production ever split into separate accounts.
- **Execution role (per env):** `ssm:GetParameters` on `/revoshop/<env>/*`, `secretsmanager:GetSecretValue` on `revoshop/<env>/*` secrets, `kms:Decrypt` via SSM/Secrets Manager.
- **Task role:** no SSM/Secrets access (values are injected).
- **GitHub deploy roles:** no read access to secret values; `iam:PassRole` for the execution role; `ecs:RegisterTaskDefinition` referencing ARNs only.
- **Human admin:** `PutParameter` on production paths only via break-glass role with MFA; everyone else read-only on names (`ssm:DescribeParameters`), not values.
- **Rollout:** change value → `aws ecs update-service --force-new-deployment` → wait `services-stable` → verify behavior (e.g. a Midtrans sandbox charge) → check CloudTrail that tasks read the new version (`GetParameters` events after the change).
:::

### 📝 Self-review checklist

- [ ] Environments can't read each other's secrets
- [ ] Deployers don't need to see secret values
- [ ] Every rotation has a no-downtime procedure

::ai-review{task="design"}

::part[Toy Exercise]{n="3"}

:::exercise{path="exercises/m5/w4/05-ssm-config-loader" ai="no-ai" title="Config from Parameter Store and Secrets Manager"}
Load a parameter hierarchy recursively with decryption and pagination into safe environment-style keys, resolve `secretsmanager:` references (fetching each secret once), and cache configuration with a TTL and a bounded stale fallback — tested with moto.
:::

:::hints
- `ssm.get_paginator("get_parameters_by_path")` handles `NextToken` for you.
- `rpartition("#")` splits the secret id from the JSON key even if the ARN contains other characters.
- Store the load time only when a load succeeds.
:::

## ✅ Quick check

:::quiz
An ECS task definition references `/revoshop/production/JWT_SECRET_KEY` as a secret. You update the parameter. When do users see the effect?

Only tasks started **after** the change get the new value — force a new deployment so all tasks are replaced.
:::

:::quiz
Why does reading a SecureString parameter need two permissions?

`ssm:GetParameter` allows reading the parameter, and `kms:Decrypt` on its KMS key allows decrypting the value; without the second, you only get an access error for the decryption.
:::

## 📖 Kamus (glossary)

| Term | Bahasa Indonesia |
|---|---|
| Parameter Store | Penyimpanan parameter |
| SecureString | String terenkripsi |
| KMS key | Kunci enkripsi terkelola |
| Rotation | Rotasi kredensial |
| Injection | Penyuntikan nilai ke aplikasi |
| Audit trail | Jejak audit |

## 📚 Keep learning

- [AWS docs: Parameter Store](https://docs.aws.amazon.com/systems-manager/latest/userguide/systems-manager-parameter-store.html) · [Restricting access by path](https://docs.aws.amazon.com/systems-manager/latest/userguide/sysman-paramstore-access.html)
- [AWS docs: Secrets Manager rotation](https://docs.aws.amazon.com/secretsmanager/latest/userguide/rotating-secrets.html)
- [AWS docs: Parameters and Secrets Lambda Extension](https://docs.aws.amazon.com/secretsmanager/latest/userguide/retrieving-secrets_lambda.html)
