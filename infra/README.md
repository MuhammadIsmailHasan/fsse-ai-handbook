# infra/

Terraform for the two optional remote pieces. Full runbook: [`../docs/DEPLOY.md`](../docs/DEPLOY.md).

| Folder | Stack |
|---|---|
| `handbook-site/` | Private S3 bucket + CloudFront, with an SPA fallback and an optional password prompt. Deployed with `npm run deploy`. |
| `dev-box/` | One `t4g.small` running Postgres + Redis on a separate data disk, reachable only from your own address. Driven with `npm run devbox -- start\|stop\|env\|shell`. |

Nothing here runs automatically, and nothing here has been applied. Each folder
keeps its own local state file, and `terraform.tfvars` plus every `.tfstate` is
gitignored — the state holds generated practice passwords.

Read these next to Module 5 W7 (`content/modules/m5/w7/01-terraform-basics.md`
and `02-terraform-for-careerpilot.md`): this is the same shape, smaller.
