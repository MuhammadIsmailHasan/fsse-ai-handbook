---
title: "Secrets & OIDC to AWS"
summary: Handle credentials professionally — kinds of secrets and their lifecycle, GitHub secrets and their limits, scanning and what to do after a leak, and OIDC login from GitHub Actions to AWS with a tightly scoped trust policy.
type: lesson
source: original
roles: { be: recommended, fe: optional, fs: recommended, ai: recommended, ops: core }
durationMinutes: 150
tags: [secrets, oidc, aws, iam, github-actions, security]
---

::part[Learn the Concept]{n="1"}

## 🎯 What you'll learn

- Kinds of secrets and a secret's **lifecycle**: create, store, deliver, rotate, revoke
- Where secrets should live at each stage (laptop, CI, runtime)
- **GitHub secrets and variables**: scopes, masking, fork behaviour, limits
- **Secret scanning**, push protection, and what to do after a **leak**
- Why **long-lived cloud keys** in CI are dangerous
- How **OIDC federation** works: token claims (`iss`, `aud`, `sub`), IAM identity provider, role, **trust policy**
- **Least-privilege** permission policies for deploy roles
- Runtime secrets on AWS: **SSM Parameter Store** and **Secrets Manager** (preview of Weeks 3–4)

## 🔤 Key words

| Word | In simple words | Bahasa Indonesia |
|---|---|---|
| **Secret** | A value that gives access and must stay hidden (password, API key) | Rahasia / kredensial |
| **Rotation** | Replacing a secret with a new one on a schedule or after a leak | Penggantian berkala |
| **Revoke** | Making an existing credential stop working | Mencabut akses |
| **Masking** | GitHub replacing a secret with `***` in the logs | Menyensor di log |
| **IAM role** | An identity in AWS that something can borrow temporarily | Identitas yang dipinjam |
| **OIDC** | A standard where GitHub proves who the job is, and AWS hands out a short-lived pass | Login lewat token bertanda tangan |
| **Claim** | One fact inside that signed token (`sub` = which repo and environment) | Isi keterangan token |
| **Trust policy** | The AWS rule saying *who* may borrow a role | Aturan siapa yang boleh |
| **Permission policy** | The AWS rule saying *what* that role may do | Aturan boleh apa saja |
| **Least privilege** | Give only the access the job really needs | Hak seminimal mungkin |

## 🧠 The big idea

A long-lived access key is a **house key you copy and hand to the cleaner**: it works forever, you don't know how many copies exist, and changing the locks is painful.

OIDC is a **hotel keycard issued at the front desk**: the desk checks your ID (a signed token saying "I'm the `production` environment of `you/revoshop`"), gives you a card that opens only your room, and the card stops working in an hour.

## ❓ Why it matters

Your pipeline must push images and deploy to AWS. Leaked AWS keys are found and abused by bots within minutes of reaching a public repository — often for crypto mining, which creates a large bill fast. Most break-ins in small projects are not clever attacks; they are credentials in the wrong place.

Done carelessly:

- `AWS_SECRET_ACCESS_KEY` sits in a GitHub secret, never rotated, belonging to an admin IAM user.
- A debug step `env | sort` prints a token GitHub's masking doesn't recognise.
- The `.env` with Midtrans server keys is committed once and "deleted" in the next commit — it stays in Git history forever.
- A trust policy of `"repo:you/*"` lets *any* of your repositories — including an old experiment — deploy to production.

## 📖 Step by step

### 1. Kinds of secrets

| Kind | RevoShop examples | Rotation |
|---|---|---|
| Signing keys | `JWT_SECRET_KEY` | rotate carefully (it invalidates tokens) or accept two keys during the switch |
| Database credentials | `POSTGRES_PASSWORD` | on a schedule; managed rotation with Secrets Manager |
| Third-party API keys | `MIDTRANS_SERVER_KEY` | when staff change or after a leak |
| Deploy credentials | SSH deploy key, cloud credentials | prefer short-lived (OIDC) |
| Encryption keys | KMS keys | managed by the cloud KMS |

Not secrets (they can be plain variables): URLs, region names, role ARNs, and the Midtrans **client** key — that one runs in browsers.

### 2. Where secrets live

```mermaid
flowchart LR
    subgraph Dev["Laptop"]
      E[".env (gitignored)<br/>or a password manager"]
    end
    subgraph CI["GitHub Actions"]
      GS["environment secrets"]
      OIDC["OIDC token → temporary AWS credentials"]
    end
    subgraph Run["Runtime on AWS"]
      SM["Secrets Manager / SSM Parameter Store"]
      TASK["task role / instance role"]
    end
    E -. never .-> Git[(Git)]
    OIDC --> AWS[(AWS APIs)]
    TASK --> SM
```

Rules: never in Git, images, build args, logs, URLs, tickets or chat. At runtime the app should get secrets from the platform (environment variables filled from Secrets Manager/SSM, or files) using an **IAM role** — not a key baked into the server.

### 3. GitHub secrets and variables

| Level | Visible to |
|---|---|
| Repository secrets | all workflows in the repo (not pull requests from forks) |
| **Environment secrets** | only jobs that declare that `environment:` and pass its protection rules |
| Organization secrets | selected repositories |
| Variables (`vars.*`) | non-secret config, shown in logs |

- Values are **masked** in logs when printed exactly — but not when transformed (base64, a substring, inside JSON). So don't print them at all.
- Secrets are not given to workflows triggered by pull requests from **forks**.
- Reusable workflows get secrets via `secrets: inherit` or an explicit `secrets:` mapping.

### 4. Scanning and leaks

- Turn on **secret scanning** and **push protection** (GitHub blocks a push containing a recognised secret format).
- Run **gitleaks** locally (as a pre-commit hook) and in CI for patterns GitHub doesn't know.

**If a secret leaks**, in this order:

1. **Revoke or rotate it immediately** at the provider (deactivate the AWS key, new Midtrans key, new DB password).
2. Check the provider's logs for misuse (CloudTrail, the Midtrans dashboard).
3. Remove it from history (`git filter-repo`) and force-push — *after* rotating; assume it's already copied.
4. Write down what happened and add a control that stops it happening again.

Treat it like a lost ATM card: block the card first, argue about how it was lost later.

### 5. OIDC federation, step by step

```mermaid
sequenceDiagram
    participant J as GitHub Actions job (id-token: write)
    participant G as GitHub OIDC provider
    participant S as AWS STS
    participant R as IAM role (trust policy)
    J->>G: request ID token (audience sts.amazonaws.com)
    G-->>J: signed JWT: iss, aud, sub=repo:you/revoshop:environment:production, …
    J->>S: AssumeRoleWithWebIdentity(role ARN, JWT)
    S->>S: verify signature with GitHub's public keys
    S->>R: evaluate trust policy conditions (aud, sub)
    R-->>S: allowed
    S-->>J: temporary credentials (expire in ~1 hour)
    J->>J: aws ecr / ecs / ssm … with those credentials
```

**One-time AWS setup** (Week 3 does it in the console, Week 7 in Terraform):

1. IAM → Identity providers → add an **OpenID Connect** provider `https://token.actions.githubusercontent.com` with audience `sts.amazonaws.com`.
2. Create a **role** with this trust policy:

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": { "Federated": "arn:aws:iam::123456789012:oidc-provider/token.actions.githubusercontent.com" },
    "Action": "sts:AssumeRoleWithWebIdentity",
    "Condition": {
      "StringEquals": { "token.actions.githubusercontent.com:aud": "sts.amazonaws.com" },
      "StringLike": { "token.actions.githubusercontent.com:sub": "repo:you/revoshop:environment:production" }
    }
  }]
}
```

3. Attach a **least-privilege permission policy** (only what deploying needs: push to one ECR repository, update one ECS service, read specific SSM parameters).
4. In the workflow:

```yaml
permissions:
  id-token: write
  contents: read
steps:
  - uses: aws-actions/configure-aws-credentials@cbe3b392738ccf3f987d68400dafcf4b0624a56c # v6.2.4
    with:
      role-to-assume: ${{ vars.AWS_ROLE_ARN }}
      aws-region: ap-southeast-3          # Jakarta
  - run: aws sts get-caller-identity       # prove it works
```

**The `sub` claim decides who gets in** — it's the name on the guest list.

| `sub` format | When |
|---|---|
| `repo:OWNER/REPO:environment:NAME` | the job uses `environment: NAME` (best for deploy roles) |
| `repo:OWNER/REPO:ref:refs/heads/BRANCH` | a job without an environment, on a branch |
| `repo:OWNER/REPO:ref:refs/tags/TAG` | tag builds |
| `repo:OWNER/REPO:pull_request` | PR workflows — **never** trust these for deploy roles |

Use **separate roles** per environment (`revoshop-deploy-staging`, `revoshop-deploy-production`), each with its own permissions.

### 6. A least-privilege permission policy

```json
{
  "Version": "2012-10-17",
  "Statement": [
    { "Effect": "Allow", "Action": "ecr:GetAuthorizationToken", "Resource": "*" },
    { "Effect": "Allow",
      "Action": ["ecr:BatchCheckLayerAvailability", "ecr:InitiateLayerUpload", "ecr:UploadLayerPart", "ecr:CompleteLayerUpload", "ecr:PutImage"],
      "Resource": "arn:aws:ecr:ap-southeast-3:123456789012:repository/revoshop-api" },
    { "Effect": "Allow", "Action": ["ecs:UpdateService", "ecs:DescribeServices"],
      "Resource": "arn:aws:ecs:ap-southeast-3:123456789012:service/revoshop/api-production" }
  ]
}
```

Start narrow, like giving a delivery driver the gate code but not the house keys. When a deploy fails with `AccessDenied`, read the denied action in the error (or CloudTrail) and add exactly that.

### Choosing your setup

- ✅ OIDC for every CI → cloud connection that supports it (AWS, GCP, Azure, many SaaS tools).
- ✅ Environment secrets for things OIDC can't replace (SSH keys, third-party API keys).
- 🚫 Never IAM users with access keys for pipelines when OIDC is possible.
- 🚫 Never `sub` wildcards across repositories, and never `pull_request` subjects on deploy roles.
- For runtime secrets, **SSM Parameter Store** (SecureString) is cheap and simple; **Secrets Manager** costs per secret but adds automatic rotation and finer audit.

## ⚠️ Common mistakes

- Forgetting `permissions: id-token: write` → "Credentials could not be loaded".
- A trust policy using `StringEquals` with a wildcard `sub` (wildcards need `StringLike`) — or `StringLike` with `*` everywhere.
- A job with `environment: production` but a trust policy expecting `ref:refs/heads/main` (using an environment changes the `sub`).
- Rotating a leaked secret *after* cleaning history — the window stays open the whole time.

## 🏆 Best practices

- [ ] Keep a list of secrets: owner, location and rotation plan for each.
- [ ] Nothing secret in Git, images, build args, logs, or client-side code (`NEXT_PUBLIC_`).
- [ ] Environment-scoped secrets; different values per environment.
- [ ] Secret scanning + push protection + gitleaks; a pre-commit hook locally.
- [ ] Leak response: **rotate first**, then investigate and clean history.
- [ ] OIDC to AWS with `aud` = `sts.amazonaws.com` and `sub` pinned to repo + environment.
- [ ] One role per environment, least privilege; `id-token: write` only in deploy jobs.
- [ ] At runtime use IAM roles + Secrets Manager/SSM, never keys on disk.
- [ ] Review CloudTrail for what each role did; alert on unusual use.

:::revoshop
1. **Good news first.** `git log --all --oneline -- .env .env.docker` returns nothing in your repo, and `git check-ignore -v .env .env.docker` confirms both are ignored — your real keys were never committed. Keep it that way: add a pre-commit `gitleaks protect --staged` hook and turn on push protection in your personal copy.
2. **Scan history anyway.** Run `gitleaks detect --source . --redact` on the repository. The Midtrans examples use `SB-Mid-server-xxxx…` placeholders — confirm nothing real was ever committed in the Postman collections (`postman/`) or docs.
3. **Inventory.** List every secret RevoShop uses (`JWT_SECRET_KEY`, `POSTGRES_PASSWORD`, `MIDTRANS_SERVER_KEY`, …) and mark which ones are *not* secrets (`MIDTRANS_CLIENT_KEY` is used by clients; `MIDTRANS_IS_PRODUCTION` is config). For each secret: where it lives locally, in CI, in staging and in production.
4. **The silent fallback.** `config/base.py` still has `JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'super-secret-key-change-in-production')`. After W1·05 production refuses to start without a real key — but what about a `development` container accidentally exposed to the internet? Would you remove the default completely?
5. **Rotation drill.** Plan how you would rotate `JWT_SECRET_KEY` without logging every user out at once (hint: sign new tokens with the new key but keep verifying with the old one during a transition window — Flask-JWT-Extended lets you choose the verification key per token with `@jwt.decode_key_loader`).
6. **Your first trust policy.** With the exercise's `trust_policy()`, generate RevoShop's staging and production policies for your personal repository name, and write down the `sub` values your jobs will present.
:::

::part[Explain & Design]{n="2"}

## 🗣️ Explain it

Explain the house-key vs hotel-keycard analogy, and why the `sub` condition is the most important line in the trust policy.

## 📐 Design it

Design RevoShop's secrets plan: list every secret, where it lives for local/CI/staging/production, who or what may read it, and how it's rotated. Then design the IAM roles for GitHub Actions (names, trust `sub`, permissions) for staging and production deploys to ECS, with images in ECR and secrets in SSM.

:::quiz
Show a possible plan

| Secret | Local | CI | Staging / Production runtime | Rotation |
|---|---|---|---|---|
| `JWT_SECRET_KEY` | `.env` (random per developer) | a test value in the workflow env | SSM SecureString `/revoshop/{env}/jwt_secret_key` → ECS task secret | yearly or after an incident; accept the previous key during the switch |
| DB password | Compose default | service container default | Secrets Manager (RDS-managed rotation) | automatic |
| `MIDTRANS_SERVER_KEY` | sandbox key in `.env` | not needed (mocked) | SSM per environment (sandbox vs production) | on staff change / leak |
| Deploy credentials | — | **OIDC roles** (no stored keys) | — | not needed (temporary) |
| SSH key (EC2 phase only) | your key | environment secret `DEPLOY_SSH_KEY` | `authorized_keys` for a `deploy` user only | when the EC2 phase ends |

**Roles**

- `revoshop-gha-staging` · trust `sub = repo:you/revoshop:environment:staging` · may push to ECR `revoshop-api`, call `ecs:UpdateService`/`DescribeServices` on `api-staging`, `ecs:RunTask` for the migrate task definition, and `iam:PassRole` limited to the staging task roles.
- `revoshop-gha-production` · trust `sub = repo:you/revoshop:environment:production` · the same actions on production resources only; the `production` GitHub environment requires a reviewer and allows only `v*` tags.
- The ECS **task execution role** reads `/revoshop/{env}/*` SSM parameters; the **task role** has only what the app needs while running (for example the S3 bucket for product images).
:::

### 📝 Self-review checklist

- [ ] No long-lived cloud keys anywhere
- [ ] Separate roles and values for staging and production
- [ ] A rotation plan per secret

::ai-review{task="design"}

::part[Toy Exercise]{n="3"}

:::exercise{path="exercises/m5/w2/04-oidc-trust-policy" ai="no-ai" title="Build and test a GitHub OIDC trust policy"}
Generate an IAM trust policy scoped to a repository's environments and branches (rejecting wildcards), then write a small evaluator for `StringEquals`/`StringLike` conditions that proves forks, other branches and pull requests can't assume the role.
:::

:::hints
- Turn a `StringLike` pattern into a regex by escaping everything except `*` and `?`.
- The principal must match the token issuer's host.
- An unknown condition operator must deny, not allow.
:::

## ✅ Quick check

:::quiz
A job uses `environment: staging`. Which `sub` will its OIDC token have?

`repo:OWNER/REPO:environment:staging` — the environment replaces the ref in the subject, so the trust policy must allow exactly that subject.
:::

:::quiz
You find `AKIA…` in a public commit from last week. What's your first action?

Deactivate or rotate the key in AWS immediately, then check CloudTrail and the bill for misuse, then clean the history and add prevention (push protection, OIDC).
:::

## 📚 Keep learning

- [GitHub docs: Configuring OpenID Connect in Amazon Web Services](https://docs.github.com/en/actions/security-for-github-actions/security-hardening-your-deployments/configuring-openid-connect-in-amazon-web-services)
- [aws-actions/configure-aws-credentials](https://github.com/aws-actions/configure-aws-credentials)
- [GitHub docs: Secret scanning and push protection](https://docs.github.com/en/code-security/secret-scanning)
- [gitleaks](https://github.com/gitleaks/gitleaks)
