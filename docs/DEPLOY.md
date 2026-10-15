# Deploying the handbook and the dev box

Two separate pieces of AWS, each in its own folder under `infra/`. They do not
depend on each other, so you can build one and skip the other.

| Folder | What it gives you | Rough cost |
|---|---|---|
| `infra/handbook-site` | The handbook on an HTTPS URL (S3 + CloudFront), readable from your phone or any laptop | **~$1/month** for this size |
| `infra/dev-box` | One small EC2 box running Postgres + Redis, so you do not start Docker on the Mac | **~$13/month** running all the time, **~$3/month** if you stop it when you are not studying |

> **The honest version of the Docker question.** Docker is needed by about 10 of
> the 494 exercises — the ones in M2 W2/W4/W6, M5 W1 and CareerPilot Phase 2 that
> use a database. Everything else is `pytest` or `npm`, and the handbook app
> itself never needed Docker. So the dev box removes a real annoyance, not a
> wall. If you only want the database to stop being your problem, a free managed
> Postgres (Neon, Supabase) plus Upstash Redis does the same job for $0 and
> nothing to patch. The dev box is still worth it as practice for Module 5 W7 and
> CareerPilot Phase 5, which is why it is here.

## Before you start

You need these on the Mac. **I did not install or run any of them, and I have
not created anything in AWS** — no account, no credentials, no `apply`:

```bash
brew install terraform awscli
brew install --cask session-manager-plugin   # only for `./scripts/devbox.sh shell`
aws configure                                # your own AWS account and keys
```

Also note: nothing here has been run through `terraform validate` or
`terraform plan`, because Terraform is not installed on this machine. Expect the
first `plan` to surface a typo or two; that is normal and the error messages are
precise.

### About the free tier

AWS restructured the free tier in July 2025: new accounts get a credit balance
instead of the old 12-month per-service allowances, so what your account
includes depends on when you opened it. Check your own numbers in
**Billing and Cost Management → Free tier** rather than trusting any guide.

Either way the site is cheap enough that it barely matters: at full price this
size costs on the order of a dollar a month. The dev box is the part that can
actually surprise you, because a `t4g.small` running all month is not free under
any version of the tier. Set a budget alarm before the first `apply`:
**Billing → Budgets → Create budget → Zero spend or $5 monthly**, about five
minutes in the console.

### About regions

The site defaults to `ap-southeast-1` (Singapore) because every account can use
it immediately. The dev box defaults to `ap-southeast-3` (Jakarta) for lower
latency, and **Jakarta is an "opt-in" region**: enable it first under
**Account → AWS Regions**, or `apply` fails with an auth error. Enabling is free.

For the site the bucket region hardly matters anyway — CloudFront serves readers
from its own edge locations, so the bucket is only touched on upload.

## Part 1 — the handbook on a URL

```bash
cd infra/handbook-site
cp terraform.tfvars.example terraform.tfvars
$EDITOR terraform.tfvars        # pick a globally unique bucket name + a password

terraform init
terraform plan                  # read this before saying yes
terraform apply
```

`apply` takes about 5 minutes, almost all of it CloudFront. Then:

```bash
cd ../..
terraform -chdir=infra/handbook-site output deploy_env   # paste into .env
npm run deploy
```

`npm run deploy` runs `content:check`, builds, uploads and clears the CloudFront
cache. The URL is in the `url` output.

What the config does and why:

- **The bucket is private.** Only CloudFront can read it, through an Origin
  Access Control. There is no public bucket to get wrong.
- **Unknown paths return `index.html` with a 200.** The app uses
  `createBrowserRouter`, so without this a refresh on
  `/modules/m7/w4/03-retrieval` would show an error page.
- **A password prompt at the edge.** `basic_auth_password` turns on a tiny
  CloudFront Function that asks for a username and password. Set it to `""` to
  publish openly. The password sits in plain text in Terraform state and in the
  deployed function, so treat it as a gate, not a secret.
- **Hashed assets cache for a year, `index.html` never caches.** That is why a
  deploy is visible immediately but repeat visits are nearly free.

### A custom domain (optional)

The free URL is `https://d111111abcdef8.cloudfront.net`. For your own domain you
need an ACM certificate **in us-east-1** (CloudFront only reads certificates from
there), then add to the distribution:

```hcl
aliases = ["handbook.example.com"]

viewer_certificate {
  acm_certificate_arn = aws_acm_certificate.site.arn
  ssl_support_method  = "sni-only"
  minimum_protocol_version = "TLSv1.2_2021"
}
```

…and a DNS record pointing at the distribution. Ask me when you want it.

## Part 2 — the dev box

```bash
curl -s https://checkip.amazonaws.com     # your current address

cd infra/dev-box
cp terraform.tfvars.example terraform.tfvars
$EDITOR terraform.tfvars                  # allowed_cidr = "<that address>/32"

terraform init
terraform plan
terraform apply
```

Then point the exercises at it:

```bash
cd ../..
./scripts/devbox.sh env        # prints DATABASE_URL and REDIS_URL
$EDITOR .env                   # paste them in
```

Daily use:

```bash
./scripts/devbox.sh start      # before studying, ~40 seconds
./scripts/devbox.sh status
./scripts/devbox.sh stop       # after studying — this is the cost control
./scripts/devbox.sh shell      # a shell on the box, no SSH key needed
./scripts/devbox.sh logs
```

What the config does and why:

- **Only your address can connect.** Postgres (5491), Redis (6391) and SSH are
  open to `allowed_cidr` and nothing else. Terraform refuses `0.0.0.0/0`
  outright. A home connection changes address every few days, so when a
  connection hangs, re-run `curl checkip`, update `terraform.tfvars` and
  `terraform apply`.
- **Same ports as local.** 5491 and 6391, as in the rest of the repo, so only
  the host changes in `.env` when you switch between local Docker and the box.
- **Databases live on a separate disk** (`/data`, its own EBS volume marked
  `prevent_destroy`). Rebuilding or replacing the instance keeps your data, and
  `terraform destroy` will refuse until you remove that protection on purpose.
- **A stable address.** An Elastic IP, free while the instance is attached, so
  stopping the box overnight does not change your `.env`.
- **No SSH by default.** Session Manager gives you a shell through the AWS API,
  so there is no key to lose and port 22 stays shut. Set
  `ssh_public_key_path` if you prefer plain `ssh`.
- **Passwords are generated** by Terraform and kept in its state file. They are
  for practice data only. Never reuse them anywhere real.

### Latency, which is the real trade-off

Every query now crosses the internet. From Indonesia to Jakarta
(`ap-southeast-3`) expect roughly 10–30 ms per round trip, against under 1 ms to
local Docker. A test suite doing hundreds of small queries will feel slower.
That is the price of not running Docker, and it is why `region` defaults to
Jakarta rather than a US region.

## Turning it all off

```bash
# handbook
terraform -chdir=infra/handbook-site destroy

# dev box — the data volume is protected on purpose
terraform -chdir=infra/dev-box destroy
```

The dev box `destroy` stops at `aws_ebs_volume.data`. That is deliberate. If you
really want the databases gone, delete the `lifecycle { prevent_destroy }` block
first, or detach and keep the volume.

## What is NOT set up

- **No CI/CD.** Deploys are manual (`npm run deploy`), matching the repo's
  "never push" rule. A GitHub Actions workflow with OIDC is a small addition —
  M5 W2 lesson 02 is the lesson for it.
- **No remote Terraform state.** State is a local file per folder, gitignored.
  Fine for one person on one Mac; M5 W7 covers the S3 + DynamoDB version.
- **No backups of the dev box data.** It is practice data. Add an EBS snapshot
  schedule (AWS Backup) if that changes.
- **No RDS or ElastiCache.** Containers on one box are about a fifth of the
  price and enough for exercises. The managed version is CareerPilot Phase 5.
