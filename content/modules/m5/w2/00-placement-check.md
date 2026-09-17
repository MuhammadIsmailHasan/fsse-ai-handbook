---
title: "Week 2 Placement Check"
summary: Pipeline design and DORA metrics, build-once-deploy-many workflows in GitHub Actions, environments with approvals, configuration parity, handling secrets and OIDC login to AWS — check what you can skip.
type: placement-check
source: original
roles: { be: recommended, fe: optional, fs: recommended, ai: recommended, ops: core }
durationMinutes: 20
tags: [placement, ci-cd, github-actions, oidc, devops]
---

::::placement{id="modules/m5/w2"}
Answer from memory. If a word is new to you, that's a sign to study the lesson.

:::quiz
1 · What's the difference between continuous delivery and continuous deployment?

Continuous **delivery**: every change that passes the pipeline *can* be released at any time, usually after someone approves it. Continuous **deployment**: every change that passes is released to production automatically, with no human step.
:::

:::quiz
2 · Name the four key DORA metrics.

Deployment frequency, change lead time, change failure rate, and how long it takes to recover from a failed deployment.
:::

:::quiz
3 · Why "build once, deploy many" — and what exactly moves from staging to production?

The **same unchanged package** moves forward (an image named by its digest). It is tested in staging and then deployed to production. Rebuilding for production could produce a different image — new dependency versions, a new base image — than the one you actually tested.
:::

:::quiz
4 · How can a workflow step be attacked through its own text, and how do you prevent it?

`run: echo "${{ github.event.pull_request.title }}"` pastes text written by a stranger into the shell command before it runs, so a crafted PR title can run commands. Pass untrusted values through `env:` and use `"$TITLE"` inside the script; also give the workflow the smallest `permissions` it needs.
:::

:::quiz
5 · Why is OIDC better than storing `AWS_ACCESS_KEY_ID`/`AWS_SECRET_ACCESS_KEY` as GitHub secrets, and what's the most important part of the IAM trust policy?

There are no long-lived keys to leak or rotate — GitHub trades a short-lived signed token for temporary credentials. In the trust policy, the `sub` condition must say **which repository and which branch or environment** may use the role (never `repo:owner/*` or `*`).
:::

:::quiz
6 · What should a GitHub **environment** named `production` give you?

Required reviewers (approval), a rule about which branches or tags may deploy, secrets and variables that exist only for that environment, and a record of deployments — plus a concurrency group so two deploys never run at the same time.
:::
::::

:::tip[Scoring yourself]
Pass with **5 of 6**. Everyone should do lesson 05 — it wires **your RevoShop** into a real pipeline.
:::
