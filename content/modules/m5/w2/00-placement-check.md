---
title: "Week 2 Placement Check"
summary: Pipeline design and DORA metrics, build-once-deploy-many workflows in GitHub Actions, environments with approvals, configuration parity, secrets management and OIDC federation to AWS — check what you can skip.
type: placement-check
source: original
roles: { be: recommended, fe: optional, fs: recommended, ai: recommended, ops: core }
durationMinutes: 20
tags: [placement, ci-cd, github-actions, oidc, devops]
---

::::placement{id="modules/m5/w2"}
:::quiz
1 · What's the difference between continuous delivery and continuous deployment?

Continuous **delivery**: every change that passes the pipeline *can* be released at any time (often with a manual approval). Continuous **deployment**: every passing change is released to production automatically.
:::

:::quiz
2 · Name the four key DORA metrics.

Deployment frequency, change lead time, change failure rate, and failed-deployment recovery time (time to restore service).
:::

:::quiz
3 · Why "build once, deploy many" — and what exactly gets promoted from staging to production?

The **same immutable artifact** (an image referenced by digest) is tested in staging and then deployed to production. Rebuilding for production could produce a different image (new dependency versions, different base image) than the one you tested.
:::

:::quiz
4 · How can a workflow step be vulnerable to script injection, and how do you prevent it?

`run: echo "${{ github.event.pull_request.title }}"` pastes attacker-controlled text into the shell script before it runs. Pass untrusted values through `env:` and reference `"$TITLE"` in the script; also minimize `permissions`.
:::

:::quiz
5 · Why is OIDC better than storing `AWS_ACCESS_KEY_ID`/`AWS_SECRET_ACCESS_KEY` as GitHub secrets, and what's the most important part of the IAM trust policy?

No long-lived keys to leak or rotate — GitHub exchanges a short-lived signed token for temporary credentials. The trust policy's `sub` condition must restrict **which repository and which branch/environment** can assume the role (never `repo:owner/*` or `*`).
:::

:::quiz
6 · What should a GitHub **environment** named `production` provide?

Required reviewers (approval), deployment branch/tag restrictions, environment-scoped secrets and variables, and a record of deployments — plus a concurrency group so two deploys never overlap.
:::
::::

:::tip[Scoring yourself]
Pass with **5 of 6**. Everyone should do lesson 05 — it wires **your RevoShop** into a real pipeline.
:::
