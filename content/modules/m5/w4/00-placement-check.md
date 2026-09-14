---
title: "Week 4 Placement Check"
summary: Frontends on S3, CloudFront or Amplify, zero-downtime EC2 deploys, ECS Fargate behind a load balancer, Lambda jobs with SQS, and config from Parameter Store and Secrets Manager — check what you can skip.
type: placement-check
source: original
roles: { be: recommended, fe: recommended, fs: recommended, ai: recommended, ops: core }
durationMinutes: 20
tags: [placement, aws, ecs, lambda, cloudfront, ssm]
---

::::placement{id="modules/m5/w4"}
:::quiz
1 · Can a Next.js App Router app with Server Actions and per-user pages be hosted as files on S3 + CloudFront? What are the options?

Not fully — static export can't run Server Actions, cookies-based auth or dynamic rendering. Options: a Node server (ECS/App Runner/EC2 with CloudFront in front), a managed host that supports Next.js SSR (AWS Amplify Hosting, Vercel), or restrict the app to static export.
:::

:::quiz
2 · Your EC2 deploy recreates the API container and there are 5–10 seconds of errors each time. Name two ways to remove the downtime.

Blue/green on the host (start the new version beside the old one, health-check it, switch the reverse proxy, then stop the old one), or multiple instances/tasks behind a load balancer with rolling deployments (ECS, Auto Scaling groups).
:::

:::quiz
3 · In ECS, what's the difference between the task **execution** role and the task **role**?

The execution role is used by the ECS agent to pull the image, read secrets for injection and write logs. The task role is what the **application code** uses to call AWS APIs (S3, SQS…).
:::

:::quiz
4 · How do you run database migrations for an ECS service safely?

As a one-off `ecs run-task` with the same task definition (command override `flask db upgrade`), wait for it to exit successfully, then update the service — never inside every task's startup.
:::

:::quiz
5 · A Lambda consuming an SQS batch of 10 fails on message 7. Without extra configuration, what happens, and what's the fix?

The whole batch returns to the queue and all 10 are retried (duplicates). Enable **ReportBatchItemFailures** and return only the failed message IDs; make processing idempotent and configure a dead-letter queue.
:::

:::quiz
6 · SSM Parameter Store or Secrets Manager for RevoShop's JWT secret and RDS master password?

JWT secret: Parameter Store SecureString is fine (cheap, simple). RDS master password: Secrets Manager (RDS can manage and rotate it). Both are read by IAM roles, never stored in images or task definitions as plain values.
:::
::::

:::tip[Scoring yourself]
Pass with **5 of 6**. Everyone should do lesson 06 — it moves **your RevoShop** to ECS.
:::
