---
title: "Terraform Basics: Infrastructure as Code"
summary: Instead of clicking in the AWS console, you write your cloud as a file — servers, databases, networks. Terraform shows a plan of what will change, then makes reality match. It's repeatable, reviewable in git, and torn down with one command.
type: lesson
source: original
roles: { be: recommended, fe: optional, fs: recommended, ai: recommended, ops: core }
durationMinutes: 100
tags: [terraform, iac, aws, devops, infrastructure]
lastReviewed: 2026-09
awsCost: concept
---

::part[Learn the Concept]{n="1"}

## 🎯 What you'll learn

- What **Infrastructure as Code (IaC)** is and why clicking in the console doesn't scale
- How **Terraform** turns a description of your cloud into real resources
- The safe loop: **plan** (preview the changes) then **apply** (make them)
- What Terraform's **state** is (its memory of what it built)
- Why `terraform destroy` is the antidote to surprise bills

## 🔤 Key words

| Word | In simple words | Bahasa Indonesia |
|---|---|---|
| **Infrastructure as Code (IaC)** | Describing your servers/network in files, not by clicking | Infrastruktur dalam berkas |
| **Terraform** | A popular tool that builds cloud resources from those files | Alat pembangun infrastruktur |
| **Resource** | One thing you create: a server, database, bucket | Satu sumber daya |
| **Plan** | A preview of what will be created, changed, or destroyed | Pratinjau perubahan |
| **Apply** | Actually make the changes | Terapkan perubahan |
| **State** | Terraform's record of what it has built | Catatan yang sudah dibuat |
| **Drift** | When reality no longer matches the code | Ketidakcocokan |

## 🧠 The big idea

Building your cloud by **clicking around the AWS console** is like assembling furniture from memory: it works once, but you can't remember exactly what you did, you can't do it the same way twice, and nobody else can reproduce it.

**Infrastructure as Code** is the **IKEA instruction sheet**: the whole build written down, step by step, in a file. Anyone can follow it and get the *same* result. If you want a second identical room (a staging environment), you follow the same sheet. If you want to throw it all away, you have a record of every piece to remove — nothing forgotten in a corner, quietly costing money.

Terraform is the tool that reads your instruction sheet, looks at what already exists, and does exactly the steps needed to make reality match — no more, no less.

## ❓ Why it matters

In Weeks 3–4 you created AWS resources partly by hand. That's fine for learning, but as a way to run real systems, "click-ops" falls apart:

- **Not repeatable.** You set up production by clicking 40 screens. Now build an identical staging. Can you click the exact same 40, the exact same way? Nobody can — so staging and production quietly differ, and you get the Week 2 bug: "it worked in staging."
- **Not reviewable.** A teammate changes a security group in the console. There's no diff, no pull request, no record of *who changed what and why*. The infrastructure just silently mutated.
- **Not disposable.** You spin up ten resources to try something, then forget three of them. They keep billing you for months. This is the #1 way learners get a surprise AWS bill.
- **Drift.** Someone tweaks a setting by hand; now the "real" setup doesn't match any document. Six months later nobody knows why production behaves differently.

IaC fixes all four. Your infrastructure is a file in git: **repeatable** (apply it again for an identical environment), **reviewable** (changes go through pull requests with a visible diff), **disposable** (`terraform destroy` removes everything it made — the surest way to avoid forgotten resources), and **drift-detectable** (Terraform compares code to reality and tells you what's off). The cost is a learning curve and a new tool to run — but for anything beyond a one-off experiment, describing infrastructure in code is simply how it's done now.

## 📖 Step by step

### 1. Describe what you want

Terraform files (`.tf`) declare **resources** — you say *what* should exist, not *how* to create it:

```hcl
# A single server, described in code.
resource "aws_instance" "web" {
  ami           = "ami-0abcd1234"
  instance_type = "t3.micro"
  tags = {
    Name = "revoshop-web"
  }
}
```

This is declarative, the same mindset as Kubernetes: you state the end result, and the tool figures out the API calls to get there.

### 2. Plan: look before you leap

**Never** let a tool change your cloud without showing you first. `terraform plan` prints a **preview** — a diff of what it will create, change, or destroy:

```bash
terraform plan
# + aws_instance.web will be created
#     instance_type = "t3.micro"
# Plan: 1 to add, 0 to change, 0 to destroy.
```

The `+` means "create". Later, changing a value might show `~` (change in place) or `-` (destroy). This preview is your seatbelt: you read it and confirm the tool is about to do what you meant — *before* anything real happens. A plan that says "3 to destroy" when you expected "1 to add" just saved you.

### 3. Apply: make it real

```bash
terraform apply     # shows the plan again, then asks: do you want to proceed? yes
```

Terraform makes exactly the changes in the plan. Run it again with no code changes and it says "no changes" — reality already matches the file. That idempotency is the point: applying the same code always converges to the same result.

### 4. State: Terraform's memory

To know what to change, Terraform keeps a **state** file recording what it has built. When you edit your code and plan, it compares *code* (what you want) with *state* (what it made) with *reality* (what's actually there), and shows the difference.

> ⚠️ State can contain sensitive values and must not be lost or shared carelessly. Real teams keep it in a shared, locked backend (like an S3 bucket with locking), never committed to git. For learning, a local state file is fine.

### 5. Destroy: the off switch

```bash
terraform destroy   # previews everything it will remove, then does it
```

This is the feature that keeps you safe on AWS: everything you created through Terraform is removed in one command, previewed first. No hunting through the console for that database you forgot. Create, experiment, `destroy` — the same local-first discipline you've used all module, now for real cloud resources.

### Choosing your setup

- ✅ Any real environment, anything you'll build more than once, anything a team shares → IaC with Terraform.
- ✅ Experiments you want to be sure you can fully tear down → Terraform, so `destroy` cleans up.
- 🚫 A quick one-off click to look at something → the console is fine; just don't run real systems that way.
- 🚫 Editing Terraform-managed resources by hand in the console → causes drift; change the code instead.

## ⚠️ Common mistakes

- Running `apply` (or `destroy`) **without reading the plan** — the plan is there to catch a mistake before it's real.
- Building production by **clicking**, so it can never be reproduced or reviewed.
- Editing a Terraform-managed resource **by hand**, causing drift the code no longer describes.
- **Losing or committing** the state file — losing it strands your resources; committing it can leak secrets.
- Forgetting to `destroy` experiments, then paying for orphaned resources for months.

## 🏆 Best practices

- [ ] Keep all real infrastructure as **code in git**, changed through pull requests.
- [ ] Always **read the plan** before you apply or destroy.
- [ ] Store **state** in a shared, locked backend (S3 + locking); never commit it.
- [ ] Change resources by **editing code**, never by hand in the console (avoid drift).
- [ ] `terraform destroy` experiments when done — the reliable cure for surprise bills.

:::revoshop
1. **Codify Week 4.** In Week 4 you deployed RevoShop's backend on AWS. List the resources that setup needs (an instance or ECS service, a database, a security group, a load balancer). Each of those is a Terraform `resource` block.
2. **Read a plan.** Imagine `terraform plan` prints "Plan: 1 to add, 0 to change, **2 to destroy**" when all you meant to do was add one instance. What would you do, and why is the plan step what saved you?
3. **The teardown promise.** With everything in Terraform, how do you make sure a weekend of AWS experiments costs you almost nothing by Monday? Which command, and why is that safer than the console?
4. **Two environments.** How does having your infra as code make an identical staging environment easy — and how does that kill the "it worked in staging" bug from Week 2?
:::

::part[Explain & Design]{n="2"}

## 🗣️ Explain it

Explain to a teammate why you'd describe RevoShop's AWS setup in Terraform instead of clicking it together in the console — using the IKEA-instructions analogy — and what the `plan` step protects you from.

## 📐 Design it

On paper, list the Terraform resources for RevoShop's AWS deployment and describe the safe change loop you'd follow to add one (say, a second instance): write the resource, run plan and check the diff, apply, and how you'd fully tear it down afterward.

:::quiz
Show a possible answer

Resources: an ECS service (or EC2 instance) for the API, an RDS PostgreSQL database, a security group, a load balancer, and the networking (VPC/subnets) from Week 3. Change loop to add a second instance: (1) add/adjust the resource block in `.tf` and open a pull request so the diff is reviewed; (2) `terraform plan` and confirm it says "1 to add, 0 to destroy" — not something scary; (3) `terraform apply` and let it make exactly that change; (4) when finished experimenting, `terraform destroy` (after reading its preview) to remove everything and stop the billing. Because it's all code, staging can be an identical apply of the same files, so the two environments can't silently drift.
:::

### 📝 Self-review checklist

- [ ] Every resource is described in code, not clicked
- [ ] The loop is plan → read the diff → apply
- [ ] I can fully tear it down with destroy

::ai-review{task="design"}

::part[Toy Exercise]{n="3"}

:::exercise{path="exercises/m5/w7/01-terraform-plan" ai="no-ai" title="Compute a Terraform plan"}
Write `plan(current, desired)`, the diff at Terraform's heart: compare the resources that exist now with the ones your code asks for, and report what must be **created**, **changed**, or **destroyed** — the preview you read before anything touches your cloud.
:::

:::hints
- Both `current` and `desired` are dicts of `name -> attributes` (an attributes dict per resource).
- **create**: in `desired` but not in `current`. **destroy**: in `current` but not in `desired`. **change**: in both, but the attributes differ.
- Return sorted lists so the plan is stable, e.g. `{"create": [...], "change": [...], "destroy": [...]}`.
:::

## ✅ Quick check

:::quiz
Why is `terraform plan` (a preview) such an important habit before `apply`?

Because it shows you exactly what will be created, changed, or destroyed *before* anything real happens. If the plan says "2 to destroy" when you only meant to add one resource, you catch the mistake for free and stop. Applying without reading the plan is letting a tool reshape your cloud sight-unseen — the plan is your seatbelt.
:::

:::quiz
Name two problems Infrastructure as Code solves that clicking around the console does not.

Any two of: **repeatability** (apply the same files for an identical staging environment, instead of trying to re-click 40 screens), **reviewability** (changes go through pull requests with a visible diff and a record of who/why), **disposability** (`terraform destroy` removes everything it made, so no forgotten resources bill you), and **drift detection** (Terraform compares code to reality and flags hand-made changes).
:::

## 📚 Keep learning

- [Terraform: What is Terraform?](https://developer.hashicorp.com/terraform/intro)
- [Terraform: plan command](https://developer.hashicorp.com/terraform/cli/commands/plan)
- [Terraform: State](https://developer.hashicorp.com/terraform/language/state)
