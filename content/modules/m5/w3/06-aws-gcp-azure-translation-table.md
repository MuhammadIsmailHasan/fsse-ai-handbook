---
title: "AWS ↔ GCP ↔ Azure Translation Table"
summary: Transfer your AWS knowledge to other clouds — equivalent services from compute to IaC, the conceptual differences that matter, and how to present multi-cloud experience honestly.
type: lesson
source: original
roles: { be: optional, fe: optional, fs: optional, ai: optional, ops: recommended }
durationMinutes: 60
tags: [aws, gcp, azure, cloud, multi-cloud]
---

::part[Learn the Concept]{n="1"}

## 🎯 What you'll learn

- The **equivalent services** across AWS, Google Cloud and Microsoft Azure
- **Conceptual differences** that trip people up (projects vs accounts, identity models, networking scope)
- How to talk about multi-cloud experience honestly in interviews

## 🔤 Key words

| Word | In simple words | Bahasa Indonesia |
|---|---|---|
| **Cloud provider** | A company renting you servers, databases and storage (AWS, Google Cloud, Azure) | Penyedia cloud |
| **Account / project / subscription** | The billing and access boundary — AWS calls it an account, GCP a project, Azure a subscription | Batas tagihan dan akses |
| **Resource group** (Azure) | A folder that holds related resources and can be deleted as one | Wadah sumber daya |
| **Managed service** | Something the provider runs for you (a database, a queue) | Layanan yang dikelola provider |
| **Serverless** | You deploy code or containers and the provider handles the servers | Tanpa mengelola server |
| **IaC (infrastructure as code)** | Describing your cloud setup in files instead of clicking | Infrastruktur sebagai kode |
| **Multi-cloud** | Using more than one provider on purpose | Memakai beberapa cloud |

## 🧠 The big idea

Clouds are like **car brands**. A steering wheel, brakes and a fuel gauge exist in all of them — just in slightly different places, with different names.

If you understand *why* a car has brakes (the concept), switching brands takes a few days, not months. So learn the concepts once on AWS, and translate the names when a job asks for GCP or Azure.

## ❓ Why it matters

Job ads in Indonesia mention AWS most often, but also GCP (common in startups and data teams) and Azure (common in big companies and banks). Remote roles in the US are the same story. Knowing the mapping lets you apply with confidence and get productive quickly.

Without it, one of two things happens:

- You think "I only know AWS", and skip a GCP role you could do.
- Or you write "multi-cloud" on your CV and then can't explain what a GCP project or an Azure resource group is.

## 📖 Step by step

### 1. The translation table

| Concept | AWS | Google Cloud | Azure |
|---|---|---|---|
| Account / billing boundary | Account (+ Organizations) | Project (+ Organization, folders) | Subscription (+ Management groups, resource groups) |
| Human identity & SSO | IAM Identity Center | Cloud Identity / Google Workspace + IAM | Microsoft Entra ID |
| Permissions | IAM policies, roles | IAM roles bound to principals on resources | Azure RBAC role assignments |
| Workload identity | IAM roles (instance/task roles, OIDC) | Service accounts, Workload Identity Federation | Managed identities, workload identity federation |
| Virtual machines | EC2 | Compute Engine | Virtual Machines |
| Serverless containers | App Runner, ECS on Fargate | **Cloud Run** | Container Apps |
| Kubernetes | EKS | GKE | AKS |
| Functions | Lambda | Cloud Run functions | Azure Functions |
| Managed PostgreSQL | RDS for PostgreSQL, Aurora | Cloud SQL, AlloyDB | Azure Database for PostgreSQL (Flexible Server) |
| Redis/Valkey | ElastiCache | Memorystore | Azure Cache for Redis / Azure Managed Redis |
| Object storage | S3 | Cloud Storage | Blob Storage |
| CDN | CloudFront | Cloud CDN | Azure Front Door / CDN |
| Private network | VPC (regional) | VPC (**global**, subnets regional) | Virtual Network (VNet, regional) |
| Firewall rules | Security groups, NACLs | VPC firewall rules (tags / service accounts) | Network security groups |
| Load balancer | ALB / NLB | Cloud Load Balancing | Application Gateway / Load Balancer / Front Door |
| DNS | Route 53 | Cloud DNS | Azure DNS |
| TLS certificates | ACM | Certificate Manager | Key Vault certificates / App Service certificates |
| Secrets | Secrets Manager, SSM Parameter Store | Secret Manager | Key Vault |
| Keys (KMS) | KMS | Cloud KMS | Key Vault keys |
| Queues | SQS | Pub/Sub, Cloud Tasks | Service Bus, Storage Queues |
| Events / scheduling | EventBridge, EventBridge Scheduler | Eventarc, Cloud Scheduler | Event Grid, Logic Apps / Functions timers |
| Container registry | ECR | Artifact Registry | Azure Container Registry |
| Logs & metrics | CloudWatch | Cloud Logging, Cloud Monitoring | Azure Monitor, Log Analytics |
| Tracing | X-Ray (and OpenTelemetry) | Cloud Trace | Application Insights |
| Audit logs | CloudTrail | Cloud Audit Logs | Activity Log |
| IaC (native) | CloudFormation, CDK | Infrastructure Manager (Terraform-based) | Bicep / ARM templates |
| IaC (portable) | Terraform / OpenTofu, Pulumi | same | same |
| Cost tools | Budgets, Cost Explorer | Budgets & alerts, Billing reports | Cost Management + Billing |
| AI platform | Bedrock, SageMaker | Vertex AI | Azure AI Foundry, Azure OpenAI |

Service names change occasionally — check the provider's current docs when you start a real project.

### 2. Differences that matter

These are the places where the "same car, different brand" idea breaks down: the pedals really are somewhere else, and assuming otherwise causes confusion in interviews.

| Topic | Difference |
|---|---|
| Boundaries | GCP **projects** are lightweight and common per app/environment; Azure groups everything in **resource groups** inside subscriptions |
| Networking | a GCP VPC is **global** (one VPC, subnets in many regions); AWS VPCs and Azure VNets are regional |
| Identity | Azure is built around **Entra ID** (company directory); GCP IAM binds roles on resources hierarchically; AWS uses JSON policies attached to principals and resources |
| Serverless containers | **Cloud Run** is very popular for "deploy a container, get an HTTPS URL, scale to zero" — similar to App Runner/ECS Fargate but with scale-to-zero by default |
| Free programs | each provider has different free tiers and trial credits — read the terms like you did for AWS |

### 3. RevoShop on each cloud

| RevoShop piece | AWS (this module) | GCP | Azure |
|---|---|---|---|
| API containers | ECS on Fargate + ALB | Cloud Run | Container Apps |
| PostgreSQL | RDS | Cloud SQL | Azure Database for PostgreSQL |
| Redis | ElastiCache / container | Memorystore | Azure Cache for Redis |
| Secrets | SSM / Secrets Manager | Secret Manager | Key Vault |
| Images | S3 + CloudFront | Cloud Storage + Cloud CDN | Blob Storage + Front Door |
| CI deploy identity | GitHub OIDC → IAM role | GitHub OIDC → Workload Identity Federation | GitHub OIDC → federated credential on a managed identity/app registration |

### Choosing your setup

Every option here is a trade-off:

| Approach | ✅ | ❌ |
|---|---|---|
| Deep on one cloud | real, defensible experience | fewer keyword matches |
| Shallow on three clouds | more keywords | weak interviews |
| Multi-cloud architecture for one app | vendor independence | much more complexity and cost — rarely worth it for small teams |

- ✅ Use the table to prepare for a job post that names GCP or Azure.
- ✅ Keep your code portable (containers, PostgreSQL, OpenTelemetry, Terraform).
- 🚫 Don't design RevoShop to run on three clouds at once.

## ⚠️ Common mistakes

- Assuming IAM concepts are identical (they're not — especially Azure RBAC + Entra ID).
- Forgetting GCP's global VPC when planning CIDRs.
- Listing every cloud on the CV without a single deployment on it.

:::revoshop
1. Fill in the "RevoShop on each cloud" table yourself before reading it again, then compare.
2. Pick the one job post from your Module 8 target list that mentions GCP or Azure. Write three sentences for your CV or interview that honestly connect your AWS RevoShop deployment to that cloud.
3. Stretch: deploy RevoShop's `prod` image to Google Cloud Run with a free trial or credits (no database — point `DATABASE_URL` at a temporary Cloud SQL or skip the DB-backed smoke tests). Write down the three biggest differences you noticed compared to ECS. **Tear it down the same day.**
:::

## 🏆 Best practices

- [ ] Learn concepts deeply on one provider, then map names.
- [ ] Prefer portable building blocks (containers, PostgreSQL, OIDC, Terraform, OpenTelemetry).
- [ ] Say "deployed on AWS; familiar with the GCP/Azure equivalents" — not "multi-cloud expert".
- [ ] Before a GCP/Azure interview, deploy one small container app there (Cloud Run / Container Apps) to back your claim.

::part[Explain & Design]{n="2"}

## 🗣️ Explain it

Explain the car-brands analogy to a friend who is worried they "only know AWS".

## 📐 Design it

A company in Jakarta uses Azure. Translate your Week 4 RevoShop design (ECS Fargate, ALB, RDS, SSM, S3 + CloudFront, GitHub OIDC deploys, CloudWatch) into Azure services, and list three things you'd need to learn first.

:::quiz
Show a possible translation

| AWS | Azure |
|---|---|
| ECS on Fargate + ALB | **Azure Container Apps** (built-in ingress with TLS) |
| RDS PostgreSQL | Azure Database for PostgreSQL – Flexible Server (private access via VNet integration) |
| SSM Parameter Store / Secrets Manager | **Key Vault**, referenced by Container Apps secrets |
| Task role | **Managed identity** with Key Vault and Blob Storage role assignments |
| S3 + CloudFront | Blob Storage (private) + Azure Front Door |
| GitHub OIDC → IAM role | GitHub OIDC → federated credential on a user-assigned managed identity, `azure/login` action |
| CloudWatch Logs/metrics | Azure Monitor + Log Analytics workspace, Application Insights |
| Region `ap-southeast-1` | Azure region in Southeast Asia or Indonesia Central (check availability) |

**Learn first:** (1) Entra ID + Azure RBAC role assignments and managed identities, (2) resource groups and subscription structure, (3) Container Apps environments, ingress and revisions.
:::

### 📝 Self-review checklist

- [ ] Concepts mapped, not just names
- [ ] Identity model differences noted
- [ ] Honest about depth of experience

::ai-review{task="design"}

::part[Practice]{n="3"}

## ✅ Quick check

:::quiz
What's the closest Google Cloud equivalent of "ECS on Fargate behind an ALB" for a simple HTTP API, and what's one feature it has by default?

**Cloud Run** — it gives an HTTPS endpoint and scales to zero when there's no traffic.
:::

:::quiz
Why do CIDR plans work differently on GCP?

A GCP VPC is global: one VPC can contain subnets in many regions, so address planning happens once across regions rather than per regional VPC.
:::


## 📚 Keep learning

- [Google Cloud: Compare AWS and Azure services to Google Cloud](https://cloud.google.com/docs/get-started/aws-azure-gcp-service-comparison)
- [Microsoft Learn: AWS to Azure services comparison](https://learn.microsoft.com/en-us/azure/architecture/aws-professional/)
