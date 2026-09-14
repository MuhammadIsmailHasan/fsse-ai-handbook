---
title: "Week 3 Placement Check"
summary: AWS account safety and billing, IAM policy evaluation, regions and VPC design, EC2, RDS, S3 with CloudFront, and mapping AWS services to GCP and Azure — check what you can skip.
type: placement-check
source: original
roles: { be: recommended, fe: optional, fs: recommended, ai: recommended, ops: core }
durationMinutes: 20
tags: [placement, aws, iam, vpc, ec2, rds, s3]
---

::::placement{id="modules/m5/w3"}
:::quiz
1 · You just created an AWS account. What are the first four things you do, before launching anything?

Enable **MFA on the root user** (and stop using root), create an **admin IAM identity with MFA** for daily work (no access keys; use `aws login` for the CLI), set up **budgets/alerts** (and check the Free Tier plan status), and set **alternate contacts**/billing preferences. Then pick a region deliberately.
:::

:::quiz
2 · A policy allows `s3:*` on a bucket; another policy attached to the same role denies `s3:DeleteObject`. Can the role delete objects?

No. An explicit **Deny** always wins over any Allow. Without any matching Allow the result is an implicit deny.
:::

:::quiz
3 · Why is a NAT gateway a common "surprise bill" for learners, and what are two ways to avoid it for a small app?

It's charged per hour (tens of USD per month) plus per GB processed, even when idle. Put small workloads that need internet access in **public subnets** with security groups (or give Fargate tasks public IPs), and use **VPC gateway endpoints** (S3, DynamoDB are free) for AWS traffic.
:::

:::quiz
4 · Security group vs network ACL: which is stateful, and which do you normally use?

**Security groups** are stateful (return traffic is allowed automatically) and attach to network interfaces; you use them for almost everything. **NACLs** are stateless subnet-level filters, used rarely for coarse deny rules.
:::

:::quiz
5 · Your RDS instance should only accept connections from your API servers. How do you express that?

Put RDS in private subnets with **Public access: No**, and allow inbound 5432 on its security group **from the API's security group** (a security-group reference, not an IP range). Require TLS (`sslmode=verify-full`).
:::

:::quiz
6 · How should browsers get product images from a private S3 bucket, and how should sellers upload them?

Serve through **CloudFront with Origin Access Control** (bucket stays private, CDN caches). Uploads go **directly to S3 with a short-lived presigned POST** that limits key, content type and size — the API never streams the file.
:::
::::

:::tip[Scoring yourself]
Pass with **5 of 6**. Even if you pass, read lesson 01 — the free plan's rules (and account closure) matter before you click anything.
:::
