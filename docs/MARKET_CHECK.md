# Market Check

> **Checked:** 2026-09-13
> **Next suggested check:** 2026-12 (AI tooling changes fast — refresh every ~3 months)

This file records what the job market asks for, and how the handbook responds. Sources are mostly career blogs, surveys and job boards, so treat numbers as **directional**, not exact.

---

## 1. Findings

### Demand
- AI engineering is one of the fastest-growing and hardest-to-fill roles in 2026; roles requiring AI skills show a wage premium.
- In Indonesia, full-stack developers remain in high demand; listings increasingly mention LLM integration, RAG and AI coding tools.

### Skills employers ask for
| Area | Skills mentioned |
|---|---|
| Full-stack (Indonesia) | React / Vue / **Next.js**, Node.js / Java / **Python** / Go, **REST / GraphQL**, SQL / NoSQL, Git |
| Full-stack (new in 2026) | Using **AI coding tools** productively; building **LLM / RAG** features |
| AI engineer (applied) | LLM APIs, **function calling**, **structured outputs**, **RAG** (hybrid retrieval, reranking, vector DBs), **MCP**, **agents** (LangGraph, LangChain, LlamaIndex), **evals** (Ragas, DeepEval, LLM-as-judge), **observability** (Langfuse, LangSmith, Phoenix — traces vs spans), prompt caching, prompt injection defense, cost & latency optimization |
| AI engineer (ML-leaning listings) | Python, **PyTorch / TensorFlow**, statistics, fine-tuning, MLOps |
| Infra | **Docker, Kubernetes**, cloud (**AWS** / GCP / Azure), CI/CD |
| General | Deploying systems end-to-end (not only notebooks); communication |

### Developer tooling (Stack Overflow Developer Survey 2025)
- Python adoption grew notably (+7 percentage points year over year).
- ~23% of developers use AI agents at least weekly.
- Among developers building agents: Ollama and LangChain are the most used frameworks; Redis is widely used for agent memory/data.

### AWS Free Tier (affects Module 5)
- Accounts created **on or after July 15, 2025** get **$100 credits (up to $200)** instead of the old 12-month free tier.
- The Free plan **ends after 6 months or when credits run out**, whichever comes first.
- → Create the AWS account **only when starting Module 5**.

---

## 2. How the Handbook Responds

| Gap found | Change to the plan |
|---|---|
| Agent frameworks named in listings | Module 7 W6: build agent from scratch, then rebuild with **LangGraph** |
| Evals libraries named | Module 7 W5: **Ragas / DeepEval** lesson |
| AI observability | Module 7 W5: tracing with **Langfuse** (self-hostable, free) |
| ML basics still requested | Module 7 W0: **ML Foundations** (🔵 AI) — scikit-learn + tiny PyTorch, fine-tuning/LoRA concepts |
| Redis common | Module 5 W1 + Architecture F: **Redis** for caching and queues |
| GraphQL in Indonesian listings | Architecture F: hands-on **GraphQL** lesson |
| Multi-cloud mentions | Module 5 W3: **AWS ↔ GCP ↔ Azure** translation table |
| AWS + AI link | Module 7 W7: **Amazon Bedrock** lesson |
| Multi-agent, voice & browser agents | Module 7 W6: ⚪ optional deep dives |
| AI tools in full-stack listings | Module 6 (tool-agnostic AI-assisted development) + brain-first rule |
| End-to-end deployment valued | "Deploy early, deploy often" rule; every CareerPilot phase ends with a deploy |
| AWS free tier change | Module 5 warning + cost badges + cleanup checklists |

---

## 3. Sources

- [Interview Query — Demand for AI Engineers in 2026](https://www.interviewquery.com/p/ai-engineers-demand)
- [Second Talent — Most In-Demand AI Engineering Skills 2026](https://www.secondtalent.com/resources/most-in-demand-ai-engineering-skills-and-salary-ranges/)
- [DEV Community — What AI Engineer Job Ads Actually Screen For](https://dev.to/johnonlee/what-ai-engineer-job-ads-actually-screen-for-53lf)
- [Digital Applied — AI Developer Hiring 2026](https://www.digitalapplied.com/blog/ai-developer-hiring-skills-that-matter-2026)
- [2025 Stack Overflow Developer Survey — AI](https://survey.stackoverflow.co/2025/ai)
- [The New Stack — 23% of Devs Regularly Use AI Agents](https://thenewstack.io/23-of-devs-regularly-use-ai-agents-per-stack-overflow-survey/)
- [JobStreet — Full Stack Developer jobs in Indonesia](https://id.jobstreet.com/id/full-stack-developer-jobs)
- [JobStreet — AI Engineer jobs in Indonesia](https://id.jobstreet.com/id/ai-engineer-jobs)
- [IDstar — Most in-demand IT jobs 2026](https://idstar.co.id/pekerjaan-it-yang-paling-dicari/)
- [AWS — Free Tier $200 credits and 6-month free plan](https://aws.amazon.com/about-aws/whats-new/2025/07/aws-free-tier-credits-month-free-plan/)
- [AWS Free Tier FAQs](https://aws.amazon.com/free/free-tier-faqs/)

---

## 4. How to Refresh

Ask Claude: *"Redo the market check for the FSSE handbook"*. It should:
1. Search current job listings (Indonesia + remote) and recent surveys.
2. Compare with the course map in `IMPLEMENTATION_PLAN.md`.
3. Update this file (date, findings, sources) and propose plan changes for approval.
