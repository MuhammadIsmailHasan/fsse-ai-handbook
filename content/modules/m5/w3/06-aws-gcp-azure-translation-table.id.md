---
title: "Tabel Perbandingan AWS ↔ GCP ↔ Azure"
summary: Alihkan pengetahuan AWS ke cloud lain — layanan setara dari compute hingga IaC, perbedaan konsep yang penting, dan cara jujur berbicara tentang pengalaman multi-cloud.
sourceHash: dad1f55985e5
---

::part[Pelajari Konsepnya]{n="1"}

## 🎯 Yang akan kamu pelajari

- Layanan **setara** di AWS, Google Cloud, dan Microsoft Azure
- **Perbedaan konsep** yang sering membingungkan (project vs account, model identity, cakupan network)
- Cara jujur berbicara tentang pengalaman multi-cloud saat interview

## 🔤 Istilah penting

| Istilah | Artinya (sederhana) |
|---|---|
| **Cloud provider** | Perusahaan yang menyewa server, database, dan penyimpanan kepada kamu (AWS, Google Cloud, Azure) |
| **Account / project / subscription** | Batas untuk tagihan dan akses — AWS menyebutnya account, GCP menyebutnya project, Azure menyebutnya subscription |
| **Resource group** (Azure) | Folder yang menyimpan resource terkait dan bisa dihapus sekaligus |
| **Managed service** | Layanan yang dijalankan provider untuk kamu (database, antrian) |
| **Serverless** | Kamu deploy code atau container, provider menangani servernya |
| **IaC (infrastructure as code)** | Mendeskripsikan setup cloud kamu dalam file, bukan klik-klikan |
| **Multi-cloud** | Memakai lebih dari satu provider dengan sengaja |

## 🧠 Ide besarnya

Cloud itu seperti **merek mobil yang berbeda**. Setir, rem, dan pengukur bahan bakar ada di semua — cuma tempatnya sedikit berbeda, namanya beda.

Kalau kamu paham *kenapa* mobil punya rem (konsepnya), ganti merek cuma butuh beberapa hari, bukan berbulan-bulan. Jadi pelajari konsep sekali di AWS, lalu terjemahkan namanya saat ada job yang minta GCP atau Azure.

## ❓ Kenapa ini penting

Iklan job di Indonesia paling sering sebutkan AWS, tapi juga GCP (sering di startup dan tim data) dan Azure (sering di perusahaan besar dan bank). Role remote di US sama saja. Tahu perbandingannya membuat kamu bisa melamar dengan percaya diri dan produktif dengan cepat.

Tanpa itu, dua hal bisa terjadi:

- Kamu pikir "aku cuma tahu AWS", lalu skip job GCP yang sebenarnya bisa kamu kerjakan.
- Atau kamu tulis "multi-cloud" di CV terus tidak bisa jelaskan apa itu GCP project atau Azure resource group.

## 📖 Langkah demi langkah

### 1. Tabel perbandingan

| Konsep | AWS | Google Cloud | Azure |
|---|---|---|---|
| Account / batas tagihan | Account (+ Organizations) | Project (+ Organization, folders) | Subscription (+ Management groups, resource groups) |
| Identity pengguna & SSO | IAM Identity Center | Cloud Identity / Google Workspace + IAM | Microsoft Entra ID |
| Permission | IAM policies, roles | IAM roles terikat ke principal di resource | Azure RBAC role assignments |
| Workload identity | IAM roles (instance/task roles, OIDC) | Service accounts, Workload Identity Federation | Managed identities, workload identity federation |
| Virtual machine | EC2 | Compute Engine | Virtual Machines |
| Serverless container | App Runner, ECS on Fargate | **Cloud Run** | Container Apps |
| Kubernetes | EKS | GKE | AKS |
| Function | Lambda | Cloud Run functions | Azure Functions |
| PostgreSQL terkelola | RDS for PostgreSQL, Aurora | Cloud SQL, AlloyDB | Azure Database for PostgreSQL (Flexible Server) |
| Redis/Valkey | ElastiCache | Memorystore | Azure Cache for Redis / Azure Managed Redis |
| Object storage | S3 | Cloud Storage | Blob Storage |
| CDN | CloudFront | Cloud CDN | Azure Front Door / CDN |
| Private network | VPC (regional) | VPC (**global**, subnets regional) | Virtual Network (VNet, regional) |
| Firewall rules | Security groups, NACLs | VPC firewall rules (tags / service accounts) | Network security groups |
| Load balancer | ALB / NLB | Cloud Load Balancing | Application Gateway / Load Balancer / Front Door |
| DNS | Route 53 | Cloud DNS | Azure DNS |
| TLS certificate | ACM | Certificate Manager | Key Vault certificates / App Service certificates |
| Secrets | Secrets Manager, SSM Parameter Store | Secret Manager | Key Vault |
| Keys (KMS) | KMS | Cloud KMS | Key Vault keys |
| Antrian | SQS | Pub/Sub, Cloud Tasks | Service Bus, Storage Queues |
| Events / scheduling | EventBridge, EventBridge Scheduler | Eventarc, Cloud Scheduler | Event Grid, Logic Apps / Functions timers |
| Container registry | ECR | Artifact Registry | Azure Container Registry |
| Logs & metrics | CloudWatch | Cloud Logging, Cloud Monitoring | Azure Monitor, Log Analytics |
| Tracing | X-Ray (dan OpenTelemetry) | Cloud Trace | Application Insights |
| Audit logs | CloudTrail | Cloud Audit Logs | Activity Log |
| IaC (native) | CloudFormation, CDK | Infrastructure Manager (Terraform-based) | Bicep / ARM templates |
| IaC (portable) | Terraform / OpenTofu, Pulumi | sama | sama |
| Cost tools | Budgets, Cost Explorer | Budgets & alerts, Billing reports | Cost Management + Billing |
| AI platform | Bedrock, SageMaker | Vertex AI | Azure AI Foundry, Azure OpenAI |

Nama service berubah sesekali — cek dokumentasi provider terbaru saat mulai proyek sungguhan.

### 2. Perbedaan yang penting

Ini tempat di mana ide "mobil sama, merek beda" rusak: pedalnya memang di tempat lain, dan anggapan salah bisa bingung saat interview.

| Topik | Perbedaannya |
|---|---|
| Batas | **Project** GCP ringan dan umum per app/environment; Azure kelompokkan segalanya di **resource groups** dalam subscription |
| Network | VPC GCP **global** (satu VPC, subnets di banyak region); VPC AWS dan VNet Azure adalah regional |
| Identity | Azure dibangun seputar **Entra ID** (direktori perusahaan); IAM GCP ikat role di resource secara hirarki; AWS pakai JSON policies yang terpasang ke principal dan resource |
| Serverless container | **Cloud Run** sangat populer untuk "deploy container, dapat URL HTTPS, scale ke nol" — mirip App Runner/ECS Fargate tapi scale-to-zero default |
| Program gratis | setiap provider punya free tier dan trial credit berbeda — baca syaratnya seperti kamu lakukan untuk AWS |

### 3. RevoShop di setiap cloud

| Bagian RevoShop | AWS (modul ini) | GCP | Azure |
|---|---|---|---|
| API container | ECS on Fargate + ALB | Cloud Run | Container Apps |
| PostgreSQL | RDS | Cloud SQL | Azure Database for PostgreSQL |
| Redis | ElastiCache / container | Memorystore | Azure Cache for Redis |
| Secrets | SSM / Secrets Manager | Secret Manager | Key Vault |
| Gambar | S3 + CloudFront | Cloud Storage + Cloud CDN | Blob Storage + Front Door |
| CI deploy identity | GitHub OIDC → IAM role | GitHub OIDC → Workload Identity Federation | GitHub OIDC → federated credential di managed identity/app registration |

### Memilih setup-mu

Setiap pilihan punya trade-off:

| Pendekatan | ✅ | ❌ |
|---|---|---|
| Dalam satu cloud | pengalaman nyata, bisa dipertahankan | cocok keyword lebih sedikit |
| Tipis di tiga cloud | lebih banyak keyword | interview lemah |
| Arsitektur multi-cloud untuk satu app | independen vendor | jauh lebih rumit dan mahal — jarang layak untuk tim kecil |

- ✅ Pakai tabel untuk bersiap interview job yang sebutkan GCP atau Azure.
- ✅ Jaga code tetap portable (container, PostgreSQL, OpenTelemetry, Terraform).
- 🚫 Jangan rancang RevoShop untuk jalan di tiga cloud sekaligus.

## ⚠️ Kesalahan umum

- Anggap konsep IAM identik (tidak — terutama Azure RBAC + Entra ID).
- Lupa VPC global GCP saat rencana CIDR.
- Tulis setiap cloud di CV tanpa satu deploy-pun di sana.

:::revoshop
1. Isi tabel "RevoShop di setiap cloud" sendiri sebelum baca lagi, terus bandingkan.
2. Pilih satu job post dari daftar target Module 8-mu yang sebutkan GCP atau Azure. Tulis tiga kalimat untuk CV atau interview yang jujur hubungkan AWS RevoShop deploy-mu ke cloud itu.
3. Stretch: deploy image RevoShop `prod` ke Google Cloud Run dengan free trial atau credit (tanpa database — arahkan `DATABASE_URL` ke Cloud SQL sementara atau skip smoke test berbasis DB). Tulis tiga perbedaan terbesar yang kamu lihat dibanding ECS. **Hapus hari yang sama.**
:::

## 🏆 Praktik terbaik

- [ ] Pelajari konsep dalam satu provider, lalu terjemahkan namanya.
- [ ] Lebih suka building block portable (container, PostgreSQL, OIDC, Terraform, OpenTelemetry).
- [ ] Bilang "deploy di AWS; kenal equivalentnya GCP/Azure" — bukan "ahli multi-cloud".
- [ ] Sebelum interview GCP/Azure, deploy satu app container kecil di sana (Cloud Run / Container Apps) untuk back up klaim-mu.

::part[Jelaskan & Rancang]{n="2"}

## 🗣️ Jelaskan

Jelaskan analogi merek mobil ke teman yang khawatir "aku cuma tahu AWS".

## 📐 Rancang

Perusahaan di Jakarta pakai Azure. Terjemahkan desain RevoShop minggu 4-mu (ECS Fargate, ALB, RDS, SSM, S3 + CloudFront, GitHub OIDC deploy, CloudWatch) ke service Azure, lalu list tiga hal yang perlu kamu pelajari dulu.

:::quiz
Lihat contoh terjemahan

| AWS | Azure |
|---|---|
| ECS on Fargate + ALB | **Azure Container Apps** (ingress built-in dengan TLS) |
| RDS PostgreSQL | Azure Database for PostgreSQL – Flexible Server (akses private via VNet integration) |
| SSM Parameter Store / Secrets Manager | **Key Vault**, direferensi oleh secrets Container Apps |
| Task role | **Managed identity** dengan Key Vault dan Blob Storage role assignments |
| S3 + CloudFront | Blob Storage (private) + Azure Front Door |
| GitHub OIDC → IAM role | GitHub OIDC → federated credential di managed identity yang ditugaskan user, aksi `azure/login` |
| CloudWatch Logs/metrics | Azure Monitor + Log Analytics workspace, Application Insights |
| Region `ap-southeast-1` | Region Azure di Southeast Asia atau Indonesia Central (cek ketersediaan) |

**Pelajari dulu:** (1) Entra ID + Azure RBAC role assignments dan managed identities, (2) struktur resource group dan subscription, (3) lingkungan Container Apps, ingress dan revision.
:::

### 📝 Checklist review mandiri

- [ ] Konsep terpetakan, bukan cuma nama
- [ ] Perbedaan model identity dicatat
- [ ] Jujur tentang kedalaman pengalaman

::ai-review{task="design"}

::part[Latihan Kecil]{n="3"}

## ✅ Cek cepat

:::quiz
Equivalent Google Cloud terdekat dari "ECS on Fargate di belakang ALB" untuk simple HTTP API apa, dan fitur apa yang ia punya by default?

**Cloud Run** — ia memberi endpoint HTTPS dan scale ke nol saat tidak ada traffic.
:::

:::quiz
Kenapa rencana CIDR beda di GCP?

VPC GCP adalah global: satu VPC bisa punya subnets di banyak region, jadi rencana alamat terjadi sekali di region, bukan per VPC regional.
:::

## 📚 Lanjut belajar

- [Google Cloud: Compare AWS and Azure services to Google Cloud](https://cloud.google.com/docs/get-started/aws-azure-gcp-service-comparison)
- [Microsoft Learn: AWS to Azure services comparison](https://learn.microsoft.com/en-us/azure/architecture/aws-professional/)
