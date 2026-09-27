---
title: "Helm: Templates & Packages for Kubernetes"
summary: Helm does two jobs — install prepackaged apps on Kubernetes with one command (a chart is like apt/brew for clusters), and template your own manifests so one file with blanks fills in per environment instead of copy-pasting YAML.
type: lesson
source: original
roles: { be: recommended, fe: optional, fs: recommended, ai: recommended, ops: core }
durationMinutes: 80
tags: [kubernetes, helm, templating, packaging, devops]
lastReviewed: 2026-09
---

::part[Learn the Concept]{n="1"}

## 🎯 What you'll learn

- The two jobs **Helm** does: **installing packages** and **templating manifests**
- What a **chart** is (a package for Kubernetes) and a **values** file (its settings)
- Why templating beats copy-pasting near-identical YAML for dev/staging/prod
- The mail-merge idea at Helm's core: **one template, many filled-in copies**
- When Helm helps and when it's more than you need

## 🔤 Key words

| Word | In simple words | Bahasa Indonesia |
|---|---|---|
| **Helm** | A tool that packages and templates Kubernetes manifests | Alat paket & template K8s |
| **Chart** | A Helm package: templates + default settings for an app | Paket Helm |
| **Values** | The settings you feed a chart (image, replicas, etc.) | Pengaturan chart |
| **Template** | A manifest with blanks to be filled in | Cetakan dengan bagian kosong |
| **Render** | Fill the blanks with values to get real YAML | Isi blank jadi YAML nyata |
| **Release** | One installed instance of a chart in a cluster | Satu instalasi chart |

## 🧠 The big idea

Helm is **mail merge for Kubernetes**. When you send the same letter to 100 people, you don't retype it 100 times — you write **one** template with blanks ("Dear **[name]**, your order **[number]**…") and a list of values, and the merge fills them in. Helm does exactly that for Kubernetes YAML: you write **one** template with blanks like `{{ .Values.replicas }}`, and a small **values** file supplies `replicas: 3`. Helm renders the real manifest by filling the blanks.

Its second job is being the **app store for clusters**: a **chart** is a ready-made package (say, "PostgreSQL" or "Redis"), and `helm install` drops it into your cluster the way `brew install` or `apt install` drops software onto your computer — one command instead of hand-writing dozens of manifests.

## ❓ Why it matters

Once you run real Kubernetes, two annoyances show up fast.

**First: copy-paste sprawl.** You need almost the same manifests for dev, staging and production — same app, but different image tag, replica count, and resource sizes. Without templating you keep three (or ten) near-identical YAML files. Change one thing and you must edit it in every copy, and the copies quietly drift apart until "staging tested a different setup than production" — the exact bug Week 2 warned about. Helm fixes this: **one** template, and a tiny values file per environment (`values-prod.yaml` sets `replicas: 6`, `values-dev.yaml` sets `replicas: 1`). The shared shape lives in one place; only the differences are written down.

**Second: installing other people's software.** You want Redis, or a metrics tool, or an ingress controller on your cluster. Writing all those manifests by hand from their docs is slow and error-prone. Someone has already packaged each as a **chart**, so `helm install redis ...` sets it up correctly in one line, and `helm upgrade` / `helm uninstall` manage it cleanly. This is the same leverage a package manager gives you on your laptop — you don't compile software from scratch, and you shouldn't hand-write cluster manifests from scratch either.

The trade: Helm adds a templating layer, and heavily templated charts can get hard to read (blanks inside blanks). For a small app with one environment, plain manifests are clearer. Helm earns its place when you have **several environments** or you're **installing packaged apps** — not before.

## 📖 Step by step

### 1. Helm as a package manager

```bash
# Add a repository of charts, then install one — like apt/brew for your cluster.
helm install my-redis bitnami/redis
helm list                 # what's installed (releases)
helm upgrade my-redis bitnami/redis --set replica.replicaCount=2
helm uninstall my-redis   # clean removal of everything it created
```

One command installs an app that would otherwise be dozens of hand-written manifests. `helm uninstall` removes exactly what it added — no leftovers.

### 2. Helm as a templater (the mail-merge)

A template manifest has blanks that read from values:

```yaml
# templates/deployment.yaml  (a template, not final YAML)
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ .Values.name }}
spec:
  replicas: {{ .Values.replicas }}      # a blank, filled from values
  template:
    spec:
      containers:
        - name: {{ .Values.name }}
          image: {{ .Values.image }}
```

And a values file supplies the answers:

```yaml
# values.yaml
name: revoshop-api
replicas: 3
image: revoshop-api:v1.4
```

`helm template` (or `helm install`) **renders** them together into the real manifest — `replicas: 3`, `image: revoshop-api:v1.4`. Same idea as the letter and the name list.

### 3. One template, many environments

The whole point: keep one template, and one small values file per environment for *only* the differences.

```yaml
# values-dev.yaml        # values-prod.yaml
replicas: 1              # replicas: 6
image: revoshop-api:dev  # image: revoshop-api:v1.4
```

```bash
helm template -f values-dev.yaml .    # renders the dev version
helm template -f values-prod.yaml .   # renders the prod version
```

Dev and prod now share the exact same shape and can't drift apart by accident — only the listed values differ. This is "build once, configure per environment" (Week 2) applied to your manifests.

### 4. What a chart contains

A **chart** is just a folder: a `templates/` directory (the manifests with blanks), a `values.yaml` (the defaults), and a `Chart.yaml` (name and version). Installing it creates a **release** — one named instance in your cluster that Helm tracks so it can upgrade or remove it as a unit.

### Choosing your setup

- ✅ Installing packaged apps (Redis, ingress, monitoring) → Helm, one command.
- ✅ One app across several environments that differ only in a few values → Helm templating.
- 🚫 A single small app with one environment → plain manifests are simpler and clearer.
- 🚫 Templating so heavily that nobody can read the result → you've traded one problem for a worse one.

## ⚠️ Common mistakes

- Keeping many **copy-pasted** manifests for environments instead of one template + values files — they drift apart.
- Over-templating: blanks inside blanks inside conditionals, until the chart is unreadable.
- Installing charts from **untrusted** sources without reading what they create — you're running someone's manifests in your cluster.
- Editing rendered YAML in the cluster by hand, so the next `helm upgrade` overwrites your change — edit values or templates instead.
- Reaching for Helm on a tiny single-environment app where plain YAML is clearer.

## 🏆 Best practices

- [ ] Use Helm to **install packaged apps** instead of hand-writing their manifests.
- [ ] Keep **one template** and a small **values file per environment** for the differences.
- [ ] Keep templates readable; don't template what never changes.
- [ ] Track versions: pin chart versions and keep your values files in git.
- [ ] Install charts only from sources you trust, and read what they create.

:::revoshop
1. **Spot the copy-paste.** If RevoShop ran on Kubernetes with dev/staging/prod, which fields would differ between environments (image tag, replicas, resource sizes, config)? Those differences are exactly what a values file holds.
2. **Write the values.** Sketch `values-dev.yaml` and `values-prod.yaml` for RevoShop: replicas and image tag for each. What stays identical (and therefore belongs in the template, not the values)?
3. **Install a dependency.** RevoShop needs Redis. Compare hand-writing Redis manifests vs `helm install`. What does the chart save you, and what must you still decide (memory, persistence)?
4. **Is it worth it yet?** RevoShop today has effectively one environment. Is Helm's templating layer worth adding now, or is that a "later, if we add environments" call? Say why.
:::

::part[Explain & Design]{n="2"}

## 🗣️ Explain it

Explain to a teammate, using the mail-merge analogy, why keeping one Helm template plus a values file per environment is safer than keeping three near-identical YAML files — and connect it to the "staging tested something different from production" bug from Week 2.

## 📐 Design it

Design RevoShop's Helm setup for two environments. Decide what goes in the shared template vs the per-environment values files, write the two values files (dev and prod differ in replicas and image), and name one chart you'd `helm install` rather than hand-write.

:::quiz
Show a possible answer

**Template (shared):** the Deployment and Service shape — container name, ports, labels, the structure — with blanks for `name`, `replicas`, and `image`. **Values:** `values-dev.yaml` → `replicas: 1`, `image: revoshop-api:dev`; `values-prod.yaml` → `replicas: 6`, `image: revoshop-api:v1.4`. Everything else (ports, labels, probes) stays in the template so dev and prod can't drift. **Installed chart, not hand-written:** Redis (e.g. the Bitnami Redis chart) — one `helm install` with a values override for memory and persistence, instead of writing Redis manifests from its docs.
:::

### 📝 Self-review checklist

- [ ] Shared shape is in the template; only differences are in values
- [ ] Dev and prod values files differ only where they should
- [ ] I used a chart for a dependency instead of hand-writing it

::ai-review{task="design"}

::part[Toy Exercise]{n="3"}

:::exercise{path="exercises/m5/w6/04-helm-render" ai="no-ai" title="Render a Helm template"}
Build the tiny engine at Helm's heart: write `render(template, values)` that replaces every `{{ .Values.key }}` blank in a template string with the matching value — the same fill-in-the-blanks step Helm runs before sending manifests to Kubernetes.
:::

:::hints
- A blank looks like `{{ .Values.NAME }}`, where `NAME` is letters, digits or underscores. Allow optional spaces inside the braces.
- Use `re.sub` with a pattern like `\{\{\s*\.Values\.(\w+)\s*\}\}` and a replacer function that looks up the captured name in `values`.
- Convert values to text with `str(...)`, so an integer like `3` renders as `3`. If a referenced key isn't in `values`, raise `KeyError(name)`.
:::

## ✅ Quick check

:::quiz
Why is one Helm template plus a values file per environment safer than three near-identical YAML files?

The shared shape lives in exactly one place, so it can't drift between environments — only the intended differences (replicas, image) are written down, in the values files. With three copies, a change must be repeated everywhere and copies silently diverge, so staging ends up testing a different setup than production. Helm makes "same shape, different settings" the default.
:::

:::quiz
You want Redis on your cluster. Why reach for `helm install` instead of writing the manifests yourself?

Someone has already packaged Redis correctly as a chart, so one command installs it (and `helm upgrade`/`uninstall` manage it cleanly), the same way `brew install` beats compiling from source. Hand-writing all the manifests from Redis's docs is slow and easy to get wrong; you'd still choose settings like memory and persistence, but through the chart's values.
:::

## 📚 Keep learning

- [Helm: What is Helm?](https://helm.sh/docs/)
- [Helm: Charts](https://helm.sh/docs/topics/charts/)
- [Helm: Values files](https://helm.sh/docs/chart_template_guide/values_files/)
