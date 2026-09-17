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
Answer from memory. If a word is new to you, that's a sign to study the lesson.

:::quiz
1 · You just created an AWS account. What are the first four things you do, before launching anything?

Turn on **MFA for the root user** and then stop using root; create an **admin IAM identity with MFA** for daily work (no access keys — use `aws login` for the command line); set up **budgets and alerts** and check which free plan you are on; and fill in **alternate contacts** plus billing preferences. Only then pick a region, on purpose.
:::

:::quiz
2 · A policy allows `s3:*` on a bucket; another policy attached to the same role denies `s3:DeleteObject`. Can the role delete objects?

No. An explicit **Deny** always beats any Allow — like a "do not enter" sign overruling a general permission. And with no matching Allow at all, the answer is still no.
:::

:::quiz
3 · Why is a NAT gateway a common "surprise bill" for learners, and what are two ways to avoid it for a small app?

You pay by the hour (tens of dollars a month) plus for every GB, even when nothing is happening — like renting a toll booth you barely use. For a small app, put the parts that need the internet in **public subnets** protected by security groups (or give Fargate tasks public IPs), and use **VPC gateway endpoints** (free for S3 and DynamoDB) for traffic to AWS itself.
:::

:::quiz
4 · Security group vs network ACL: which is stateful, and which do you normally use?

**Security groups** are stateful — if you allow a request in, the reply is allowed back out automatically — and they attach to each network interface. You use them for almost everything. **NACLs** are stateless filters on a whole subnet, used only now and then for broad deny rules.
:::

:::quiz
5 · Your RDS instance should only accept connections from your API servers. How do you express that?

Put RDS in private subnets with **Public access: No**, and on its security group allow incoming port 5432 **from the API's security group** — point at the group, not at an IP range, so the rule keeps working when servers are replaced. Also require TLS (`sslmode=verify-full`).
:::

:::quiz
6 · How should browsers get product images from a private S3 bucket, and how should sellers upload them?

Serve them through **CloudFront with Origin Access Control**: the bucket stays private and only the CDN may read it. Sellers upload **straight to S3 using a short-lived presigned POST** that limits the file name, type and size — so the file never passes through your API.
:::
::::

:::tip[Scoring yourself]
Pass with **5 of 6**. Even if you pass, read lesson 01 — the free plan's rules (and account closure) matter before you click anything.
:::
