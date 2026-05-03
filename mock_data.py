import random
from datetime import datetime, timedelta

APP_NAMES = [
    "payment-gateway", "user-auth", "inventory-svc", "order-mgmt",
    "notification-svc", "api-gateway", "data-pipeline", "report-engine",
    "ml-inference", "search-svc", "billing-processor", "customer-portal",
    "admin-dashboard", "event-bus", "cache-svc", "file-storage",
    "email-svc", "sms-gateway", "analytics-engine", "fraud-detection",
    "loyalty-program", "catalog-svc", "checkout-svc", "shipping-tracker",
    "returns-processor", "review-engine", "recommendation-svc", "pricing-svc",
    "tax-calculator", "audit-logger", "compliance-monitor", "deploy-pipeline",
    "perf-monitor", "cost-optimizer", "config-validator", "secrets-rotation",
    "log-aggregator", "metrics-collector", "waf-manager", "ddos-protection",
]

CREDENTIAL_TYPES = [
    {"type": "AWS Access Key ID",      "service": "AWS IAM",       "severity": "CRITICAL", "example": "AKIAIOSFODNN7EXAMPLE"},
    {"type": "AWS Secret Access Key",  "service": "AWS IAM",       "severity": "CRITICAL", "example": "wJalrXUtnFEMI/K7MDENG/..."},
    {"type": "Database Password",      "service": "RDS/Aurora",    "severity": "HIGH",     "example": "DB_PASSWORD=Sup3rS3cret!"},
    {"type": "API Key",                "service": "External API",  "severity": "HIGH",     "example": "api_key=sk_prod_aBcDeFg"},
    {"type": "OAuth Client Secret",    "service": "OAuth2/OIDC",   "severity": "HIGH",     "example": "CLIENT_SECRET=abc123xyz"},
    {"type": "SSH Private Key",        "service": "EC2/Bastion",   "severity": "CRITICAL", "example": "-----BEGIN RSA PRIVATE KEY-----"},
    {"type": "Stripe Live Key",        "service": "Payment",       "severity": "CRITICAL", "example": "sk_live_4eC39HqLyjWD..."},
    {"type": "JWT Secret",             "service": "Authentication","severity": "HIGH",     "example": "JWT_SECRET=ultraSecret_K3y"},
    {"type": "Slack Bot Token",        "service": "Slack",         "severity": "MEDIUM",   "example": "xoxb-17653672481-..."},
    {"type": "SMTP Password",          "service": "Email",         "severity": "MEDIUM",   "example": "smtp_password=mailP@ss"},
    {"type": "GitHub PAT",             "service": "GitHub",        "severity": "HIGH",     "example": "ghp_R2D2C3P0tokenXXX"},
    {"type": "SendGrid API Key",       "service": "Email API",     "severity": "MEDIUM",   "example": "SG.xxxxxx.yyyyyyy"},
]

FILE_LOCATIONS = [
    "config/application.properties", "src/main/resources/application.yml",
    ".env", "docker-compose.yml", "Dockerfile",
    "infrastructure/terraform/variables.tf", "scripts/deploy.sh",
    ".github/workflows/ci.yml", "k8s/deployment.yaml", "src/config.py",
    "app/settings.js", "helm/values.yaml", "cloudformation/template.yaml",
    "tests/integration/config.json", "scripts/bootstrap.sh",
]

COMMIT_AUTHORS = [
    "john.doe", "jane.smith", "bob.wilson", "alice.jones", "charlie.brown",
    "diana.prince", "eve.carter", "frank.miller", "grace.lee", "henry.ford",
]

ENVIRONMENTS = ["production", "staging", "development", "qa"]


def get_credential_findings(n: int = 1200) -> list:
    rng = random.Random(42)
    findings = []
    for i in range(n):
        cred = rng.choice(CREDENTIAL_TYPES)
        days_old = rng.randint(1, 365)
        findings.append({
            "id":               f"CRED-{10000 + i}",
            "application":      rng.choice(APP_NAMES),
            "environment":      rng.choice(ENVIRONMENTS),
            "credential_type":  cred["type"],
            "service":          cred["service"],
            "severity":         cred["severity"],
            "file_location":    rng.choice(FILE_LOCATIONS),
            "line_number":      rng.randint(1, 500),
            "example_pattern":  cred["example"][:20] + "...",
            "detected_date":    (datetime.now() - timedelta(days=days_old)).strftime("%Y-%m-%d"),
            "age_days":         days_old,
            "status":           rng.choice(["Open", "Open", "Open", "In Progress", "Resolved"]),
            "commit_author":    rng.choice(COMMIT_AUTHORS),
            "repository":       f"github.com/org/{rng.choice(APP_NAMES)}",
            "branch":           rng.choice(["main", "develop", "feature/auth", "fix/config"]),
        })
    return findings


APP_TYPES = [
    {"type": "EC2 Instance",     "count": 100, "default_backup": "EC2 Snapshots"},
    {"type": "RDS Database",     "count": 50,  "default_backup": "RDS Automated Backups"},
    {"type": "ECS Service",      "count": 37,  "default_backup": "EFS + EBS Snapshots"},
    {"type": "Lambda Function",  "count": 25,  "default_backup": "S3 Versioning"},
    {"type": "S3 Application",   "count": 25,  "default_backup": "S3 Versioning + Replication"},
    {"type": "DynamoDB Table",   "count": 13,  "default_backup": "DynamoDB PITR"},
]

CRITICALITIES     = ["Mission Critical", "Mission Critical", "Business Critical", "Standard", "Low"]
TEAMS             = ["Platform", "Data", "Frontend", "Backend", "Infrastructure", "Security", "ML/AI"]
DATA_CLASSES      = ["PII", "Financial", "PHI", "Internal", "Public"]
RPO_OPTIONS       = ["< 15 minutes", "< 1 hour", "< 4 hours", "< 24 hours"]
RTO_OPTIONS       = ["< 1 hour", "< 2 hours", "< 4 hours", "< 8 hours", "< 24 hours"]
REGIONS           = ["us-east-1", "us-west-2", "eu-west-1", "ap-southeast-1"]


def get_app_inventory(n: int = 250) -> list:
    rng = random.Random(42)
    apps, app_id = [], 2000
    for app_type_info in APP_TYPES:
        for i in range(app_type_info["count"]):
            base    = rng.choice(APP_NAMES)
            prefix  = app_type_info["type"].split()[0].lower()
            name    = f"{base}-{prefix}-{i+1:03d}"
            rand    = rng.random()
            if rand < 0.50:
                backup_status  = "Protected"
                backup_solution = app_type_info["default_backup"] + " + AWS Backup"
                last_backup    = rng.randint(0, 7)
                immutable      = rng.choice([True, True, False])
            elif rand < 0.70:
                backup_status  = "Partial"
                backup_solution = "Manual snapshots (ad-hoc)"
                last_backup    = rng.randint(7, 60)
                immutable      = False
            else:
                backup_status  = "Unprotected"
                backup_solution = "None"
                last_backup    = None
                immutable      = False
            apps.append({
                "app_id":             f"APP-{app_id}",
                "application":        name,
                "type":               app_type_info["type"],
                "environment":        rng.choice(ENVIRONMENTS),
                "criticality":        rng.choice(CRITICALITIES),
                "team":               rng.choice(TEAMS),
                "region":             rng.choice(REGIONS),
                "data_classification":rng.choice(DATA_CLASSES),
                "backup_status":      backup_status,
                "backup_solution":    backup_solution,
                "last_backup_days_ago": last_backup,
                "immutable_backup":   immutable,
                "rpo_requirement":    rng.choice(RPO_OPTIONS),
                "rto_requirement":    rng.choice(RTO_OPTIONS),
                "snow_ticket":        None,
                "snow_ticket_url":    None,
            })
            app_id += 1
    return apps


BACKUP_TECHNOLOGIES = {
    "AWS Backup": {
        "vendor":                  "AWS",
        "type":                    "Cloud-Native Managed Service",
        "cloud_support":           ["AWS"],
        "aws_services":            ["EC2", "RDS", "Aurora", "EFS", "DynamoDB", "DocumentDB", "Neptune", "S3"],
        "on_prem":                 False,
        "immutable":               True,
        "immutability_mechanism":  "Backup Vault Lock — WORM compliance & governance modes",
        "cross_region_backup":     True,
        "cross_account_backup":    True,
        "rpo":                     "1 hour minimum (configurable frequency)",
        "rto":                     "2–6 hours for full workload restore",
        "encryption":              "AES-256 via AWS KMS (CMK supported)",
        "compliance":              ["SOC 2", "PCI DSS", "HIPAA", "ISO 27001", "FedRAMP"],
        "monitoring":              "CloudWatch metrics + SNS event notifications",
        "testing":                 "Restore validation via AWS Backup Audit Manager",
        "operational_model":       "Fully managed — AWS handles infrastructure; customer sets policies via console / Terraform",
        "cost_model":              "Pay-per-GB stored + data restore costs",
        "strengths":               ["Zero infrastructure overhead", "Native AWS integration across 8+ services", "Org-wide policies via AWS Organizations"],
        "limitations":             ["AWS-only — no on-prem or multi-cloud", "Limited support for 3rd-party workloads"],
    },
    "Veeam Backup for AWS": {
        "vendor":                  "Veeam",
        "type":                    "Third-Party SaaS / Self-Managed",
        "cloud_support":           ["AWS", "Azure", "GCP", "On-premises"],
        "aws_services":            ["EC2", "RDS", "EFS", "VPC configurations"],
        "on_prem":                 True,
        "immutable":               True,
        "immutability_mechanism":  "S3 Object Lock + Veeam Hardened Repository (Linux)",
        "cross_region_backup":     True,
        "cross_account_backup":    True,
        "rpo":                     "15 minutes (continuous data protection available)",
        "rto":                     "< 2 hours (instant VM recovery)",
        "encryption":              "AES-256 with customer-managed keys; in-flight TLS",
        "compliance":              ["SOC 2", "PCI DSS", "HIPAA", "GDPR"],
        "monitoring":              "Veeam ONE dashboard + SIEM/SNMP integration",
        "testing":                 "SureBackup automated recovery verification with test reports",
        "operational_model":       "Customer-managed; vendor support available. Requires Veeam Backup Server deployment.",
        "cost_model":              "License per instance/socket + cloud storage costs",
        "strengths":               ["Multi-cloud & hybrid support", "Granular file-level recovery", "Rich automated reporting"],
        "limitations":             ["Requires infrastructure management", "License cost overhead"],
    },
    "Commvault": {
        "vendor":                  "Commvault",
        "type":                    "Enterprise Backup Platform",
        "cloud_support":           ["AWS", "Azure", "GCP", "On-premises", "Hybrid"],
        "aws_services":            ["EC2", "RDS", "Oracle", "SAP HANA", "Exchange", "SharePoint"],
        "on_prem":                 True,
        "immutable":               True,
        "immutability_mechanism":  "Air-gap + WORM storage + Metallic ThreatWise cyber deception layer",
        "cross_region_backup":     True,
        "cross_account_backup":    True,
        "rpo":                     "< 15 minutes for critical workloads (CommCell Journal)",
        "rto":                     "< 1 hour for critical systems",
        "encryption":              "AES-256, FIPS 140-2 validated",
        "compliance":              ["SOC 2", "PCI DSS", "HIPAA", "FedRAMP Moderate", "GDPR", "ITAR"],
        "monitoring":              "Command Center + Splunk/QRadar/SNMP/REST API integration",
        "testing":                 "Automated DR orchestration with full compliance reporting",
        "operational_model":       "Enterprise managed; Commvault professional services available for complex environments.",
        "cost_model":              "Enterprise perpetual or subscription license",
        "strengths":               ["Deepest enterprise application support", "Handles complex hybrid environments", "Built-in ransomware detection & deception"],
        "limitations":             ["Complex initial deployment", "High total cost of ownership", "Requires dedicated admin"],
    },
    "AWS S3 Object Lock": {
        "vendor":                  "AWS",
        "type":                    "Storage-Level Immutability",
        "cloud_support":           ["AWS"],
        "aws_services":            ["S3", "S3 Glacier", "S3 Glacier Deep Archive"],
        "on_prem":                 False,
        "immutable":               True,
        "immutability_mechanism":  "WORM — Compliance mode cannot be overridden even by AWS root account",
        "cross_region_backup":     True,
        "cross_account_backup":    True,
        "rpo":                     "Continuous with S3 versioning + replication; seconds to minutes",
        "rto":                     "Immediate (S3 Standard) → Hours (Glacier) → 12+ hours (Deep Archive)",
        "encryption":              "SSE-S3, SSE-KMS, SSE-C; client-side encryption supported",
        "compliance":              ["SEC Rule 17a-4", "CFTC", "FINRA", "SOC 2", "HIPAA"],
        "monitoring":              "S3 Storage Lens + CloudWatch + S3 Event Notifications",
        "testing":                 "Object retrieval tests via AWS Console / CLI / SDK",
        "operational_model":       "Fully managed storage layer; backup orchestration requires supplemental tooling (AWS Backup or custom Lambda).",
        "cost_model":              "S3 standard storage pricing; minimal overhead vs unprotected buckets",
        "strengths":               ["Strongest regulatory compliance (SEC 17a-4)", "Infinite scale with zero infrastructure", "Lowest cost for cold/archive data"],
        "limitations":             ["S3 data only — no compute/database native backup", "No built-in backup orchestration or scheduling", "Glacier retrieval latency for archive tiers"],
    },
}
