# Infosys CIS Cloud Shield — End User Guide

**Version 1.0 · May 2026**  
**Infosys Cloud Infrastructure Services (CIS)**

---

## Table of Contents

1. [Overview](#1-overview)
2. [Getting Started — Login](#2-getting-started--login)
3. [Sidebar Configuration](#3-sidebar-configuration)
4. [Module 1 — Credential Intelligence](#4-module-1--credential-intelligence)
5. [Module 2 — Backup Intelligence](#5-module-2--backup-intelligence)
6. [Module 3 — Auto-Remediation Loop](#6-module-3--auto-remediation-loop)
7. [ServiceNow Integration](#7-servicenow-integration)
8. [Troubleshooting](#8-troubleshooting)
9. [FAQ](#9-faq)
10. [Appendix — Required AWS Permissions](#10-appendix--required-aws-permissions)

---

## 1. Overview

**CIS Cloud Shield** is an agentic AI platform built by Infosys Cloud Infrastructure Services to address two critical enterprise security challenges:

| Challenge | Scale | CIS Cloud Shield Capability |
|-----------|-------|----------------------------|
| Hardcoded credentials in AWS-hosted applications | ~1,200 instances identified | Detect · Assess risk · Rotate · Prevent recurrence |
| Applications without immutable backup | ~250 applications | Identify gaps · Design solution · Track remediation via ServiceNow |

### How It Works

The platform uses **four specialised AI agents** powered by OpenAI GPT-4o that work together in sequence:

```
Scanner Agent  →  Risk Agent  →  Remediation Agent  →  Prevention Agent
     ↓                                                        ↓
  Finds credentials                               Stops future exposure
```

For backup gaps, the platform integrates directly with **ServiceNow** to raise, track, and close incidents automatically.

For detected vulnerabilities, the **Auto-Remediation Loop** (Module 3) runs a continuous agentic cycle that opens a ServiceNow incident, investigates the root cause, executes remediation, and closes the ticket — all without manual intervention.

---

## 2. Getting Started — Login

### Step 1: Open the Application

Navigate to the Streamlit Cloud URL provided by your administrator.

### Step 2: Sign In

| Field | Value |
|-------|-------|
| **Username** | `admin` |
| **Password** | `Infosys@123` |

Click **Sign In**.

> ⚠️ **Note for administrators:** These are demo credentials. Replace with your organisation's identity provider integration before production deployment. Contact the CIS team for SSO/SAML configuration options.

### Step 3: Verify You Are Logged In

After successful login you will see the **CIS Cloud Shield** header bar at the top of every page, showing your username in the top-right corner.

---

## 3. Sidebar Configuration

The sidebar on the left controls all platform integrations. Configure it before running any analysis.

### 3.1 OpenAI Configuration

| Field | Description |
|-------|-------------|
| **API Key** | Your OpenAI API key (`sk-...`). Required for all AI agent features. |
| **Model** | Select the GPT model. `gpt-4o` is recommended for best analysis quality. `gpt-4o-mini` is faster and lower cost. |

> 💡 **Tip:** If the platform is deployed on Streamlit Cloud with secrets configured, the API key is pre-loaded and you will see a green **"OpenAI key loaded from secrets ✓"** message. No manual entry is needed.

### 3.2 ServiceNow Configuration

| Field | Description | Example |
|-------|-------------|---------|
| **Instance URL** | Your ServiceNow instance base URL | `https://dev218436.service-now.com` |
| **Username** | ServiceNow user with incident/change write access | `admin` |
| **Password** | ServiceNow password | _(your password)_ |

Click **🔗 Test SNOW Connection** to verify the connection before proceeding. A green success message confirms connectivity.

### 3.3 AWS Account Connection

| Field | Description |
|-------|-------------|
| **Access Key ID** | IAM user access key (`AKIA...`) |
| **Secret Access Key** | IAM user secret key |
| **Session Token** | Only required for temporary credentials via STS AssumeRole. Leave blank for permanent keys. |
| **Region** | Primary AWS region to scan (e.g. `us-east-1`) |

Click **🔌 Connect to AWS**. The platform calls AWS STS to verify your identity and displays your **Account ID** on success.

> 🔒 **Security note:** Credentials are held in your Streamlit session only and are never written to disk or logs. For production deployments, inject credentials via Streamlit Cloud Secrets (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`) rather than typing them in the UI.

### 3.4 Environment Overview Panel

The bottom of the sidebar shows a live summary of the current data:

| Metric | Description |
|--------|-------------|
| Findings | Total credential findings loaded (mock: 1,200) |
| Apps | Total applications in backup inventory (mock: 250) |
| Critical / High | Credential findings by severity |
| No Backup / Partial | Application backup gap counts |

---

## 4. Module 1 — Credential Intelligence

**Tab:** 🔐 Credential Intelligence

This module identifies hardcoded credentials across your AWS environment and provides AI-generated remediation guidance.

### 4.1 KPI Dashboard

At the top of the tab, five key metrics are shown:

| Metric | What It Means |
|--------|---------------|
| **Total Findings** | All credential instances detected (1,200 in demo) |
| **Critical** | Credentials requiring immediate rotation (AWS root keys, SSH private keys, live payment keys) |
| **High** | High-priority findings (DB passwords, JWT secrets, API keys) — 72-hour SLA |
| **Medium** | Lower-risk findings (SMTP passwords, internal tokens) |
| **Apps Affected** | Number of distinct applications with at least one finding |

### 4.2 AI Agent Orchestration — Running the Analysis

The four agent cards show each agent's current status:

| Status | Colour | Meaning |
|--------|--------|---------|
| `idle` | Grey | Waiting to run |
| `active` | Blue glow | Currently analysing |
| `done` | Green | Analysis complete |

**To run the full AI analysis:**

1. Ensure your OpenAI API key is set in the sidebar.
2. Click **🚀 Launch AI Security Analysis**.
3. The four agents will run in sequence. Each streams its output live as it thinks.
4. Results appear in the **Agent Analysis Output** expander below the button.

**What each agent produces:**

| Agent | Output |
|-------|--------|
| **🔍 Scanner Agent** | Executive summary, top 5 critical findings, attack vectors, 24-hour action items |
| **⚖️ Risk Agent** | Risk score (0–100), compliance gap matrix (PCI-DSS, SOC2, CIS), financial exposure estimate, remediation SLAs (P0–P3) |
| **🔧 Remediation Agent** | Python/boto3 migration script for AWS Secrets Manager, IAM key rotation Lambda skeleton, before/after code patterns, 4-week phased schedule |
| **🛡️ Prevention Agent** | Pre-commit hook config (detect-secrets), AWS SCP policy JSON, GitHub Actions CI/CD scan step, GuardDuty alert rules, developer training topics |

> 💡 **Tip:** Each agent receives context from the previous agent, so the analysis is progressive and coherent — the Prevention Agent understands what the Scanner found.

### 4.3 Live AWS IAM Scan

> Requires: AWS account connected in sidebar.

Three scan buttons are available:

| Button | What It Does | Time |
|--------|-------------|------|
| **🔍 Scan IAM Credential Report** | Generates the AWS IAM credential report and flags: root active keys, users without MFA, stale passwords (>90 days), stale access keys (>90/180 days) | 15–30 seconds |
| **🔐 List Secrets Manager** | Lists all secrets in AWS Secrets Manager with rotation status and last-changed date | 5–10 seconds |
| **🛡️ Security Hub Findings** | Fetches all active failed security controls from AWS Security Hub | 10–20 seconds |

**Reading IAM findings:**

| Severity | Credential Type | Action Required |
|----------|----------------|-----------------|
| CRITICAL | Root Access Key | Delete immediately — AWS best practice violation |
| CRITICAL | Root Account — No MFA | Enable MFA on root account today |
| CRITICAL | Stale Access Key (>180 days) | Rotate within 24 hours |
| HIGH | IAM User — No MFA | Enable MFA — P1 priority |
| HIGH | Stale Access Key (>90 days) | Rotate within 72 hours |
| HIGH | Stale Console Password (>90 days) | Disable or reset — P1 priority |

### 4.4 Credential Findings Table

The findings table shows all 1,200 simulated (or live IAM) findings. Use the filters to narrow down:

| Filter | Options |
|--------|---------|
| **Severity** | CRITICAL, HIGH, MEDIUM, LOW (multi-select) |
| **Environment** | production, staging, development, qa |
| **Credential Type** | AWS Access Key ID, Database Password, API Key, etc. |

The table shows up to 60 rows at a time. Key columns:

| Column | Description |
|--------|-------------|
| Finding ID | Unique identifier (e.g. `CRED-10042`) |
| Application | The service or application where the credential was found |
| Environment | Which environment the finding is in |
| Credential Type | Category of the exposed secret |
| Severity | Risk level |
| File Location | The file path where the credential was found (e.g. `.env`, `docker-compose.yml`) |
| Status | Open / In Progress / Resolved |
| Commit Author | The developer whose commit introduced the credential |

### 4.5 Raising ServiceNow Change Requests

For critical credential findings, the platform can automatically create **Emergency Change Requests** in ServiceNow:

1. Set the **Max tickets to create** slider (1–20).
2. Click **📝 Create SNOW Change Requests (Critical Findings)**.
3. The platform creates one change request per CRITICAL finding with full context: finding details, file location, commit author, and step-by-step remediation instructions.
4. Results show ticket numbers as clickable ServiceNow links.

### 4.6 Analytics Charts

Three charts provide a visual breakdown of the finding landscape:

| Chart | What It Shows |
|-------|--------------|
| **Findings by Severity** (pie) | Proportion of CRITICAL / HIGH / MEDIUM / LOW |
| **Top Credential Types** (bar) | Which credential types appear most often |
| **Most Exposed Applications** (bar) | Which applications have the most findings |
| **Environment × Severity Heatmap** | Which environments are most exposed by severity |

---

## 5. Module 2 — Backup Intelligence

**Tab:** 💾 Backup Intelligence

This module identifies applications that lack immutable backup coverage and manages remediation through ServiceNow.

### 5.1 KPI Dashboard

| Metric | Description |
|--------|-------------|
| **Total Apps** | Applications in scope (250 in demo) |
| **Protected** | Applications with full backup coverage |
| **Partial Backup** | Applications with ad-hoc or incomplete backup — need upgrade |
| **Unprotected** | Applications with no backup whatsoever — highest priority |
| **Immutable Backups** | Applications where backup storage has WORM/Object Lock protection |

### 5.2 Coverage Charts

| Chart | What It Shows |
|-------|--------------|
| **Backup Status Distribution** (pie) | Protected / Partial / Unprotected breakdown |
| **Coverage by App Type** (stacked bar) | Backup status per resource type (EC2, RDS, ECS, Lambda, S3, DynamoDB) |
| **Critical Apps Without Full Backup** | Mission Critical and Business Critical apps that are unprotected |

### 5.3 Application Inventory Table

Filter the 250-application inventory using:

| Filter | Options |
|--------|---------|
| **Backup Status** | Protected, Partial, Unprotected |
| **Criticality** | Mission Critical, Business Critical, Standard, Low |
| **App Type** | EC2 Instance, RDS Database, ECS Service, Lambda Function, S3, DynamoDB |

Key columns in the table:

| Column | Description |
|--------|-------------|
| App ID | Unique application identifier |
| Type | AWS resource type |
| Environment | Production / Staging / Development |
| Criticality | Business impact rating |
| Backup Status | Protected / Partial / Unprotected |
| Immutable | Whether WORM-protected backup is in place |
| RPO Requirement | Target recovery point objective |
| RTO Requirement | Target recovery time objective |
| SNOW Ticket | ServiceNow ticket number once raised (auto-populated) |

### 5.4 Live AWS Backup Scan

> Requires: AWS account connected in sidebar.

| Button | What It Scans | Time |
|--------|--------------|------|
| **📦 Scan Backup Coverage** | EC2, RDS, S3 (Object Lock), DynamoDB (PITR) against AWS Backup protected resource list | 30–90 seconds |
| **📋 List Backup Plans** | All AWS Backup plans with creation date and last execution | 5 seconds |
| **🔒 Check Vault Lock Status** | All backup vaults — which have WORM lock enabled, retention settings | 5 seconds |

After scanning, a **live coverage chart** shows real backup status for your actual AWS account. Use the **"Show gaps only"** checkbox to filter to unprotected/partial resources immediately.

### 5.5 Creating ServiceNow Incidents

**For mock data (demo mode):**

1. Set **Max tickets to create** (1–50).
2. Choose **Prioritise by**:
   - *Mission Critical first* — focuses on highest-impact applications
   - *All Unprotected first* — focuses on applications with zero backup
   - *All gaps* — processes both Unprotected and Partial
3. Click **🎫 Create ServiceNow Incidents for Backup Gaps**.
4. A progress bar tracks creation. Each incident includes: app details, current backup state, RPO/RTO requirements, and recommended solution (AWS Backup + Vault Lock).
5. Created tickets appear in the **ServiceNow Tickets** expander with clickable links.

**For live AWS data:**

After running a live backup scan, click **🎫 Raise SNOW Incidents for Live Backup Gaps** to create tickets for real unprotected resources in your account.

**Incident priority mapping:**

| Application Criticality | Data Classification | Resulting Priority |
|------------------------|--------------------|--------------------|
| Mission Critical | PII / Financial / PHI | Priority 1 — Critical |
| Mission Critical | Internal / Public | Priority 2 — High |
| Business Critical | Any | Priority 2 — High |
| Standard / Low | Any | Priority 3 — Moderate |

### 5.6 Backup Technology Comparison

Four tabs compare the major backup technologies evaluated for this environment:

| Technology | Best For |
|-----------|---------|
| **AWS Backup** | AWS-native workloads; zero infrastructure management; org-wide policies |
| **Veeam Backup for AWS** | Multi-cloud or hybrid environments; granular file-level recovery |
| **Commvault** | Complex enterprise environments; SAP/Oracle/Exchange; FedRAMP compliance |
| **AWS S3 Object Lock** | Data archive and compliance (SEC 17a-4); strongest WORM guarantee |

Each tab shows: RPO, RTO, immutability mechanism, encryption, compliance certifications, monitoring approach, recovery testing method, operational model, cost model, strengths, and limitations.

### 5.7 RPO / RTO Matrix

A heatmap shows the distribution of applications by their RPO and RTO requirements. Use this to:
- Identify which backup technology tiers are needed
- Prioritise which applications need the most capable backup solutions
- Validate that existing backup frequency meets RPO targets

### 5.8 Operational Support Model

Three operational runbook pillars are documented:

| Pillar | Cadence | Key Activities |
|--------|---------|---------------|
| **Daily Operations** | Every business day | Backup job monitoring, failed backup alerting, capacity trending, compliance check |
| **Weekly / Monthly / Quarterly** | Scheduled | Restore testing (10% sample weekly), runbook refresh, DR tabletop exercise quarterly |
| **Tooling & Automation** | Ongoing | AWS Backup Audit Manager, Terraform IaC, tag-driven auto-enrolment, ServiceNow CMDB sync |

---

## 6. Module 3 — Auto-Remediation Loop

**Tab:** 🔄 Auto-Remediation Loop

This module runs a **continuous, automated, 4-phase agent cycle** that takes a detected credential vulnerability from discovery through to ServiceNow incident closure without human intervention.

### 6.1 The Agent Handoff Flow

```
┌─────────────────────────────────────────────────────┐
│  Vulnerability Detected                              │
│           ↓                                          │
│  ┌──────────────────┐                               │
│  │   INC Agent      │  Creates SNOW incident         │
│  │                  │  Classifies severity & SLA      │
│  │                  │  Writes handoff note            │
│  └────────┬─────────┘                               │
│           │ handoff                                  │
│  ┌────────▼─────────┐                               │
│  │ Dispatcher Agent │  Root cause analysis            │
│  │                  │  Scope & attack vector          │
│  │                  │  Detailed remediation plan      │
│  └────────┬─────────┘                               │
│           │                                          │
│  ┌────────▼─────────┐                               │
│  │ Remediator Agent │  Executes remediation steps    │
│  │                  │  Provides AWS CLI/Python code   │
│  │                  │  Validates the fix              │
│  └────────┬─────────┘                               │
│           │ handoff back                             │
│  ┌────────▼─────────┐                               │
│  │   INC Agent      │  Writes resolution note        │
│  │                  │  Updates SNOW incident          │
│  │                  │  CLOSES the incident ✅         │
│  └──────────────────┘                               │
│           ↓                                          │
│     Next finding → loop repeats                      │
└─────────────────────────────────────────────────────┘
```

### 6.2 Configuration

Before starting the loop, configure the following:

| Setting | Description | Recommendation |
|---------|-------------|---------------|
| **Finding source** | *Mock data (demo)* uses the 1,200 simulated findings. *Live IAM scan* uses results from Tab 1's IAM scan (run it first). | Use *Mock data* for first-time demos |
| **Findings to process** | How many findings to run through the loop (1–20) | Start with 3 for a demo |
| **Target severity** | Which severities to include | CRITICAL + HIGH for demos |

> ⚠️ **Prerequisites:**
> - OpenAI API key must be set (sidebar)
> - ServiceNow credentials must be set (sidebar)
> - Both buttons become active once these are configured

### 6.3 Running the Loop

Click **▶️ Start Auto-Remediation Loop**.

Each finding appears in an expandable section showing all four agent phases in real time. Agent output is colour-coded:

| Agent | Colour | What to Watch For |
|-------|--------|-------------------|
| 🎫 INC Agent | Blue | Incident classification, SLA declaration, handoff note |
| 📡 Dispatcher Agent | Orange | Root cause reasoning, scope assessment, step-by-step remediation plan |
| 🔧 Remediator Agent | Purple | Specific AWS CLI commands, before/after code, validation output |
| ✅ INC Agent (closure) | Green | Resolution summary, root cause one-liner, closure declaration |

A real ServiceNow ticket is created between Phase 1 and Phase 2, and closed after Phase 4. The ticket number appears as a clickable link to ServiceNow.

### 6.4 Loop Summary

After all findings are processed, a summary table shows:

| Column | Description |
|--------|-------------|
| Finding | The finding ID that was processed |
| Severity | CRITICAL / HIGH / MEDIUM |
| Type | Credential type |
| Application | The affected application |
| SNOW Ticket | The incident number created and closed |
| ServiceNow link | Clickable deep link to the resolved incident |
| Status | ✅ Resolved & Closed |

---

## 7. ServiceNow Integration

### Incident States Used

| SNOW State Code | Label | When Set |
|----------------|-------|----------|
| `1` | New | On incident creation |
| `2` | In Progress | When Dispatcher Agent takes over |
| `6` | Resolved | After Remediator completes the fix |

### Incident Fields Populated

| SNOW Field | Source |
|-----------|--------|
| Short Description | Auto-generated: `[AUTO-REMEDIATION] <Type> — <App> — <Severity>` |
| Description | Full finding details: app, environment, file location, detected date |
| Work Notes | Dispatcher investigation + Remediator actions |
| Close Notes | INC Agent closure summary |
| Urgency | 1 (Critical) for CRITICAL findings, 2 (High) for others |
| Impact | 1 for PII/Financial/PHI data, 2 for others |
| Priority | Calculated from Urgency × Impact matrix |
| Category | Cloud Services |
| Subcategory | Backup & Recovery (backup incidents) or Security (credential incidents) |
| Assignment Group | Cloud Infrastructure |

### Viewing Tickets in ServiceNow

1. Navigate to your ServiceNow instance (`https://dev218436.service-now.com`)
2. Go to **Incident → All** or use the direct links in the CIS Cloud Shield results tables.
3. Filter by **Assignment Group = Cloud Infrastructure** and **Short Description contains [AUTO-REMEDIATION]** or **[BACKUP GAP]**.

---

## 8. Troubleshooting

### Login Issues

| Symptom | Fix |
|---------|-----|
| "Invalid credentials" | Use exactly `admin` / `Infosys@123` (case-sensitive) |
| Page reloads but doesn't log in | Clear browser cache and retry |

### OpenAI Issues

| Symptom | Fix |
|---------|-----|
| "Enter your OpenAI API key" error | Add the key in the sidebar under **🤖 OpenAI** |
| Agent output stops mid-stream | Likely an API rate limit — wait 30 seconds and retry |
| `RateLimitError` | Switch to `gpt-4o-mini` in the model selector for lower consumption |
| `AuthenticationError` | Your API key is invalid or expired — generate a new one at platform.openai.com |

### AWS Connection Issues

| Symptom | Fix |
|---------|-----|
| "Connection failed: NoCredentialsError" | Enter Access Key ID and Secret Access Key in the sidebar |
| "Connection failed: InvalidClientTokenId" | Access Key ID is incorrect — double-check it |
| "Connection failed: AccessDenied" | The IAM user lacks `sts:GetCallerIdentity` — attach the permission policy in the Appendix |
| IAM scan returns 0 findings | The credential report may still be generating — wait 30 seconds and retry |
| Backup scan returns 0 resources | Verify the region selected matches where your resources are deployed |
| Security Hub returns 0 findings | Security Hub may not be enabled in this region — enable it in the AWS Console |

### ServiceNow Issues

| Symptom | Fix |
|---------|-----|
| "HTTP 401" on test connection | Check username and password |
| "HTTP 403" on ticket creation | The ServiceNow user lacks write access to the `incident` or `change_request` tables — contact your SNOW admin |
| Ticket created but state not updating | The `state` field may use different codes in your SNOW instance — check with your admin |
| Incident created with empty fields | Ensure the ServiceNow user has the `itil` role |

---

## 9. FAQ

**Q: Is the data shown real or simulated?**  
A: By default (without AWS credentials connected), all findings and application data are simulated using realistic mock data. Once you connect an AWS account, the Live Scan buttons fetch real data from your account.

**Q: Can I run this against multiple AWS accounts?**  
A: Yes. Disconnect and reconnect with different credentials in the sidebar. Each connection replaces the previous session's live scan results. For multi-account scanning at scale, contact the CIS team for the enterprise deployment configuration.

**Q: Does the Remediator Agent actually rotate credentials in my AWS account?**  
A: No. The agents generate remediation *guidance and code* — they do not execute changes in your account. All AWS API calls are read-only (describe, list, get). Actual remediation requires a human or a separate automation pipeline to run the generated scripts.

**Q: How many OpenAI tokens does a full analysis consume?**  
A: A single run of the 4 agents uses approximately 4,000–6,000 tokens (input + output). The Auto-Remediation Loop uses approximately 2,500–4,000 tokens per finding. With `gpt-4o` pricing, a full demo (3 findings in the loop + credential analysis) costs roughly $0.15–0.25 USD.

**Q: Can I export the findings or reports?**  
A: Tables can be downloaded as CSV using the download icon in the top-right corner of each Streamlit dataframe. For formal PDF reports, contact the CIS team — a reporting module is on the roadmap.

**Q: What happens to my AWS credentials?**  
A: Credentials are stored only in your Streamlit browser session (in-memory). They are not written to disk, logged, or transmitted to any service other than AWS. The session clears when you close the browser tab or your session expires.

**Q: Can I add more users to the login page?**  
A: The current demo login supports a single hardcoded `admin` account. For multi-user authentication with LDAP/SAML/SSO, contact the CIS team for the enterprise configuration.

**Q: Why does the IAM credential report sometimes take 30+ seconds?**  
A: AWS generates the IAM credential report asynchronously. The platform polls AWS until the report is ready (up to 15 attempts × 2 second intervals = 30 seconds maximum). This is an AWS-imposed constraint.

---

## 10. Appendix — Required AWS Permissions

Attach the following IAM policy to the user or role used to connect the platform. This policy is **read-only** — no changes are made to your account.

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "STSIdentity",
      "Effect": "Allow",
      "Action": ["sts:GetCallerIdentity"],
      "Resource": "*"
    },
    {
      "Sid": "IAMCredentialScan",
      "Effect": "Allow",
      "Action": [
        "iam:GenerateCredentialReport",
        "iam:GetCredentialReport",
        "iam:ListUsers",
        "iam:ListAccessKeys"
      ],
      "Resource": "*"
    },
    {
      "Sid": "SecretsManagerRead",
      "Effect": "Allow",
      "Action": ["secretsmanager:ListSecrets"],
      "Resource": "*"
    },
    {
      "Sid": "SecurityHubRead",
      "Effect": "Allow",
      "Action": ["securityhub:GetFindings"],
      "Resource": "*"
    },
    {
      "Sid": "BackupRead",
      "Effect": "Allow",
      "Action": [
        "backup:ListBackupPlans",
        "backup:ListBackupVaults",
        "backup:ListProtectedResources"
      ],
      "Resource": "*"
    },
    {
      "Sid": "EC2Read",
      "Effect": "Allow",
      "Action": ["ec2:DescribeInstances"],
      "Resource": "*"
    },
    {
      "Sid": "RDSRead",
      "Effect": "Allow",
      "Action": ["rds:DescribeDBInstances"],
      "Resource": "*"
    },
    {
      "Sid": "S3Read",
      "Effect": "Allow",
      "Action": [
        "s3:ListAllMyBuckets",
        "s3:GetBucketVersioning",
        "s3:GetObjectLockConfiguration"
      ],
      "Resource": "*"
    },
    {
      "Sid": "DynamoDBRead",
      "Effect": "Allow",
      "Action": [
        "dynamodb:ListTables",
        "dynamodb:DescribeContinuousBackups"
      ],
      "Resource": "*"
    }
  ]
}
```

### How to Attach the Policy

1. Open the **AWS Console → IAM → Users** (or Roles).
2. Select the user/role used for the platform connection.
3. Click **Add permissions → Attach policies directly → Create inline policy**.
4. Paste the JSON above → **Review policy** → Name it `CISCloudShieldReadOnly` → **Create policy**.

---

*Document prepared by Infosys Cloud Infrastructure Services · CIS Cloud Shield v1.0 · May 2026*  
*For support, contact your Infosys CIS account team.*
