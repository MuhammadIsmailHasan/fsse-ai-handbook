---
title: "Terraform for CareerPilot: Variables, Outputs & Modules"
summary: Go past a single resource. Variables let one config serve dev and prod, outputs hand back values like a database URL, and modules bundle a reusable group of resources — so you can stand up CareerPilot's cloud, repeatably, from code.
type: lesson
source: original
roles: { be: recommended, fe: optional, fs: recommended, ai: recommended, ops: core }
durationMinutes: 90
tags: [terraform, iac, modules, careerpilot, aws]
lastReviewed: 2026-09
awsCost: concept
---

::part[Learn the Concept]{n="1"}

## 🎯 What you'll learn

- **Variables** — one set of Terraform files that serves dev *and* prod
- **Outputs** — getting values back out (a database URL, a load balancer address)
- **Modules** — bundling a reusable group of resources you can stamp out again
- How these turn Week 1's single resource into a real app's infrastructure
- The same plan → apply → destroy loop, now for CareerPilot

## 🔤 Key words

| Word | In simple words | Bahasa Indonesia |
|---|---|---|
| **Variable** | A blank in your config, filled per environment | Nilai yang bisa diganti |
| **Output** | A value Terraform hands back after building | Nilai yang dikembalikan |
| **Module** | A reusable bundle of resources with its own inputs | Paket sumber daya |
| **Environment** | dev / staging / prod, each with its own settings | Lingkungan |
| **tfvars** | A file holding the values for the variables | Berkas isian variabel |

## 🧠 The big idea

The last lesson wrote one hard-coded resource. Real infrastructure needs three more moves, and they map to things you already know:

- **Variables** are the **blanks in a form** — the same mail-merge idea from Helm. One config, filled differently for dev (`t3.micro`, 1 copy) and prod (`t3.small`, 3 copies).
- **Outputs** are the **receipt** the build hands you: "here's your database's address, here's your site's URL" — values you (or another tool) need after the resources exist.
- **Modules** are **IKEA kits**: a boxed bundle ("a web service with its load balancer and security group") you can drop in once, or five times, without rewriting the pieces.

Together they let you describe CareerPilot's whole cloud once and stamp out identical copies on demand.

## ❓ Why it matters

Without variables, you'd copy your entire Terraform folder for each environment and hand-edit values inside — the exact copy-paste drift problem Helm solved for Kubernetes. One `.tf` set plus a small values file per environment keeps dev and prod the **same shape**, differing only where you intend.

Without outputs, you'd build a database and then go **hunting in the console** for its address to paste into your app's config. Outputs hand it to you (and to the next tool) automatically, so the pieces connect without manual copying — fewer mistakes, and it's automatable.

Without modules, a big system becomes one giant unreadable file with the same patterns copied over and over. A module names a pattern once ("a service behind a load balancer") so you reuse it and read it easily — the same "don't repeat yourself" you learned in the Architecture track, applied to infrastructure.

CareerPilot is a good size to see all three: it has a backend API, a database, some storage, and it deserves at least a dev and a prod environment. Describing it in parameterized, modular Terraform is how a real team would run it — and it's your **Phase 5** project.

## 📖 Step by step

### 1. Variables: one config, many environments

Declare a variable, use it, and supply its value per environment:

```hcl
variable "instance_type" {
  type    = string
  default = "t3.micro"
}

resource "aws_instance" "api" {
  instance_type = var.instance_type   # the blank, filled from the variable
  ami           = var.ami
}
```

```hcl
# prod.tfvars                # dev.tfvars
instance_type = "t3.small"   # instance_type = "t3.micro"
```

```bash
terraform apply -var-file=dev.tfvars    # builds the small dev version
terraform apply -var-file=prod.tfvars   # builds the bigger prod version
```

Same files, different fillings — dev and prod can't silently drift.

### 2. Outputs: get values back

After building, you need some values — the database endpoint, the site URL. Declare them as **outputs**:

```hcl
output "database_url" {
  value = aws_db_instance.main.address
}

output "site_url" {
  value = aws_lb.web.dns_name
}
```

```bash
terraform output database_url    # prints the address; no console hunting
```

Now your app's config, or your CI pipeline, can read these automatically instead of someone copy-pasting an address from a web page.

### 3. Modules: reuse a bundle

A **module** is a folder of resources with its own inputs (variables) and outputs. You use it like a function you call:

```hcl
module "api" {
  source        = "./modules/web-service"   # the reusable bundle
  instance_type = var.instance_type
  app_image     = var.app_image
}
```

The `web-service` module might contain the instance, its security group, and its load balancer — written once. Need a second identical service? Call the module again with different inputs. This is the Architecture track's "don't repeat yourself," now for infrastructure.

### 4. The CareerPilot shape

CareerPilot needs, roughly: a **backend service** (API), a **database** (RDS PostgreSQL), some **storage** (S3 for files), and **config/secrets** (Parameter Store / Secrets Manager). A sensible Terraform layout:

```text
careerpilot-infra/
├── modules/
│   ├── web-service/     # API service + load balancer + security group
│   └── database/        # RDS instance + its security group
├── main.tf              # calls the modules, wires them together
├── variables.tf         # instance_type, db_size, app_image, ...
├── outputs.tf           # database_url, site_url
├── dev.tfvars           # small, cheap values
└── prod.tfvars          # bigger values
```

Then `terraform apply -var-file=dev.tfvars` builds a full CareerPilot dev environment, and `prod.tfvars` builds prod from the *same* code.

### 5. Same safe loop, always

Nothing about the loop changes: **plan** (read the diff), **apply** (make it), **destroy** (remove it, previewed). Variables and modules just make the thing you're planning bigger and reusable. Always read the plan — a module can create many resources at once, so the preview matters even more.

### Choosing your setup

- ✅ More than one environment → variables + `.tfvars` files, not copied folders.
- ✅ A pattern you build more than once (a service, a database) → a module.
- ✅ Values another step needs (DB URL, site URL) → outputs.
- 🚫 Don't over-modularize a tiny setup; a module for a single one-off resource just adds indirection.

## ⚠️ Common mistakes

- Copying the whole Terraform folder per environment instead of using **variables** — they drift apart.
- Hard-coding values that differ per environment (sizes, image tags) directly in resources.
- Hunting the console for a database address instead of declaring an **output**.
- Putting **secrets** in `.tfvars` committed to git — keep secrets in Secrets Manager/Parameter Store and reference them.
- Modules so generic and deeply nested that nobody can tell what they build — keep them readable.

## 🏆 Best practices

- [ ] Parameterize per-environment differences with **variables** and `.tfvars` files.
- [ ] Expose values other steps need as **outputs** (DB URL, site URL).
- [ ] Bundle repeated patterns into **modules**; keep them small and readable.
- [ ] Keep **secrets** out of tfvars/git; reference a secrets store instead.
- [ ] Build dev and prod from the **same code**, different values — no drift.

:::revoshop
1. **Find the variables.** For CareerPilot (or RevoShop), list which values would differ between dev and prod: instance size, replica/instance count, image tag, database size. Those become variables in `.tfvars`.
2. **List the outputs.** After Terraform builds CareerPilot, which values does the app or your CI need back? (Database URL? Site URL? A bucket name?) Each is an `output`.
3. **Spot a module.** Which group of resources appears more than once, or is worth naming as a bundle (a "web service": instance + load balancer + security group)? That's a module candidate.
4. **Prep Phase 5.** Sketch the folder layout for CareerPilot's Terraform (modules, variables, tfvars per environment). You'll build a version of this in Phase 5.
:::

::part[Explain & Design]{n="2"}

## 🗣️ Explain it

Explain to a teammate how variables, outputs and modules turn "one hard-coded server" into "CareerPilot's whole cloud, buildable for dev and prod from the same code." Tie each to something they know: variables ↔ Helm blanks, modules ↔ don't-repeat-yourself, outputs ↔ a receipt of addresses.

## 📐 Design it

Design CareerPilot's Terraform layout: name the modules, the variables that differ between dev and prod, the outputs the app needs, and write the two `apply` commands. Then describe how you'd tear the dev environment down cleanly.

:::quiz
Show a possible answer

**Modules:** `web-service` (API instance/ECS service + load balancer + security group) and `database` (RDS + its security group). **Variables (differ per env):** `instance_type`, `instance_count`, `db_size`, `app_image` — set in `dev.tfvars` (small) and `prod.tfvars` (bigger). **Outputs:** `database_url` (for the app's config), `site_url` (to visit / for CI). **Commands:** `terraform apply -var-file=dev.tfvars` and `...prod.tfvars`. **Teardown:** `terraform destroy -var-file=dev.tfvars` — read the preview (it may remove many resources from the modules), confirm, and everything the dev environment created is gone, so it stops billing. Secrets live in Secrets Manager and are referenced, never put in the tfvars files.
:::

### 📝 Self-review checklist

- [ ] Per-environment differences are variables, not copied files
- [ ] Reusable patterns are modules; needed values are outputs
- [ ] Secrets are referenced, not committed in tfvars

::ai-review{task="design"}

::part[Toy Exercise]{n="3"}

### 🧠 Design it (no code)

There's no Python here — the practice is designing CareerPilot's infrastructure on paper, ready for **Phase 5**:

1. Draw the folder layout (`modules/`, `main.tf`, `variables.tf`, `outputs.tf`, `dev.tfvars`, `prod.tfvars`).
2. List every variable and its dev vs prod value in a small table.
3. List the outputs and say who consumes each one.
4. For each module, list the resources inside it.
5. Write the exact `plan`, `apply` and `destroy` commands for the **dev** environment.

Keep this design — Phase 5 asks you to build a working slice of it.

## ✅ Quick check

:::quiz
Why use variables with `dev.tfvars`/`prod.tfvars` instead of copying the Terraform folder for each environment?

So dev and prod share the exact same code (the same *shape*), and only the intended differences — sizes, counts, image tags — live in the small values files. Copied folders drift apart as changes get made to one and not the other, recreating the "staging tested something different from production" bug. One config, many fillings, keeps environments honest.
:::

:::quiz
What problem do Terraform outputs solve?

After Terraform builds resources, you often need some of their values — a database's address, a load balancer's URL. Without outputs you'd hunt for them in the console and paste them into config by hand. Outputs hand those values back automatically, so your app config or CI pipeline can read them directly — no manual copying, fewer mistakes.
:::

## 📚 Keep learning

- [Terraform: Input variables](https://developer.hashicorp.com/terraform/language/values/variables)
- [Terraform: Output values](https://developer.hashicorp.com/terraform/language/values/outputs)
- [Terraform: Modules](https://developer.hashicorp.com/terraform/language/modules)
