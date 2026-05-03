"""
Real AWS data integration via boto3.
Queries IAM, Security Hub, AWS Backup, EC2, RDS, S3, and DynamoDB.
"""

import boto3
from botocore.exceptions import ClientError, NoCredentialsError
import csv
import io
import time
from datetime import datetime, timezone


def _age_days(value) -> int:
    """Return days since a datetime or ISO string. -1 if unknown/unparseable."""
    if not value or str(value) in ("N/A", "no_information", "not_supported", "None", ""):
        return -1
    try:
        if isinstance(value, datetime):
            dt = value
        else:
            dt = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return (datetime.now(timezone.utc) - dt).days
    except Exception:
        return -1


class AWSIntelligenceClient:

    def __init__(self, role_arn: str = "", external_id: str = "",
                 region: str = "us-east-1", auth_method: str = "env"):
        """
        auth_method="role"  → STS AssumeRole using role_arn (+ optional external_id)
        auth_method="env"   → boto3 credential chain: env vars, instance profile,
                              ECS task role, SSO — nothing entered in the UI
        """
        self.region = region
        self.account_id: str = ""

        if auth_method == "role" and role_arn:
            # Assume the IAM role; the caller identity of the host/env is used
            # to make the sts:AssumeRole call, so no long-lived keys are needed.
            sts_client = boto3.client("sts", region_name=region)
            assume_kwargs: dict = {
                "RoleArn":         role_arn,
                "RoleSessionName": "CISCloudShieldSession",
                "DurationSeconds": 3600,
            }
            if external_id:
                assume_kwargs["ExternalId"] = external_id
            resp  = sts_client.assume_role(**assume_kwargs)
            creds = resp["Credentials"]
            self._session = boto3.Session(
                aws_access_key_id     = creds["AccessKeyId"],
                aws_secret_access_key = creds["SecretAccessKey"],
                aws_session_token     = creds["SessionToken"],
                region_name           = region,
            )
        else:
            # Let boto3 discover credentials automatically:
            # env vars → ~/.aws/credentials → instance profile → ECS task role → SSO
            self._session = boto3.Session(region_name=region)

    def _client(self, service: str):
        return self._session.client(service, region_name=self.region)

    # ── Connection test ────────────────────────────────────────────────────────

    def test_connection(self) -> dict:
        try:
            sts      = self._client("sts")
            identity = sts.get_caller_identity()
            self.account_id = identity["Account"]
            return {
                "ok":         True,
                "account_id": identity["Account"],
                "arn":        identity["Arn"],
                "user_id":    identity["UserId"],
            }
        except NoCredentialsError:
            return {"ok": False, "error": "No AWS credentials configured"}
        except ClientError as exc:
            return {"ok": False, "error": str(exc)}
        except Exception as exc:
            return {"ok": False, "error": str(exc)}

    # ── IAM Credential Findings ────────────────────────────────────────────────

    def get_iam_findings(self) -> list:
        """
        Parse the IAM credential report into finding dicts that match
        the same schema as mock_data.get_credential_findings().
        Checks: root active key, no-MFA console users, stale keys/passwords.
        """
        iam      = self._client("iam")
        findings = []
        fid      = 20000

        # Generate + poll credential report
        try:
            iam.generate_credential_report()
        except Exception:
            pass

        report_content = None
        for _ in range(20):
            try:
                resp           = iam.get_credential_report()
                report_content = resp["Content"].decode("utf-8")
                break
            except iam.exceptions.CredentialReportNotReadyException:
                time.sleep(2)
            except Exception:
                time.sleep(2)

        if not report_content:
            return [_err_finding(fid, "IAM credential report unavailable (timeout)")]

        reader = csv.DictReader(io.StringIO(report_content))
        today  = datetime.now().strftime("%Y-%m-%d")

        for row in reader:
            user = row.get("user", "unknown")

            # ── Root account ───────────────────────────────────────────────
            if user == "<root_account>":
                if row.get("access_key_1_active") == "true":
                    findings.append(_finding(fid, "AWS Root Account", "CRITICAL",
                        "AWS Root Access Key", "Root account has an active access key — delete immediately",
                        "IAM / Account Settings", today, 0))
                    fid += 1
                if row.get("mfa_active") == "false":
                    findings.append(_finding(fid, "AWS Root Account", "CRITICAL",
                        "Root Account — No MFA", "Root account has no MFA enabled",
                        "IAM / Account Settings", today, 0))
                    fid += 1
                continue

            # ── Console user without MFA ───────────────────────────────────
            if row.get("mfa_active") == "false" and row.get("password_enabled") == "true":
                findings.append(_finding(fid, user, "HIGH",
                    "IAM User — No MFA",
                    f"User '{user}' has console password but MFA is disabled",
                    f"IAM / Users / {user}", today, 0))
                fid += 1

            # ── Stale console password ─────────────────────────────────────
            pwd_last = row.get("password_last_used", "")
            if row.get("password_enabled") == "true" and pwd_last not in ("", "N/A", "no_information", "not_supported"):
                age = _age_days(pwd_last)
                if age > 90:
                    sev = "CRITICAL" if age > 180 else "HIGH"
                    findings.append(_finding(fid, user, sev,
                        "Stale Console Password",
                        f"User '{user}' password last used {age} days ago — consider disabling",
                        f"IAM / Users / {user}", today, age))
                    fid += 1

            # ── Stale access keys ──────────────────────────────────────────
            for k in ("1", "2"):
                if row.get(f"access_key_{k}_active") != "true":
                    continue
                rotated = row.get(f"access_key_{k}_last_rotated", "")
                age     = _age_days(rotated)
                if age < 90:
                    continue
                sev      = "CRITICAL" if age > 180 else "HIGH"
                last_use = row.get(f"access_key_{k}_last_used_date", "never")
                last_use = last_use[:10] if last_use not in ("", "N/A", "no_information") else "never"
                findings.append(_finding(fid, user, sev,
                    "Stale IAM Access Key",
                    f"Access key {k} for '{user}' is {age} days old (last used: {last_use})",
                    f"IAM / Users / {user} / Access Key {k}", today, age))
                fid += 1

        return findings

    def get_secrets_inventory(self) -> list:
        """List Secrets Manager secrets with rotation status."""
        sm      = self._client("secretsmanager")
        secrets = []
        try:
            paginator = sm.get_paginator("list_secrets")
            for page in paginator.paginate():
                for s in page["SecretList"]:
                    age = _age_days(s.get("LastRotatedDate"))
                    secrets.append({
                        "name":               s["Name"],
                        "arn":                s["ARN"],
                        "rotation_enabled":   s.get("RotationEnabled", False),
                        "last_rotated_days":  age,
                        "last_changed":       str(s.get("LastChangedDate", ""))[:10],
                        "description":        s.get("Description", ""),
                    })
        except ClientError:
            pass
        return secrets

    def get_security_hub_findings(self, max_results: int = 200) -> list:
        """Fetch active failed Security Hub findings (if Hub is enabled)."""
        sh       = self._client("securityhub")
        findings = []
        try:
            paginator = sh.get_paginator("get_findings")
            filters = {
                "ComplianceStatus": [{"Value": "FAILED",  "Comparison": "EQUALS"}],
                "RecordState":      [{"Value": "ACTIVE",  "Comparison": "EQUALS"}],
                "WorkflowStatus":   [{"Value": "NEW",     "Comparison": "EQUALS"}],
            }
            count = 0
            for page in paginator.paginate(Filters=filters, MaxResults=100):
                for f in page["Findings"]:
                    if count >= max_results:
                        break
                    resources = f.get("Resources", [{}])
                    findings.append({
                        "id":            f.get("Id", "")[-20:],
                        "title":         f.get("Title", ""),
                        "severity":      f.get("Severity", {}).get("Label", "MEDIUM"),
                        "resource_type": resources[0].get("Type", "") if resources else "",
                        "resource_id":   resources[0].get("Id", "")[-40:] if resources else "",
                        "created_at":    str(f.get("CreatedAt", ""))[:10],
                        "control_id":    f.get("ProductFields", {}).get("ControlId", ""),
                        "description":   f.get("Description", "")[:120],
                    })
                    count += 1
        except ClientError as exc:
            # Silently skip if Security Hub is not enabled / not subscribed
            if "not subscribed" not in str(exc).lower() and "InvalidAccess" not in str(exc):
                raise
        return findings

    # ── Backup Intelligence ────────────────────────────────────────────────────

    def get_backup_plans(self) -> list:
        backup = self._client("backup")
        plans  = []
        try:
            for p in backup.list_backup_plans().get("BackupPlansList", []):
                plans.append({
                    "plan_id":        p["BackupPlanId"],
                    "plan_name":      p["BackupPlanName"],
                    "version":        p["VersionId"][:8],
                    "created_at":     str(p.get("CreationDate", ""))[:10],
                    "last_execution": str(p.get("LastExecutionDate", ""))[:10],
                })
        except ClientError:
            pass
        return plans

    def get_backup_vaults(self) -> list:
        backup = self._client("backup")
        vaults = []
        try:
            for v in backup.list_backup_vaults().get("BackupVaultList", []):
                locked = v.get("Locked", False)
                vaults.append({
                    "vault_name":        v["BackupVaultName"],
                    "recovery_points":   v.get("NumberOfRecoveryPoints", 0),
                    "locked":            locked,
                    "lock_date":         str(v.get("LockDate", ""))[:10] if locked else "—",
                    "min_retention":     v.get("MinRetentionDays", "—"),
                    "max_retention":     v.get("MaxRetentionDays", "—"),
                    "immutable":         locked,
                })
        except ClientError:
            pass
        return vaults

    def _protected_arns(self) -> set:
        backup = self._client("backup")
        arns   = set()
        try:
            paginator = backup.get_paginator("list_protected_resources")
            for page in paginator.paginate():
                for r in page["Results"]:
                    arns.add(r["ResourceArn"])
        except ClientError:
            pass
        return arns

    def get_ec2_backup_status(self, protected: set = None) -> list:
        ec2       = self._client("ec2")
        protected = protected or self._protected_arns()
        items     = []
        try:
            paginator = ec2.get_paginator("describe_instances")
            for page in paginator.paginate(
                Filters=[{"Name": "instance-state-name", "Values": ["running", "stopped"]}]
            ):
                for res in page["Reservations"]:
                    for inst in res["Instances"]:
                        tags    = {t["Key"]: t["Value"] for t in inst.get("Tags", [])}
                        arn     = f"arn:aws:ec2:{self.region}:{self.account_id}:instance/{inst['InstanceId']}"
                        backed  = arn in protected
                        items.append(_app_row(
                            app_id   = inst["InstanceId"],
                            name     = tags.get("Name", inst["InstanceId"]),
                            rtype    = "EC2 Instance",
                            env      = tags.get("Environment", tags.get("Env", "unknown")),
                            crit     = tags.get("Criticality", "Standard"),
                            team     = tags.get("Team", tags.get("Owner", "unknown")),
                            region   = self.region,
                            data_cls = tags.get("DataClassification", "Internal"),
                            backed   = backed,
                            solution = "AWS Backup" if backed else "None",
                            immut    = backed,
                            rpo      = tags.get("RPO", "< 24 hours"),
                            rto      = tags.get("RTO", "< 8 hours"),
                        ))
        except ClientError:
            pass
        return items

    def get_rds_backup_status(self, protected: set = None) -> list:
        rds       = self._client("rds")
        protected = protected or self._protected_arns()
        items     = []
        try:
            paginator = rds.get_paginator("describe_db_instances")
            for page in paginator.paginate():
                for db in page["DBInstances"]:
                    arn     = db["DBInstanceArn"]
                    backed  = arn in protected
                    auto_bk = db.get("BackupRetentionPeriod", 0) > 0
                    if backed:
                        status   = "Protected"
                        solution = "AWS Backup + RDS Automated Backups"
                    elif auto_bk:
                        status   = "Partial"
                        solution = f"RDS Auto Backups ({db['BackupRetentionPeriod']}d)"
                    else:
                        status   = "Unprotected"
                        solution = "None"
                    items.append(_app_row(
                        app_id   = db["DBInstanceIdentifier"],
                        name     = db["DBInstanceIdentifier"],
                        rtype    = "RDS Database",
                        env      = "production",
                        crit     = "Business Critical",
                        team     = "Database",
                        region   = self.region,
                        data_cls = "Financial",
                        backed   = backed,
                        solution = solution,
                        immut    = backed,
                        rpo      = "< 1 hour",
                        rto      = "< 4 hours",
                        status_override = status,
                    ))
        except ClientError:
            pass
        return items

    def get_s3_backup_status(self) -> list:
        s3    = self._client("s3")
        items = []
        try:
            for b in s3.list_buckets().get("Buckets", []):
                name        = b["Name"]
                versioning  = "Disabled"
                object_lock = False
                try:
                    v          = s3.get_bucket_versioning(Bucket=name)
                    versioning = v.get("Status", "Disabled") or "Disabled"
                except ClientError:
                    pass
                try:
                    s3.get_object_lock_configuration(Bucket=name)
                    object_lock = True
                except ClientError:
                    pass

                if object_lock:
                    status   = "Protected"
                    solution = "S3 Object Lock (WORM) + Versioning"
                elif versioning == "Enabled":
                    status   = "Partial"
                    solution = "S3 Versioning (no Object Lock)"
                else:
                    status   = "Unprotected"
                    solution = "None"

                items.append(_app_row(
                    app_id   = name,
                    name     = name,
                    rtype    = "S3 Application",
                    env      = "production",
                    crit     = "Standard",
                    team     = "Platform",
                    region   = self.region,
                    data_cls = "Internal",
                    backed   = object_lock,
                    solution = solution,
                    immut    = object_lock,
                    rpo      = "< 1 hour",
                    rto      = "< 1 hour",
                    status_override = status,
                ))
        except ClientError:
            pass
        return items

    def get_dynamodb_backup_status(self, protected: set = None) -> list:
        ddb       = self._client("dynamodb")
        protected = protected or self._protected_arns()
        items     = []
        try:
            paginator = ddb.get_paginator("list_tables")
            for page in paginator.paginate():
                for table in page["TableNames"]:
                    arn    = f"arn:aws:dynamodb:{self.region}:{self.account_id}:table/{table}"
                    backed = arn in protected
                    pitr   = False
                    try:
                        r    = ddb.describe_continuous_backups(TableName=table)
                        pitr = r["ContinuousBackupsDescription"]["PointInTimeRecoveryDescription"]["PointInTimeRecoveryStatus"] == "ENABLED"
                    except ClientError:
                        pass
                    if backed:
                        status   = "Protected"
                        solution = "AWS Backup + DynamoDB PITR"
                    elif pitr:
                        status   = "Partial"
                        solution = "DynamoDB PITR only"
                    else:
                        status   = "Unprotected"
                        solution = "None"
                    items.append(_app_row(
                        app_id   = table,
                        name     = table,
                        rtype    = "DynamoDB Table",
                        env      = "production",
                        crit     = "Business Critical",
                        team     = "Data",
                        region   = self.region,
                        data_cls = "Internal",
                        backed   = backed or pitr,
                        solution = solution,
                        immut    = backed,
                        rpo      = "< 1 hour",
                        rto      = "< 2 hours",
                        status_override = status,
                    ))
        except ClientError:
            pass
        return items

    def get_all_backup_status(self) -> list:
        """Aggregate backup status across EC2, RDS, S3, DynamoDB in one pass."""
        protected = self._protected_arns()
        results   = []
        results.extend(self.get_ec2_backup_status(protected))
        results.extend(self.get_rds_backup_status(protected))
        results.extend(self.get_s3_backup_status())
        results.extend(self.get_dynamodb_backup_status(protected))
        return results


# ── Helpers ────────────────────────────────────────────────────────────────────

def _finding(fid, user, severity, cred_type, detail, location, date, age):
    return {
        "id":               f"IAM-{fid}",
        "application":      user,
        "environment":      "production",
        "credential_type":  cred_type,
        "service":          "AWS IAM",
        "severity":         severity,
        "file_location":    location,
        "line_number":      0,
        "example_pattern":  detail[:30] + "...",
        "detected_date":    date,
        "age_days":         age,
        "status":           "Open",
        "commit_author":    user,
        "repository":       "AWS IAM (Live)",
        "branch":           "live",
    }


def _err_finding(fid, msg):
    return _finding(fid, "IAM Scanner", "MEDIUM", "Scanner Error", msg,
                    "IAM", datetime.now().strftime("%Y-%m-%d"), 0)


def _app_row(*, app_id, name, rtype, env, crit, team, region, data_cls,
             backed, solution, immut, rpo, rto, status_override=None):
    if status_override:
        status = status_override
    else:
        status = "Protected" if backed else "Unprotected"
    return {
        "app_id":              app_id,
        "application":         name,
        "type":                rtype,
        "environment":         env,
        "criticality":         crit,
        "team":                team,
        "region":              region,
        "data_classification": data_cls,
        "backup_status":       status,
        "backup_solution":     solution,
        "last_backup_days_ago": 0 if backed else None,
        "immutable_backup":    immut,
        "rpo_requirement":     rpo,
        "rto_requirement":     rto,
        "snow_ticket":         None,
        "snow_ticket_url":     None,
    }
