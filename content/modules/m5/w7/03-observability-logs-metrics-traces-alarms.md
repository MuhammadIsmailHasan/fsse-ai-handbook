---
title: "Observability: Logs, Metrics, Traces & Alarms"
summary: In production nobody's watching, so the system must alert you. Metrics are the gauges, logs the diary, traces follow one request, and alarms are the warning lights that page a human when a number crosses a line users feel.
type: lesson
source: original
roles: { be: core, fe: optional, fs: core, ai: recommended, ops: core }
durationMinutes: 100
tags: [observability, monitoring, metrics, logs, alarms, sre]
lastReviewed: 2026-09
---

::part[Learn the Concept]{n="1"}

## 🎯 What you'll learn

- The three signals: **metrics**, **logs**, **traces** — what each answers
- What an **alarm** is and why it's what lets you stop staring at dashboards
- How to write alarms that are **useful**, not noisy (symptoms users feel)
- The rough idea of an **SLO** and an **error budget**
- How the signals work together to go from "something's wrong" to "here's why"

## 🔤 Key words

| Word | In simple words | Bahasa Indonesia |
|---|---|---|
| **Metric** | A number tracked over time (requests/sec, error rate) | Angka dari waktu ke waktu |
| **Log** | A timestamped line describing one event | Catatan kejadian |
| **Trace** | One request's journey across services (Week 5) | Perjalanan satu permintaan |
| **Alarm** | A rule that fires when a metric crosses a line | Aturan yang memicu peringatan |
| **Dashboard** | A screen of metric charts | Layar grafik |
| **SLO** | The target you promise (e.g. 99.9% of requests OK) | Target layanan |
| **Error budget** | How much failure the SLO still allows | Jatah kegagalan |

## 🧠 The big idea

Observability is the **dashboard and warning lights of a car**:

- **Metrics** are the **gauges** — speed, fuel, engine temperature. Numbers that move over time. One glance tells you *how things are going*.
- **Logs** are the **trip diary** — a detailed line for each event ("14:02 turned left onto the highway"). They tell you *exactly what happened*.
- **Traces** are **following one trip** through the car's systems (you met these in Week 5).
- **Alarms** are the **warning lights** — you don't stare at the temperature gauge for six hours; a red light comes on *only* when it crosses into danger, so you can drive (and live your life) until then.

The point of the warning light is that **the car tells you**, instead of you having to watch.

## ❓ Why it matters

Here's the uncomfortable truth about production: **you are not watching it.** It's 3 a.m., you're asleep, and 500 users just hit an error. A beautiful dashboard helps *nobody* if no human is looking at it. So the system has to reach out and **tell** you — that's what an **alarm** is, and it's the single most important piece. Metrics, logs and traces are how you *investigate*; alarms are how you *find out at all*.

But alarms cut both ways. An alarm that fires too easily — on every little blip nobody feels — trains you to ignore it. After the tenth false alarm at 3 a.m., you silence your phone, and then you miss the real one. This is **alert fatigue**, and it's how outages get missed *despite* good monitoring. So the skill isn't "add alarms"; it's writing **few, meaningful** alarms that fire on things users actually feel (the checkout is failing, the site is slow) and that a human can *act on* — not on internal noise like "CPU briefly hit 80%."

Then, once an alarm wakes you, the three signals work as a funnel: the **metric** says *something* is wrong ("error rate is 8%"), the **trace** says *where* ("the Payments span is failing"), and the **log** says *what exactly* ("Midtrans returned 503"). Metric → trace → log takes you from "there's a fire" to "it's the payment provider" in minutes instead of hours. Without this, you're guessing in the dark while users leave.

## 📖 Step by step

### 1. The three signals, side by side

| Signal | Answers | Shape | Example |
|---|---|---|---|
| **Metric** | *Is* something wrong, and how much? | numbers over time | error rate = 8% |
| **Trace** | *Where* in the request? | one request across services | Payments span failing |
| **Log** | *What exactly* happened? | timestamped event lines | "Midtrans 503 at 14:02" |

You already do structured logging (Module 2) and know tracing (Week 5). Metrics are the new piece: counts and measurements aggregated over time — requests per second, error rate, p95 latency, queue length — usually viewed as charts on a **dashboard** and, crucially, watched by **alarms**.

### 2. The four "golden signals" worth watching

For almost any service, four metrics tell you most of the story:

- **Latency** — how long requests take (watch p95/p99, not the average — the average hides the slow tail).
- **Traffic** — how much demand (requests per second).
- **Errors** — the rate of failed requests (5xx, timeouts).
- **Saturation** — how full the system is (CPU, memory, queue length).

If you only set up a few things, set these up.

### 3. What makes an alarm good

An alarm is just a rule: *when metric crosses threshold for a while, notify someone.* A **good** one is:

- **On a symptom users feel** — "error rate > 2% for 5 minutes", "p95 latency > 1s" — not on a cause nobody notices ("CPU at 80%"). High CPU that hurts no one isn't an emergency.
- **Actionable** — when it fires, there's something a human can *do*. An alarm you'd always ignore should be a chart, not an alarm.
- **Not too twitchy** — it waits a few minutes ("for 5 minutes") so a one-second blip doesn't page you.
- **Rare** — if an alarm cries wolf weekly, people stop trusting it.

> Rule of thumb: **every alarm that pages a human should be worth waking up for.** Everything else is a dashboard.

### 4. SLOs and error budgets (the gentle version)

An **SLO** (service level objective) is a target you promise: "99.9% of requests succeed each month." The gap — the 0.1% you're allowed to fail — is your **error budget**. It reframes reliability sanely: you don't need *zero* errors (impossible and ruinously expensive), you need to stay *within budget*. If you're burning the budget fast, slow down and fix reliability; if there's plenty left, you can ship features faster. It turns "is it reliable enough?" into a number instead of an argument.

### 5. On AWS

**CloudWatch** collects metrics and logs and runs **alarms** (e.g. "if 5xx error rate > 2% for 5 minutes, send a notification"); alarms notify through **SNS** to email, Slack or a pager. Traces come from **X-Ray** or OpenTelemetry (Week 5). For LLM apps, **Langfuse** gives you metrics, traces and cost per call. Same ideas everywhere — gauges, diary, one-trip view, warning lights.

### Choosing your setup

- ✅ Anything real: at least the four golden signals, plus a *few* alarms on user-facing symptoms.
- ✅ An SLO for your most important flow (checkout), with an error budget to guide priorities.
- 🚫 Don't alarm on every metric — most are dashboards, not pages.
- 🚫 Don't page humans for things they can't act on, or you'll train them to ignore alarms.

## ⚠️ Common mistakes

- **No alarms** — a gorgeous dashboard nobody watches at 3 a.m. tells you nothing.
- **Too many alarms** — alert fatigue; the real one gets ignored among false ones.
- Alarming on **causes** (CPU, memory) instead of **symptoms** users feel (errors, latency).
- Watching the **average** latency, which hides the slow tail — watch p95/p99.
- Logging **secrets or personal data**, or spending on logs you never read.

## 🏆 Best practices

- [ ] Track the four golden signals: **latency, traffic, errors, saturation**.
- [ ] Alarm on **user-facing symptoms**, and make every paging alarm **actionable**.
- [ ] Keep alarms **few and trusted**; everything else is a dashboard.
- [ ] Set an **SLO + error budget** for your most important flow.
- [ ] Use metric → trace → log as a funnel from "what's wrong" to "why".

:::revoshop
1. **Golden signals for RevoShop.** Name the four metrics you'd watch for the RevoShop API and where each comes from. Which single one would you alarm on first, and at what threshold?
2. **A good alarm vs a bad one.** Write one *good* alarm (a symptom users feel) and one *bad* alarm (a cause nobody notices) for RevoShop. Why would the bad one train you to ignore alarms?
3. **The funnel.** Checkout error rate alarms at 8%. Walk through how you'd use a trace, then a log, to get from that alarm to the actual cause (hint: Week 5's Payments span).
4. **An SLO.** Pick RevoShop's most important flow and write an SLO for it ("X% of checkouts succeed per month"). What does the error budget let you decide?
:::

::part[Explain & Design]{n="2"}

## 🗣️ Explain it

Explain to a teammate why a dashboard alone isn't enough and an **alarm** is the key piece — using the car warning-light analogy — and why *too many* alarms is as dangerous as none.

## 📐 Design it

Design RevoShop's monitoring: the four golden-signal metrics, two or three alarms (threshold, duration, and what a human does when each fires), one SLO with its error budget, and how you'd use metric → trace → log to debug a checkout failure.

:::quiz
Show a possible answer

**Metrics:** p95 latency, requests/sec, 5xx error rate, CPU/memory (and queue length if using a queue). **Alarms:** (1) "5xx error rate > 2% for 5 min" → page on-call; action: check the error/trace, roll back if a recent deploy caused it; (2) "p95 latency > 1s for 10 min" → page; action: find the slow span (trace), likely DB or payment provider; (3) "checkout success rate < 98% for 10 min" → page; action: investigate Payments. **SLO:** "99.5% of checkouts succeed per month"; the 0.5% error budget decides whether to ship features (budget left) or focus on reliability (budget burning). **Debug funnel:** the error-rate alarm says *something's* wrong → the checkout trace shows the failing Payments span → the log on that span says "Midtrans 503" → fix or fail over. All the alarms are on symptoms a customer feels, and each has a clear action.
:::

### 📝 Self-review checklist

- [ ] Alarms are on user-facing symptoms and are actionable
- [ ] There are few alarms, not one per metric
- [ ] I can trace an alarm down to a cause with metric → trace → log

::ai-review{task="design"}

::part[Toy Exercise]{n="3"}

:::exercise{path="exercises/m5/w7/03-evaluate-alarms" ai="no-ai" title="Decide which alarms fire"}
An alarm is a rule on a metric. Write `evaluate_alarms(readings, rules)` that checks the current metric readings against a set of alarm rules and returns exactly which alarms are firing — the logic CloudWatch runs every minute.
:::

:::hints
- Each rule has a `name`, a `metric`, an `op` (one of `">"`, `"<"`, `">="`, `"<="`) and a `threshold`.
- Look up the reading for the rule's metric; if that metric isn't in `readings`, the alarm can't fire — skip it.
- Compare with the right operator; collect the names of firing alarms and return them **sorted**.
:::

## ✅ Quick check

:::quiz
Why is an alarm more important than a beautiful dashboard for production?

Because in production nobody is watching the dashboard — it's 3 a.m. and everyone's asleep. A dashboard only helps when a human is looking; an alarm reaches out and *tells* a human that something is wrong, so it's the thing that makes you find out at all. Dashboards and the other signals are for investigating once the alarm has woken you.
:::

:::quiz
Why alarm on "error rate > 2%" rather than "CPU > 80%"?

Because error rate is a symptom users actually feel — requests are failing — and it's worth waking a human for. High CPU that isn't causing errors or slowness hurts no one, so paging on it trains people to ignore alarms (alert fatigue). Alarm on symptoms users feel and that a human can act on; keep causes like CPU as dashboards.
:::

## 📚 Keep learning

- [Google SRE Book: Monitoring & the Four Golden Signals](https://sre.google/sre-book/monitoring-distributed-systems/)
- [Google SRE Workbook: SLOs](https://sre.google/workbook/implementing-slos/)
- [Amazon CloudWatch: Alarms](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/AlarmThatSendsEmail.html)
