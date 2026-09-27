---
title: "Teardown & Cost Review"
summary: The cloud bills you by the second for whatever is running, so a forgotten resource is a light left on in an empty room. Learn the teardown checklist that leaves nothing behind, and the cost review that finds waste before the bill does.
type: lesson
source: original
roles: { be: recommended, fe: optional, fs: recommended, ai: recommended, ops: core }
durationMinutes: 80
tags: [aws, cost, teardown, finops, cleanup, devops]
lastReviewed: 2026-09
awsCost: free
---

::part[Learn the Concept]{n="1"}

## 🎯 What you'll learn

- The mental shift: you **rent** cloud resources by the second — running = paying
- The **teardown checklist** that leaves nothing billing you behind
- The usual suspects behind **surprise bills** (forgotten, oversized, data transfer)
- How to **review costs**: tags, budgets, and finding the biggest line items
- Why `terraform destroy` plus a cleanup pass is your safety net

## 🔤 Key words

| Word | In simple words | Bahasa Indonesia |
|---|---|---|
| **Teardown** | Deleting resources you no longer need | Membongkar sumber daya |
| **Orphan** | A resource left running that nothing uses | Sumber daya terlantar |
| **Right-sizing** | Matching resource size to real need | Menyesuaikan ukuran |
| **Data transfer / egress** | Cost of moving data out of AWS | Biaya kirim data keluar |
| **Budget alarm** | A warning when spending passes a limit | Peringatan anggaran |
| **Tag** | A label on a resource so you know what it's for | Label sumber daya |

## 🧠 The big idea

Owning a computer feels free after you buy it — leave it on, no extra charge. The cloud is the opposite: it's a **rented apartment where the meter runs every second**. Every server, database and load balancer is a light bulb, and **you pay for every one that's on, whether or not anyone's in the room.**

So two habits keep you safe. **Teardown** is the checklist you run when you leave: turn off every light, unplug the appliances, hand back the keys — leave nothing drawing power. **Cost review** is reading the electricity bill each month to spot the heater you forgot in the spare room. Do both, and the cloud is cheap. Skip them, and a forgotten resource quietly bills you for months.

## ❓ Why it matters

The number one horror story for people learning AWS is the **surprise bill**: "I was just experimenting, and a month later I owed $200." It almost never comes from the thing you were working on — it comes from what you **forgot**. You spun up a database to test something, moved on, and it kept running at a few dollars a day for six weeks. The meter never stops just because your attention did.

This matters even more with the credit-based free plan the module warned about: credits run out, and then forgotten resources bill real money. The three usual causes are worth memorizing:

- **Forgotten resources** — the big one. Instances, databases, NAT gateways and load balancers you stopped using but never deleted. Also the *invisible* orphans: an unattached disk volume, an idle load balancer, old database snapshots, an unused Elastic IP (AWS charges for reserved-but-unused addresses).
- **Oversized resources** — a giant instance doing a tiny job. You pay for the size you asked for, not the work you used.
- **Data transfer (egress)** — moving lots of data *out* of AWS (to users or another region) costs money in ways that surprise people, because it's not a "thing" you can see running.

The fix is discipline, and you've already built most of it. If everything is in **Terraform**, `terraform destroy` removes it all in one previewed command — the single best defense, because it can't forget the way you can. Then a short **cleanup pass** catches anything created outside Terraform, and a monthly **cost review** (using the **budget alarms** you set in Week 3) catches whatever slips through *before* it becomes a real bill. None of this is hard; it's just a habit — and it's the difference between the cloud being a cheap playground and an expensive scare.

## 📖 Step by step

### 1. The mental model: running = paying

Before creating anything, ask "what does this cost per hour, and when will I turn it off?" A `t3.micro` is pennies; a big instance, a NAT gateway or an RDS database left on for a month is real money. The habit isn't stinginess — it's knowing the meter is running.

### 2. The teardown checklist

When you finish a piece of work or an experiment:

- [ ] **`terraform destroy`** the stack (read the preview, confirm). This removes everything Terraform made — the best case.
- [ ] **Stop or terminate** any instances you created by hand.
- [ ] Delete **orphans**: unattached EBS volumes, idle load balancers, unused Elastic IPs, old snapshots/AMIs.
- [ ] Empty and delete **S3 buckets** you don't need (storage bills monthly).
- [ ] Check **every region** you used — resources hide in regions you forgot you touched.
- [ ] Confirm in the **billing console** that nothing unexpected is still listed.

### 3. Finding orphans

Orphans are resources nothing uses but that still bill you. The cheap way to find them: look for things **not attached to anything** — a volume with no instance, a load balancer with no healthy targets, an Elastic IP not associated with a running instance. If a resource isn't doing a job, it's a light left on. (Tools like AWS Trusted Advisor and Cost Explorer surface these for you.)

### 4. Reviewing the bill

Once a month (or after any big experiment):

- Open **Cost Explorer** and look at the **biggest line items** first — that's where the money is.
- Use **tags** (a `project` and `environment` label on every resource) so you can see *what* each cost belongs to. Untagged spend is spend you can't explain.
- Check your **budget alarm** (Week 3) is still set — it's your automatic tripwire, the same "the system tells you" idea as last lesson's alarms, but for money.
- **Right-size**: is anything much bigger than it needs to be? Downsize it.

### 5. Tags make it all possible

A resource tagged `project=careerpilot, environment=dev` tells you, months later, *why it exists and whether you can delete it.* Untagged resources become scary mysteries nobody dares remove. Tag everything from the start (Terraform makes this easy — set tags in the resource blocks), and both teardown and cost review get far easier.

### Choosing your setup

- ✅ Everything in Terraform, tagged, with a budget alarm → teardown and review are easy and safe.
- ✅ A teardown checklist run at the end of every experiment or project.
- 🚫 Don't leave experiments running "just in case" — recreate them from code when you need them again.
- 🚫 Don't trust your memory to track resources across regions — use `destroy`, tags and the billing console.

## ⚠️ Common mistakes

- Leaving an experiment **running** and forgetting it — the classic surprise bill.
- Missing **invisible orphans**: unattached volumes, idle load balancers, unused Elastic IPs, old snapshots.
- Resources hiding in a **region you forgot** you used.
- **Untagged** resources you can't identify later, so nobody dares delete them.
- Assuming the free plan means "free forever" — credits run out, then forgotten resources cost real money.

## 🏆 Best practices

- [ ] Manage everything in **Terraform** so `terraform destroy` is a reliable off switch.
- [ ] **Tag** every resource (`project`, `environment`) from the start.
- [ ] Run a **teardown checklist** after every experiment; check all regions.
- [ ] Keep a **budget alarm** set (Week 3) as an automatic tripwire.
- [ ] Review the **biggest line items** monthly and right-size what's oversized.

:::revoshop
1. **Teardown drill.** You spent a weekend deploying RevoShop to AWS to learn. Write the exact checklist to make sure it costs you almost nothing by Monday. Which command does most of the work?
2. **Hunt the orphans.** List three "invisible" resources that could keep billing after you think you've cleaned up (hint: volumes, addresses, snapshots). How would you find each?
3. **Tag plan.** Choose the tags you'd put on every RevoShop resource so future-you can tell what's safe to delete. Why does an untagged resource become dangerous?
4. **Read a bill.** If RevoShop's AWS bill doubled one month, name the three things you'd check first (forgotten resource? oversized? data transfer?) and where you'd look.
:::

::part[Explain & Design]{n="2"}

## 🗣️ Explain it

Explain to a teammate why the cloud is a "rented apartment with the meter running", the three usual causes of a surprise bill, and why `terraform destroy` plus tags beats trying to remember what you created — using the lights-in-an-empty-room analogy.

## 📐 Design it

Design RevoShop's cost-safety setup: the tags on every resource, the budget alarm threshold, the teardown checklist you'd run after experiments, and the monthly review steps. Then explain how having everything in Terraform makes all of this reliable.

:::quiz
Show a possible answer

**Tags:** `project=revoshop`, `environment=dev|prod`, `owner` on every resource (set in Terraform blocks). **Budget alarm:** a monthly budget (say $10 for learning) that emails you at 50% and 80% — the Week 3 tripwire. **Teardown checklist:** `terraform destroy` the stack (read the preview) → terminate any hand-made instances → delete orphaned volumes, idle load balancers, unused Elastic IPs, old snapshots → empty and delete unused S3 buckets → check *every region* → confirm the billing console is clean. **Monthly review:** open Cost Explorer, sort by biggest line item, use the tags to see which project/environment it's from, right-size anything oversized, confirm the budget alarm is still active. **Why Terraform makes it reliable:** everything created through code is removed by one previewed `destroy`, so cleanup doesn't depend on remembering what you clicked — the tool can't forget.
:::

### 📝 Self-review checklist

- [ ] Everything is tagged and in Terraform
- [ ] There's a budget alarm and a teardown checklist
- [ ] I'd check forgotten/oversized/egress when a bill jumps

::ai-review{task="design"}

::part[Toy Exercise]{n="3"}

:::exercise{path="exercises/m5/w7/05-cost-review" ai="no-ai" title="Review costs and find waste"}
Write `monthly_cost(resources)` to total what your cloud costs per month, and `idle_resources(resources)` to list the orphans that are billing you for nothing — the two questions every cost review starts with.
:::

:::hints
- Use **730 hours** as one month. A resource's monthly cost is `hourly_cost * 730`.
- `monthly_cost` sums *all* resources (in use or not); round the total to 2 decimals.
- `idle_resources` returns the **sorted** names of resources where `in_use` is `False` — the ones to clean up.
:::

## ✅ Quick check

:::quiz
Why is a forgotten resource the most common cause of a surprise cloud bill?

Because the cloud bills you per second for whatever is *running*, and stopping paying attention doesn't stop the meter. You spin up a database to test something, move on, and it keeps charging a few dollars a day for weeks — often an invisible orphan (an unattached volume, an idle load balancer) you don't even remember creating. The cost isn't the thing you're working on; it's the thing you forgot.
:::

:::quiz
How does having everything in Terraform protect you from surprise bills better than being careful?

`terraform destroy` removes everything the code created in one previewed command, so cleanup doesn't rely on you remembering what you clicked across regions — and the tool doesn't forget the way people do. Being careful helps, but memory fails; code doesn't. Add tags and a budget alarm and you have a reliable off switch plus a tripwire.
:::

## 📚 Keep learning

- [AWS: Control your costs (free tier)](https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/tracking-free-tier-usage.html)
- [AWS Cost Explorer](https://docs.aws.amazon.com/cost-management/latest/userguide/ce-what-is.html)
- [AWS: Tagging best practices](https://docs.aws.amazon.com/whitepapers/latest/tagging-best-practices/tagging-best-practices.html)
