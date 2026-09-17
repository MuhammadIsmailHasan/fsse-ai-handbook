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
Answer from memory. If a word is new to you, that's a sign to study the lesson.

:::quiz
1 · Can a Next.js App Router app with Server Actions and per-user pages be hosted as files on S3 + CloudFront? What are the options?

Not fully. A static export is just files on a shelf: it can't run Server Actions, read login cookies, or build pages per request. Your options: run a Node server (ECS/App Runner/EC2 with CloudFront in front), use a managed host that supports Next.js server rendering (AWS Amplify Hosting, Vercel), or keep the app inside what static export can do.
:::

:::quiz
2 · Your EC2 deploy recreates the API container and there are 5–10 seconds of errors each time. Name two ways to remove the downtime.

Either blue/green on the same server — start the new version next to the old one, check it's healthy, point the reverse proxy at it, then stop the old one — or run several copies behind a load balancer and replace them one at a time (ECS rolling deployments, Auto Scaling groups).
:::

:::quiz
3 · In ECS, what's the difference between the task **execution** role and the task **role**?

The **execution** role belongs to the delivery crew: ECS itself uses it to pull the image, read secrets to inject, and write logs. The **task** role is the badge your **application code** wears when it calls AWS APIs (S3, SQS…).
:::

:::quiz
4 · How do you run database migrations for an ECS service safely?

Run them once as their own task: `ecs run-task` with the same task definition but the command replaced by `flask db upgrade`, wait for it to finish successfully, and only then update the service. Never on every task's startup, or copies race each other.
:::

:::quiz
5 · A Lambda consuming an SQS batch of 10 fails on message 7. Without extra configuration, what happens, and what's the fix?

The whole batch goes back to the queue, so all 10 are processed again — nine of them twice. Turn on **ReportBatchItemFailures** and return only the failed message IDs, make the handler idempotent, and add a dead-letter queue for messages that keep failing.
:::

:::quiz
6 · SSM Parameter Store or Secrets Manager for RevoShop's JWT secret and RDS master password?

JWT secret: a Parameter Store SecureString is enough — cheap and simple. RDS master password: Secrets Manager, because RDS can create and rotate it for you. Either way an IAM role reads them at runtime; they never sit in an image or as plain text in a task definition.
:::
::::

:::tip[Scoring yourself]
Pass with **5 of 6**. Everyone should do lesson 06 — it moves **your RevoShop** to ECS.
:::
