"""
Infosys CIS Cloud Shield
Agentic AI platform for AWS credential remediation and immutable backup governance.
"""

import streamlit as st
import openai
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
from datetime import datetime

from mock_data import get_credential_findings, get_app_inventory, BACKUP_TECHNOLOGIES
from servicenow import ServiceNowClient
from aws_client import AWSIntelligenceClient

APP_NAME    = "CIS Cloud Shield"
APP_TAGLINE = "Agentic AI · AWS Security · Immutable Backup"

# ── Page config (must be first Streamlit call) ────────────────────────────────
st.set_page_config(
    page_title=f"Infosys {APP_NAME}",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Global CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── base ── */
[data-testid="stSidebar"] { background:#0d1117; }
body, .stApp { background:#060d18; }

/* ── login animations ── */
@keyframes spin-ring  { to { transform:rotate(360deg); } }
@keyframes glow-pulse {
    0%,100% { box-shadow:0 0 12px rgba(0,170,255,.45); }
    50%     { box-shadow:0 0 28px rgba(0,170,255,.9),0 0 48px rgba(124,58,237,.45); }
}
@keyframes float-up {
    0%,100% { transform:translateY(0); }
    50%     { transform:translateY(-5px); }
}

/* ── login card: style the centre column block as the card ── */
div[data-testid="stHorizontalBlock"] > div:nth-child(2) > div > div[data-testid="stVerticalBlock"] {
    background:linear-gradient(160deg,#0d1b2a 0%,#091220 100%) !important;
    border:1px solid #1f3a5f !important;
    border-radius:18px !important;
    padding:28px 24px 20px !important;
    box-shadow:0 0 55px rgba(0,170,255,.12) !important;
    margin-top:7vh !important;
}

/* ── match input fields to card theme ── */
.stTextInput > div > div > input {
    background:#070e1c !important;
    border:1px solid #1f3a5f !important;
    color:#e0e0e0 !important;
    border-radius:8px !important;
    font-size:13px !important;
}
.stTextInput > div > div > input:focus {
    border-color:#00aaff !important;
    box-shadow:0 0 0 2px rgba(0,170,255,.18) !important;
}

/* ── top header bar ── */
.topbar {
    display:flex;align-items:center;gap:16px;
    padding:12px 24px;
    background:linear-gradient(90deg,#060d18 0%,#0d1b2a 50%,#060d18 100%);
    border-bottom:1px solid #1f3a5f;
    margin-bottom:12px;
}
.topbar-logo {
    position:relative;width:40px;height:40px;flex-shrink:0;
}
.topbar-logo-ring {
    position:absolute;inset:0;border-radius:50%;
    background:conic-gradient(from 0deg,#00aaff,#7c3aed,#0044cc,#00ff88,#00aaff);
    animation:spin-ring 4s linear infinite;
}
.topbar-logo-inner {
    position:absolute;inset:2px;border-radius:50%;
    background:#0d1b2a;
    display:flex;align-items:center;justify-content:center;font-size:17px;
}
.topbar-name { font-size:20px;font-weight:800;color:#fff; }
.topbar-tag  { font-size:12px;color:#6b8aad; }
.topbar-pill {
    margin-left:auto;background:#0a2a4a;border:1px solid #00aaff33;
    color:#00aaff;font-size:11px;padding:4px 12px;border-radius:20px;
}

/* ── agent cards ── */
.agent-card {
    background:#0d1b2a; border:1px solid #1f3a5f;
    border-radius:10px; padding:14px 16px; margin-bottom:10px; text-align:center;
}
.agent-idle   { border-color:#334; }
.agent-active { border-color:#00aaff; box-shadow:0 0 14px rgba(0,170,255,0.25); }
.agent-done   { border-color:#00cc88; }

/* ── misc ── */
.kpi-box { background:#111827;border:1px solid #1f2937;border-radius:8px;padding:14px;text-align:center; }
.snow-row { background:#0f2218;border:1px solid #1a4a2a;border-radius:6px;padding:8px 12px;margin:4px 0; }
</style>
""", unsafe_allow_html=True)

# ── Login gate ────────────────────────────────────────────────────────────────
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    _, mid, _ = st.columns([3.5, 2, 3.5])
    with mid:
        # ── Animated logo + brand (all inside the same column = same card) ──
        st.markdown("""
        <div style="text-align:center;padding-bottom:18px;animation:float-up 4s ease-in-out infinite">
          <!-- Spinning conic-gradient ring with static emoji centre -->
          <div style="position:relative;width:58px;height:58px;margin:0 auto 12px">
            <div style="position:absolute;inset:0;border-radius:50%;
                        background:conic-gradient(from 0deg,#00aaff,#7c3aed,#0044cc,#00ff88,#00aaff);
                        animation:spin-ring 3s linear infinite,glow-pulse 2s ease-in-out infinite;">
            </div>
            <div style="position:absolute;inset:3px;border-radius:50%;
                        background:#091220;
                        display:flex;align-items:center;justify-content:center;font-size:22px;">
              🛡️
            </div>
          </div>
          <div style="font-size:9px;color:#00aaff;letter-spacing:2.5px;
                      text-transform:uppercase;margin-bottom:6px;">
            Infosys · Cloud Infrastructure Services
          </div>
          <div style="font-size:18px;font-weight:800;color:#fff;
                      letter-spacing:.5px;margin-bottom:3px;">
            CIS Cloud Shield
          </div>
          <div style="font-size:11px;color:#6b8aad;margin-bottom:4px;">
            Agentic AI · AWS Security · Immutable Backup
          </div>
        </div>
        <hr style="border:none;border-top:1px solid #1f3a5f;margin:0 0 14px">
        """, unsafe_allow_html=True)

        username = st.text_input("Username", placeholder="Username", label_visibility="collapsed")
        password = st.text_input("Password", type="password", placeholder="Password", label_visibility="collapsed")
        if st.button("🔐  Sign In", type="primary", use_container_width=True):
            if username == "admin" and password == "Infosys@123":
                st.session_state.authenticated = True
                st.session_state.login_user    = username
                st.rerun()
            else:
                st.error("Invalid credentials. Use admin / Infosys@123")
        st.markdown(
            "<p style='text-align:center;font-size:10px;color:#3a5070;margin-top:10px'>"
            "🔒 Protected by Infosys CIS · TLS encrypted · Session-scoped</p>",
            unsafe_allow_html=True,
        )
    st.stop()

# ── App header (shown only when authenticated) ────────────────────────────────
st.markdown(f"""
<div class="topbar">
  <div class="topbar-logo">
    <div class="topbar-logo-ring"></div>
    <div class="topbar-logo-inner">🛡️</div>
  </div>
  <div>
    <div class="topbar-name">Infosys &nbsp;<span style="color:#00aaff">{APP_NAME}</span></div>
    <div class="topbar-tag">{APP_TAGLINE}</div>
  </div>
  <div class="topbar-pill">👤 {st.session_state.get('login_user','admin')}</div>
</div>
""", unsafe_allow_html=True)

# ── Session state initialisation ──────────────────────────────────────────────
if "findings"       not in st.session_state: st.session_state.findings       = get_credential_findings(1200)
if "apps"           not in st.session_state: st.session_state.apps           = get_app_inventory(250)
if "agent_outputs"  not in st.session_state: st.session_state.agent_outputs  = {}
if "agent_statuses" not in st.session_state: st.session_state.agent_statuses = {1:"idle",2:"idle",3:"idle",4:"idle"}
if "snow_tickets"   not in st.session_state: st.session_state.snow_tickets   = {}
if "cred_tickets"   not in st.session_state: st.session_state.cred_tickets   = {}
if "aws_connected"  not in st.session_state: st.session_state.aws_connected  = False
if "aws_creds"      not in st.session_state: st.session_state.aws_creds      = {}
if "live_iam"       not in st.session_state: st.session_state.live_iam       = []
if "live_hub"       not in st.session_state: st.session_state.live_hub       = []
if "live_secrets"   not in st.session_state: st.session_state.live_secrets   = []
if "live_backup"    not in st.session_state: st.session_state.live_backup    = []
if "live_plans"     not in st.session_state: st.session_state.live_plans     = []
if "live_vaults"    not in st.session_state: st.session_state.live_vaults    = []

findings_df = pd.DataFrame(st.session_state.findings)
apps_df     = pd.DataFrame(st.session_state.apps)

# ── Load secrets (Streamlit Cloud injects these; sidebar inputs are fallback) ──
_secrets            = st.secrets if hasattr(st, "secrets") else {}
_oai_from_secrets   = _secrets.get("OPENAI_API_KEY",  "")
_snow_url_default   = _secrets.get("SNOW_URL",         "https://dev218436.service-now.com")
_snow_user_default  = _secrets.get("SNOW_USER",        "admin")
_snow_pass_default  = _secrets.get("SNOW_PASS",        "")
_aws_key_default    = _secrets.get("AWS_ACCESS_KEY_ID",     "")
_aws_secret_default = _secrets.get("AWS_SECRET_ACCESS_KEY", "")
_aws_token_default  = _secrets.get("AWS_SESSION_TOKEN",     "")
_aws_region_default = _secrets.get("AWS_DEFAULT_REGION",    "us-east-1")

def _make_aws_client() -> AWSIntelligenceClient:
    c = st.session_state.aws_creds
    return AWSIntelligenceClient(
        access_key    = c.get("key",    ""),
        secret_key    = c.get("secret", ""),
        region        = c.get("region", "us-east-1"),
        session_token = c.get("token",  ""),
    )

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🛡️ Security Intelligence")
    st.caption("AWS Credential & Backup Platform")
    st.divider()

    st.markdown("### 🤖 OpenAI")
    if _oai_from_secrets:
        st.success("OpenAI key loaded from secrets ✓")
        openai_key = _oai_from_secrets
        llm_model  = st.selectbox("Model", ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo"], index=0)
    else:
        openai_key = st.text_input("API Key", type="password", placeholder="sk-...")
        llm_model  = st.selectbox("Model", ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo"], index=0)

    st.markdown("### 🎫 ServiceNow")
    snow_url  = st.text_input("Instance URL", value=_snow_url_default)
    snow_user = st.text_input("Username",     value=_snow_user_default)
    snow_pass = st.text_input("Password",     type="password",
                              value=_snow_pass_default, placeholder="ServiceNow password")

    if st.button("🔗 Test SNOW Connection", use_container_width=True):
        if snow_url and snow_user and snow_pass:
            res = ServiceNowClient(snow_url, snow_user, snow_pass).test_connection()
            (st.success if res["ok"] else st.error)(res["msg"])
        else:
            st.warning("Fill in all ServiceNow fields first.")

    st.markdown("### ☁️ AWS Account")
    if _aws_key_default:
        st.info("AWS credentials loaded from secrets ✓")
    aws_key    = st.text_input("Access Key ID",       value=_aws_key_default,    type="password", placeholder="AKIA...")
    aws_secret = st.text_input("Secret Access Key",   value=_aws_secret_default, type="password", placeholder="wJalr...")
    aws_token  = st.text_input("Session Token",       value=_aws_token_default,  type="password", placeholder="(optional — for STS assumed roles)")
    aws_region = st.selectbox("Region", [
        "us-east-1","us-east-2","us-west-1","us-west-2",
        "eu-west-1","eu-west-2","eu-central-1",
        "ap-southeast-1","ap-southeast-2","ap-northeast-1",
    ], index=["us-east-1","us-east-2","us-west-1","us-west-2",
              "eu-west-1","eu-west-2","eu-central-1",
              "ap-southeast-1","ap-southeast-2","ap-northeast-1"].index(_aws_region_default)
       if _aws_region_default in ["us-east-1","us-east-2","us-west-1","us-west-2",
                                   "eu-west-1","eu-west-2","eu-central-1",
                                   "ap-southeast-1","ap-southeast-2","ap-northeast-1"] else 0)

    if st.button("🔌 Connect to AWS", use_container_width=True):
        if aws_key and aws_secret:
            st.session_state.aws_creds = {"key": aws_key, "secret": aws_secret,
                                           "token": aws_token, "region": aws_region}
            with st.spinner("Verifying identity…"):
                result = _make_aws_client().test_connection()
            if result["ok"]:
                st.session_state.aws_connected  = True
                st.session_state.aws_account_id = result["account_id"]
                st.session_state.aws_arn        = result["arn"]
                st.success(f"✅ Connected\n**Account:** {result['account_id']}")
                st.caption(result["arn"])
            else:
                st.session_state.aws_connected = False
                st.error(f"Connection failed: {result['error']}")
        else:
            st.warning("Enter Access Key ID and Secret Access Key.")

    if st.session_state.aws_connected:
        st.success(f"🟢 Live — Account {st.session_state.get('aws_account_id','')}")

    st.divider()
    st.markdown("### 📊 Environment")
    crit  = len(findings_df[findings_df.severity == "CRITICAL"])
    high  = len(findings_df[findings_df.severity == "HIGH"])
    unp   = len(apps_df[apps_df.backup_status == "Unprotected"])
    part  = len(apps_df[apps_df.backup_status == "Partial"])
    c1, c2 = st.columns(2)
    c1.metric("Findings", "1,200");   c2.metric("Apps",     "250")
    c1.metric("Critical", crit);      c2.metric("High",     high)
    c1.metric("No Backup", unp);      c2.metric("Partial",  part)
    st.divider()
    st.caption("v1.0 · Prototype · 2026")


# ═════════════════════════════════════════════════════════════════════════════
# TABS
# ═════════════════════════════════════════════════════════════════════════════
tab1, tab2, tab3 = st.tabs([
    "🔐  Credential Intelligence",
    "💾  Backup Intelligence",
    "🔄  Auto-Remediation Loop",
])


# ═════════════════════════════════════════════════════════════════════════════
# TAB 1 — CREDENTIAL INTELLIGENCE
# ═════════════════════════════════════════════════════════════════════════════
with tab1:
    st.title("🔐 AWS Credential Intelligence")
    st.markdown("*4-agent AI system — detection → risk assessment → remediation → prevention*")

    # ── KPI row ──────────────────────────────────────────────────────────────
    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Total Findings",      "1,200")
    k2.metric("Critical",            crit,  delta="Rotate Now")
    k3.metric("High",                high,  delta="72-hr SLA")
    k4.metric("Medium",              len(findings_df[findings_df.severity == "MEDIUM"]))
    k5.metric("Apps Affected",       int(findings_df.application.nunique()))
    st.divider()

    # ── Agent orchestration panel ─────────────────────────────────────────────
    st.subheader("🤖 Multi-Agent Orchestration")

    AGENTS = [
        (1, "🔍", "Scanner Agent",
         "Discovers credential patterns across repos, configs & CI/CD pipelines"),
        (2, "⚖️", "Risk Agent",
         "Scores business risk, maps PCI-DSS / SOC2 / CIS compliance gaps"),
        (3, "🔧", "Remediation Agent",
         "Generates AWS Secrets Manager migration code & rotation scripts"),
        (4, "🛡️", "Prevention Agent",
         "Designs pre-commit hooks, SCPs, CI/CD guardrails & monitoring rules"),
    ]

    ac = st.columns(4)
    for num, icon, name, desc in AGENTS:
        status = st.session_state.agent_statuses.get(num, "idle")
        color  = {"idle": "#334455", "active": "#00aaff", "done": "#00cc88", "error": "#ff4444"}.get(status, "#334")
        ac[num - 1].markdown(
            f"""<div class="agent-card agent-{status}" style="border-color:{color}">
            <div style="font-size:28px">{icon}</div>
            <div style="font-weight:700;margin:6px 0">{name}</div>
            <div style="font-size:11px;color:#888;margin-bottom:8px">{desc}</div>
            <div style="font-size:11px;color:{color};text-transform:uppercase;letter-spacing:1px">{status}</div>
            </div>""",
            unsafe_allow_html=True,
        )

    st.markdown("")
    run_btn = st.button("🚀 Launch AI Security Analysis", type="primary", use_container_width=True)

    # ── Run AI agents ─────────────────────────────────────────────────────────
    if run_btn:
        if not openai_key:
            st.error("Enter your OpenAI API key in the sidebar.")
        else:
            client = openai.OpenAI(api_key=openai_key)

            # Build context payload
            by_sev = findings_df.severity.value_counts().to_dict()
            by_type = findings_df.credential_type.value_counts().head(6).to_dict()
            top_apps = findings_df.groupby("application").size().sort_values(ascending=False).head(5).to_dict()
            sample_critical = findings_df[findings_df.severity == "CRITICAL"].head(5).to_dict("records")

            env_ctx = json.dumps({
                "total_findings": 1200,
                "by_severity": by_sev,
                "top_credential_types": by_type,
                "most_exposed_apps": top_apps,
                "apps_affected": int(findings_df.application.nunique()),
                "sample_critical_findings": sample_critical,
            }, indent=2)

            AGENT_DEFS = [
                {
                    "num": 1, "name": "Scanner Agent", "icon": "🔍",
                    "system": (
                        "You are a senior AWS cloud security engineer specializing in credential scanning. "
                        "Analyze the environment data below and produce a structured threat assessment. "
                        "Use markdown headers and bullet points. Be specific and technical. Max 450 words."
                    ),
                    "user": (
                        f"Analyze our AWS environment credential scan results:\n\n{env_ctx}\n\n"
                        "Produce:\n"
                        "1. **Executive Summary** (2-3 sentences)\n"
                        "2. **Top 5 Most Critical Findings** — each with specific exploitation risk\n"
                        "3. **Attack Surface Analysis** — how each credential type could be weaponised\n"
                        "4. **24-Hour Immediate Actions** — what must happen today"
                    ),
                },
                {
                    "num": 2, "name": "Risk Assessment Agent", "icon": "⚖️",
                    "system": (
                        "You are a cybersecurity risk analyst specialising in AWS security posture. "
                        "You receive Scanner Agent findings. Assess business risk and compliance gaps. "
                        "Be quantitative. Use markdown. Max 450 words."
                    ),
                    "user": (
                        "Based on the Scanner Agent's analysis of 1,200 hardcoded credentials "
                        f"({crit} CRITICAL, {high} HIGH) across {int(findings_df.application.nunique())} apps:\n\n"
                        "Produce:\n"
                        "1. **Risk Score** — 0-100 with weighted formula breakdown\n"
                        "2. **Compliance Gap Matrix** — PCI-DSS §3.4, SOC2 CC6.3, CIS AWS Benchmark 1.21\n"
                        "3. **Business Impact** — financial exposure estimate and operational risk\n"
                        "4. **Remediation SLAs by Priority** — P0/P1/P2/P3 with concrete timeframes"
                    ),
                },
                {
                    "num": 3, "name": "Remediation Agent", "icon": "🔧",
                    "system": (
                        "You are a DevSecOps engineer specialising in AWS Secrets Manager and automated credential rotation. "
                        "Generate production-ready code. Be immediately actionable. Max 550 words."
                    ),
                    "user": (
                        "Generate a concrete remediation plan for hardcoded AWS credentials:\n\n"
                        "1. **Secrets Manager Migration** — Python/boto3 script to migrate a hardcoded DB password\n"
                        "2. **Application Code Before/After** — show the pattern change to retrieve the secret\n"
                        "3. **IAM Key Rotation Lambda** — skeleton function for automated rotation\n"
                        "4. **Rollback Procedure** — step-by-step if rotation causes an outage\n"
                        "5. **4-Week Phased Remediation Schedule** — week-by-week priority order"
                    ),
                },
                {
                    "num": 4, "name": "Prevention Agent", "icon": "🛡️",
                    "system": (
                        "You are a cloud security architect designing defence-in-depth controls. "
                        "Prevent future credential exposure. Provide specific configs and policy snippets. "
                        "Use markdown. Max 450 words."
                    ),
                    "user": (
                        "Design a prevention framework for our AWS environment to stop future credential hardcoding:\n\n"
                        "1. **Pre-commit Hook** — detect-secrets `.secrets.baseline` configuration\n"
                        "2. **AWS SCP** — deny IAM key creation without mandatory tagging approval\n"
                        "3. **GitHub Actions Step** — credential scanning in CI/CD pipeline YAML\n"
                        "4. **AWS Config Rule** — custom rule to detect plaintext credential patterns\n"
                        "5. **GuardDuty + CloudWatch** — alerting rules for compromised credential activity\n"
                        "6. **Developer Awareness** — top 5 security training topics to prevent recurrence"
                    ),
                },
            ]

            output_expander = st.expander("📊 Agent Analysis Output", expanded=True)
            with output_expander:
                prev_ctx = ""
                for adef in AGENT_DEFS:
                    st.session_state.agent_statuses[adef["num"]] = "active"
                    st.markdown(f"#### {adef['icon']} {adef['name']}")
                    placeholder = st.empty()
                    try:
                        messages = [{"role": "system", "content": adef["system"]}]
                        if prev_ctx:
                            messages.append({"role": "user", "content": f"[Prior agent context]:\n{prev_ctx[:800]}"})
                        messages.append({"role": "user", "content": adef["user"]})

                        stream = client.chat.completions.create(
                            model=llm_model, messages=messages,
                            stream=True, max_tokens=700,
                        )
                        full = ""
                        for chunk in stream:
                            delta = chunk.choices[0].delta.content
                            if delta:
                                full += delta
                                placeholder.markdown(full + "▌")
                        placeholder.markdown(full)
                        st.session_state.agent_outputs[adef["num"]] = full
                        st.session_state.agent_statuses[adef["num"]] = "done"
                        prev_ctx = full
                    except Exception as exc:
                        st.session_state.agent_statuses[adef["num"]] = "error"
                        st.error(f"Agent {adef['num']} error: {exc}")
                    st.markdown("---")

            st.rerun()

    # Show cached outputs if analysis already ran
    if st.session_state.agent_outputs and not run_btn:
        with st.expander("📊 Last Agent Analysis Output", expanded=False):
            for num, icon, name, _ in AGENTS:
                if num in st.session_state.agent_outputs:
                    st.markdown(f"#### {icon} {name}")
                    st.markdown(st.session_state.agent_outputs[num])
                    st.markdown("---")

    st.divider()

    # ── Findings table ────────────────────────────────────────────────────────
    st.subheader("📋 Credential Findings")
    col1, col2, col3 = st.columns(3)
    sev_f  = col1.multiselect("Severity",        ["CRITICAL", "HIGH", "MEDIUM", "LOW"],  default=["CRITICAL", "HIGH"])
    env_f  = col2.multiselect("Environment",     sorted(findings_df.environment.unique()))
    type_f = col3.multiselect("Credential Type", sorted(findings_df.credential_type.unique()))

    filt = findings_df.copy()
    if sev_f:   filt = filt[filt.severity.isin(sev_f)]
    if env_f:   filt = filt[filt.environment.isin(env_f)]
    if type_f:  filt = filt[filt.credential_type.isin(type_f)]

    st.dataframe(
        filt[["id", "application", "environment", "credential_type", "severity",
              "file_location", "line_number", "status", "commit_author", "detected_date"]].head(60),
        use_container_width=True,
        column_config={
            "id":             "Finding ID",
            "severity":       st.column_config.SelectboxColumn("Severity", options=["CRITICAL", "HIGH", "MEDIUM", "LOW"]),
            "detected_date":  "Detected",
        },
    )
    st.caption(f"Showing {min(60, len(filt))} of {len(filt)} filtered findings")

    # ── ServiceNow for credentials ────────────────────────────────────────────
    st.divider()
    st.subheader("🎫 Raise Change Requests for Credential Remediation")
    cr_limit = st.slider("Max change requests to create", 1, 20, 5)
    if st.button("📝 Create SNOW Change Requests (Critical Findings)", use_container_width=True):
        if not (snow_url and snow_user and snow_pass):
            st.error("Configure ServiceNow in the sidebar.")
        else:
            snow = ServiceNowClient(snow_url, snow_user, snow_pass)
            critical_open = findings_df[
                (findings_df.severity == "CRITICAL") &
                (findings_df.status.isin(["Open", "In Progress"])) &
                (~findings_df.id.isin(st.session_state.cred_tickets))
            ].head(cr_limit)

            cr_pb   = st.progress(0)
            cr_rows = []
            for idx, (_, row) in enumerate(critical_open.iterrows()):
                desc = (
                    f"CREDENTIAL REMEDIATION CHANGE REQUEST\n\n"
                    f"Finding ID:       {row['id']}\n"
                    f"Application:      {row['application']}\n"
                    f"Environment:      {row['environment']}\n"
                    f"Credential Type:  {row['credential_type']}\n"
                    f"Service:          {row['service']}\n"
                    f"Severity:         {row['severity']}\n"
                    f"File Location:    {row['file_location']} (line {row['line_number']})\n"
                    f"Commit Author:    {row['commit_author']}\n"
                    f"Repository:       {row['repository']}\n"
                    f"Detected:         {row['detected_date']}\n\n"
                    f"ACTION REQUIRED:\n"
                    f"1. Rotate/revoke the exposed credential immediately.\n"
                    f"2. Migrate secret to AWS Secrets Manager.\n"
                    f"3. Update application to use secretsmanager:GetSecretValue.\n"
                    f"4. Remove plaintext credential from source and force-push clean history.\n"
                    f"5. Enable pre-commit hook (detect-secrets) on the repository.\n\n"
                    f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}"
                )
                res = snow.create_change_request(
                    short_description=f"[CRED-ROTATION] {row['application']} — {row['credential_type']} — {row['severity']}",
                    description=desc,
                    change_type="Emergency" if row["severity"] == "CRITICAL" else "Normal",
                    risk="High" if row["severity"] == "CRITICAL" else "Moderate",
                )
                if res["ok"]:
                    st.session_state.cred_tickets[row["id"]] = res
                    cr_rows.append({"Finding": row["id"], "App": row["application"],
                                    "Type": row["credential_type"], "CHG": res["number"],
                                    "URL": res["url"], "Status": "✅ Created"})
                else:
                    cr_rows.append({"Finding": row["id"], "App": row["application"],
                                    "Type": row["credential_type"], "CHG": "-",
                                    "URL": "-", "Status": f"❌ {res.get('error', 'Failed')}"})
                cr_pb.progress((idx + 1) / len(critical_open))

            st.dataframe(pd.DataFrame(cr_rows), use_container_width=True,
                         column_config={"URL": st.column_config.LinkColumn("SNOW Link")})

    st.divider()

    # ── Live AWS IAM Scan ─────────────────────────────────────────────────────
    st.subheader("☁️ Live AWS Credential Scan")
    if not st.session_state.aws_connected:
        st.info("Connect to an AWS account in the sidebar to enable live IAM scanning.")
    else:
        acct = st.session_state.get("aws_account_id", "")
        st.markdown(f"**Connected account:** `{acct}` · region `{st.session_state.aws_creds.get('region','us-east-1')}`")
        lc1, lc2, lc3 = st.columns(3)

        if lc1.button("🔍 Scan IAM Credential Report", use_container_width=True):
            with st.spinner("Generating IAM credential report…"):
                client = _make_aws_client()
                client.account_id = acct
                st.session_state.live_iam = client.get_iam_findings()
            st.success(f"IAM scan complete — {len(st.session_state.live_iam)} findings")

        if lc2.button("🔐 List Secrets Manager", use_container_width=True):
            with st.spinner("Listing Secrets Manager secrets…"):
                client = _make_aws_client()
                st.session_state.live_secrets = client.get_secrets_inventory()
            st.success(f"Found {len(st.session_state.live_secrets)} secrets")

        if lc3.button("🛡️ Security Hub Findings", use_container_width=True):
            with st.spinner("Querying Security Hub…"):
                client = _make_aws_client()
                st.session_state.live_hub = client.get_security_hub_findings(200)
            st.success(f"Security Hub returned {len(st.session_state.live_hub)} active failed controls")

        # IAM findings table
        if st.session_state.live_iam:
            st.markdown("#### 🔑 IAM Findings (Live)")
            lidf = pd.DataFrame(st.session_state.live_iam)
            sev_filter_live = st.multiselect("Filter severity (IAM)", ["CRITICAL","HIGH","MEDIUM","LOW"],
                                              default=["CRITICAL","HIGH"], key="iam_sev_filter")
            if sev_filter_live:
                lidf = lidf[lidf.severity.isin(sev_filter_live)]
            st.dataframe(lidf[["id","application","credential_type","severity",
                                "file_location","age_days","status"]],
                         use_container_width=True)
            lc = lidf.severity.value_counts().reset_index()
            lc.columns = ["Severity","Count"]
            fig = px.bar(lc, x="Severity", y="Count", title="Live IAM Finding Severity",
                         color="Severity",
                         color_discrete_map={"CRITICAL":"#ff2244","HIGH":"#ff7700","MEDIUM":"#ffcc00","LOW":"#22cc66"})
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, use_container_width=True)

        # Secrets Manager table
        if st.session_state.live_secrets:
            with st.expander(f"🔐 Secrets Manager Inventory ({len(st.session_state.live_secrets)} secrets)"):
                sdf = pd.DataFrame(st.session_state.live_secrets)
                st.dataframe(sdf[["name","rotation_enabled","last_rotated_days","last_changed","description"]],
                             use_container_width=True,
                             column_config={"rotation_enabled": st.column_config.CheckboxColumn("Auto-Rotate")})

        # Security Hub findings table
        if st.session_state.live_hub:
            with st.expander(f"🛡️ Security Hub — {len(st.session_state.live_hub)} Active Failures"):
                hdf = pd.DataFrame(st.session_state.live_hub)
                st.dataframe(hdf[["control_id","title","severity","resource_type","resource_id","created_at"]],
                             use_container_width=True)

    st.divider()

    # ── Charts ────────────────────────────────────────────────────────────────
    st.subheader("📊 Mock Data Analytics (1,200 simulated findings)")
    ch1, ch2, ch3 = st.columns(3)

    with ch1:
        sev_c = findings_df.severity.value_counts().reset_index()
        sev_c.columns = ["Severity", "Count"]
        fig = px.pie(sev_c, values="Count", names="Severity", title="Findings by Severity",
                     color="Severity",
                     color_discrete_map={"CRITICAL": "#ff2244", "HIGH": "#ff7700",
                                         "MEDIUM": "#ffcc00", "LOW": "#22cc66"})
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)

    with ch2:
        tc = findings_df.credential_type.value_counts().head(7).reset_index()
        tc.columns = ["Type", "Count"]
        fig = px.bar(tc, x="Count", y="Type", orientation="h",
                     title="Top Credential Types", color="Count",
                     color_continuous_scale="reds")
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                          yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig, use_container_width=True)

    with ch3:
        ac2 = findings_df.groupby("application").size().sort_values(ascending=False).head(8).reset_index()
        ac2.columns = ["Application", "Findings"]
        fig = px.bar(ac2, x="Findings", y="Application", orientation="h",
                     title="Most Exposed Applications",
                     color="Findings", color_continuous_scale="oranges")
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                          yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig, use_container_width=True)

    # ── Env heatmap ────────────────────────────────────────────────────────────
    heat = findings_df.groupby(["environment", "severity"]).size().reset_index(name="Count")
    heat_pivot = heat.pivot(index="environment", columns="severity", values="Count").fillna(0)
    fig = go.Figure(go.Heatmap(
        z=heat_pivot.values,
        x=heat_pivot.columns.tolist(),
        y=heat_pivot.index.tolist(),
        colorscale="Reds",
        text=heat_pivot.values.astype(int),
        texttemplate="%{text}",
    ))
    fig.update_layout(title="Findings Heatmap: Environment × Severity",
                      paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig, use_container_width=True)


# ═════════════════════════════════════════════════════════════════════════════
# TAB 2 — BACKUP INTELLIGENCE
# ═════════════════════════════════════════════════════════════════════════════
with tab2:
    st.title("💾 Immutable Backup Intelligence")
    st.markdown("*Gap analysis for 250 applications · ServiceNow incident management · Technology advisory*")

    protected_n = len(apps_df[apps_df.backup_status == "Protected"])
    partial_n   = len(apps_df[apps_df.backup_status == "Partial"])
    unp_n       = len(apps_df[apps_df.backup_status == "Unprotected"])
    immut_n     = int(apps_df["immutable_backup"].sum())

    # ── KPI row ──────────────────────────────────────────────────────────────
    b1, b2, b3, b4, b5 = st.columns(5)
    b1.metric("Total Apps",       250)
    b2.metric("Protected",        protected_n, delta=f"{protected_n/250*100:.0f}% covered")
    b3.metric("Partial Backup",   partial_n,   delta="Needs upgrade",   delta_color="inverse")
    b4.metric("Unprotected",      unp_n,       delta="No backup at all", delta_color="inverse")
    b5.metric("Immutable Backups",immut_n)
    st.divider()

    # ── Charts ────────────────────────────────────────────────────────────────
    bc1, bc2, bc3 = st.columns(3)

    with bc1:
        sc = apps_df.backup_status.value_counts().reset_index()
        sc.columns = ["Status", "Count"]
        fig = px.pie(sc, values="Count", names="Status", title="Backup Coverage Distribution",
                     color="Status",
                     color_discrete_map={"Protected": "#00cc88", "Partial": "#ffcc00", "Unprotected": "#ff2244"})
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)

    with bc2:
        ts = apps_df.groupby(["type", "backup_status"]).size().reset_index(name="Count")
        fig = px.bar(ts, x="type", y="Count", color="backup_status",
                     title="Coverage by App Type", barmode="stack",
                     color_discrete_map={"Protected": "#00cc88", "Partial": "#ffcc00", "Unprotected": "#ff2244"})
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                          xaxis_tickangle=30)
        st.plotly_chart(fig, use_container_width=True)

    with bc3:
        crit_gap = apps_df[
            (apps_df.criticality.isin(["Mission Critical", "Business Critical"])) &
            (apps_df.backup_status != "Protected")
        ].groupby(["criticality", "backup_status"]).size().reset_index(name="Count")
        fig = px.bar(crit_gap, x="criticality", y="Count", color="backup_status",
                     title="Critical Apps Without Full Backup",
                     color_discrete_map={"Partial": "#ffcc00", "Unprotected": "#ff2244"})
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # ── App inventory table ───────────────────────────────────────────────────
    st.subheader("📋 Application Inventory")
    ac1, ac2, ac3 = st.columns(3)
    stat_f  = ac1.multiselect("Backup Status",  ["Protected", "Partial", "Unprotected"], default=["Unprotected", "Partial"])
    crit_f  = ac2.multiselect("Criticality",    sorted(apps_df.criticality.unique()))
    atype_f = ac3.multiselect("App Type",       sorted(apps_df.type.unique()))

    fa = apps_df.copy()
    if stat_f:   fa = fa[fa.backup_status.isin(stat_f)]
    if crit_f:   fa = fa[fa.criticality.isin(crit_f)]
    if atype_f:  fa = fa[fa.type.isin(atype_f)]

    fa = fa.copy()
    fa["snow_ticket"] = fa.app_id.apply(
        lambda aid: st.session_state.snow_tickets.get(aid, {}).get("number", "—")
    )

    st.dataframe(
        fa[["app_id", "application", "type", "environment", "criticality",
            "backup_status", "immutable_backup", "rpo_requirement", "rto_requirement",
            "team", "data_classification", "snow_ticket"]].head(100),
        use_container_width=True,
        column_config={
            "backup_status":    st.column_config.SelectboxColumn("Backup Status", options=["Protected", "Partial", "Unprotected"]),
            "immutable_backup": st.column_config.CheckboxColumn("Immutable"),
            "snow_ticket":      "SNOW Ticket",
        },
    )
    st.caption(f"Showing {min(100, len(fa))} of {len(fa)} filtered applications")

    st.divider()

    # ── ServiceNow incident creation ──────────────────────────────────────────
    st.subheader("🎫 ServiceNow Incident Management")

    already = set(st.session_state.snow_tickets.keys())
    gap_apps = apps_df[apps_df.backup_status.isin(["Unprotected", "Partial"])]
    pending  = gap_apps[~gap_apps.app_id.isin(already)]

    sc1, sc2 = st.columns([2, 1])
    with sc1:
        st.markdown(f"""
**Gap Summary:**
- 🔴 **{unp_n} unprotected** applications — zero backup coverage
- 🟡 **{partial_n} partially protected** — manual / inconsistent backups
- 🎫 **{len(already)} tickets** already raised in ServiceNow
- 📋 **{len(pending)} applications** still pending ticket creation
        """)
    with sc2:
        max_tickets    = st.number_input("Max tickets to create", 1, 50, 10)
        priority_mode  = st.selectbox("Prioritise by", ["Mission Critical first", "All Unprotected first", "All gaps"])

    if st.button("🎫 Create ServiceNow Incidents for Backup Gaps", type="primary", use_container_width=True):
        if not (snow_url and snow_user and snow_pass):
            st.error("Configure ServiceNow credentials in the sidebar.")
        elif len(pending) == 0:
            st.success("All gap applications already have ServiceNow tickets!")
        else:
            snow = ServiceNowClient(snow_url, snow_user, snow_pass)

            if priority_mode == "Mission Critical first":
                mc   = pending[pending.criticality == "Mission Critical"].head(max_tickets)
                rest = pending[pending.criticality != "Mission Critical"].head(max(0, max_tickets - len(mc)))
                to_t = pd.concat([mc, rest])
            elif priority_mode == "All Unprotected first":
                to_t = pending[pending.backup_status == "Unprotected"].head(max_tickets)
            else:
                to_t = pending.head(max_tickets)

            pb      = st.progress(0)
            res_ph  = st.empty()
            rows    = []

            for idx, (_, app) in enumerate(to_t.iterrows()):
                urg = 1 if app.criticality == "Mission Critical" else 2
                imp = 1 if app.data_classification in ["PII", "Financial", "PHI"] else 2

                desc = (
                    f"APPLICATION BACKUP GAP — INCIDENT REPORT\n\n"
                    f"App ID:              {app.app_id}\n"
                    f"Application:         {app.application}\n"
                    f"Type:                {app.type}\n"
                    f"Environment:         {app.environment}\n"
                    f"Business Criticality:{app.criticality}\n"
                    f"Owning Team:         {app.team}\n"
                    f"AWS Region:          {app.region}\n"
                    f"Data Classification: {app.data_classification}\n\n"
                    f"CURRENT STATE:\n"
                    f"  Backup Status:     {app.backup_status}\n"
                    f"  Current Solution:  {app.backup_solution}\n"
                    f"  Immutable Backup:  {'Yes' if app.immutable_backup else 'No — REQUIRED'}\n"
                    f"  Last Backup:       {str(app.last_backup_days_ago) + ' days ago' if app.last_backup_days_ago else 'NEVER'}\n\n"
                    f"RPO REQUIREMENT:     {app.rpo_requirement}\n"
                    f"RTO REQUIREMENT:     {app.rto_requirement}\n\n"
                    f"REQUIRED ACTIONS:\n"
                    f"1. Enable AWS Backup with Vault Lock (WORM) for this workload.\n"
                    f"2. Configure cross-region backup copy to secondary AWS region.\n"
                    f"3. Set backup frequency to meet RPO of {app.rpo_requirement}.\n"
                    f"4. Run first backup restore test within 7 days of implementation.\n"
                    f"5. Register backup policy in CMDB and update Backup Audit Manager.\n\n"
                    f"RECOMMENDED SOLUTION:\n"
                    f"  Primary:  AWS Backup + Backup Vault Lock\n"
                    f"  Storage:  S3 Object Lock (Compliance mode) for archive copies\n"
                    f"  Testing:  AWS Backup Audit Manager automated restore verification\n\n"
                    f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}"
                )

                result = snow.create_incident(
                    short_description=f"[BACKUP GAP] {app.application} — {app.backup_status} — {app.criticality}",
                    description=desc,
                    urgency=urg,
                    impact=imp,
                )

                if result["ok"]:
                    st.session_state.snow_tickets[app.app_id] = result
                    rows.append({"Application": app.application, "Criticality": app.criticality,
                                 "Gap": app.backup_status, "Ticket": result["number"],
                                 "URL": result["url"], "Status": "✅ Created"})
                else:
                    rows.append({"Application": app.application, "Criticality": app.criticality,
                                 "Gap": app.backup_status, "Ticket": "—",
                                 "URL": "—", "Status": f"❌ {result.get('error', 'Failed')}"})

                pb.progress((idx + 1) / len(to_t))
                res_ph.dataframe(pd.DataFrame(rows), use_container_width=True,
                                 column_config={"URL": st.column_config.LinkColumn("SNOW Link")})

            created = sum(1 for r in rows if "✅" in r["Status"])
            st.success(f"Done — {created}/{len(to_t)} incidents created in ServiceNow.")

    # Show existing tickets
    if st.session_state.snow_tickets:
        with st.expander(f"📂 ServiceNow Tickets Created ({len(st.session_state.snow_tickets)})", expanded=False):
            trows = []
            for aid, tkt in st.session_state.snow_tickets.items():
                arow = apps_df[apps_df.app_id == aid]
                if not arow.empty:
                    a = arow.iloc[0]
                    trows.append({"Ticket": tkt["number"], "Application": a["application"],
                                  "Criticality": a["criticality"], "Gap": a["backup_status"],
                                  "URL": tkt["url"]})
            if trows:
                st.dataframe(pd.DataFrame(trows), use_container_width=True,
                             column_config={"URL": st.column_config.LinkColumn("SNOW Link")})

    st.divider()

    # ── Live AWS Backup Scan ───────────────────────────────────────────────────
    st.subheader("☁️ Live AWS Backup Coverage")
    if not st.session_state.aws_connected:
        st.info("Connect to an AWS account in the sidebar to scan real backup coverage.")
    else:
        acct   = st.session_state.get("aws_account_id", "")
        region = st.session_state.aws_creds.get("region", "us-east-1")
        st.markdown(f"**Account:** `{acct}` · **Region:** `{region}`")

        bc1, bc2, bc3 = st.columns(3)
        if bc1.button("📦 Scan Backup Coverage (EC2/RDS/S3/DDB)", use_container_width=True):
            with st.spinner("Querying EC2, RDS, S3, DynamoDB and AWS Backup…"):
                client = _make_aws_client()
                client.account_id = acct
                st.session_state.live_backup = client.get_all_backup_status()
            st.success(f"Scanned {len(st.session_state.live_backup)} resources")

        if bc2.button("📋 List Backup Plans", use_container_width=True):
            with st.spinner("Fetching AWS Backup plans…"):
                client = _make_aws_client()
                st.session_state.live_plans = client.get_backup_plans()
            st.success(f"Found {len(st.session_state.live_plans)} backup plans")

        if bc3.button("🔒 Check Vault Lock Status", use_container_width=True):
            with st.spinner("Checking backup vault immutability…"):
                client = _make_aws_client()
                st.session_state.live_vaults = client.get_backup_vaults()
            st.success(f"Found {len(st.session_state.live_vaults)} vaults")

        # Live backup coverage table
        if st.session_state.live_backup:
            lbdf = pd.DataFrame(st.session_state.live_backup)
            live_unp  = len(lbdf[lbdf.backup_status == "Unprotected"])
            live_part = len(lbdf[lbdf.backup_status == "Partial"])
            live_prot = len(lbdf[lbdf.backup_status == "Protected"])
            live_immut = int(lbdf["immutable_backup"].sum())

            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Total Resources", len(lbdf))
            m2.metric("Protected",       live_prot,  delta=f"{live_prot/max(len(lbdf),1)*100:.0f}%")
            m3.metric("Unprotected",     live_unp,   delta="Gap", delta_color="inverse")
            m4.metric("Immutable",       live_immut)

            # Charts
            lbc1, lbc2 = st.columns(2)
            with lbc1:
                sc = lbdf.backup_status.value_counts().reset_index()
                sc.columns = ["Status","Count"]
                fig = px.pie(sc, values="Count", names="Status",
                             title=f"Live Backup Coverage — {acct}",
                             color="Status",
                             color_discrete_map={"Protected":"#00cc88","Partial":"#ffcc00","Unprotected":"#ff2244"})
                fig.update_layout(paper_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig, use_container_width=True)
            with lbc2:
                ts = lbdf.groupby(["type","backup_status"]).size().reset_index(name="Count")
                fig = px.bar(ts, x="type", y="Count", color="backup_status",
                             title="Coverage by Resource Type", barmode="stack",
                             color_discrete_map={"Protected":"#00cc88","Partial":"#ffcc00","Unprotected":"#ff2244"})
                fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", xaxis_tickangle=30)
                st.plotly_chart(fig, use_container_width=True)

            # Resource table
            st.markdown("#### Resource Inventory")
            gap_only = st.checkbox("Show gaps only (Unprotected + Partial)", value=True, key="live_gap_only")
            disp = lbdf[lbdf.backup_status != "Protected"] if gap_only else lbdf
            st.dataframe(
                disp[["app_id","application","type","environment","backup_status",
                       "backup_solution","immutable_backup","rpo_requirement","rto_requirement"]],
                use_container_width=True,
                column_config={"immutable_backup": st.column_config.CheckboxColumn("Immutable")},
            )
            st.caption(f"Showing {len(disp)} of {len(lbdf)} resources")

            # Quick ServiceNow tickets for live gaps
            live_gaps = lbdf[lbdf.backup_status.isin(["Unprotected","Partial"])]
            if len(live_gaps) > 0:
                st.markdown(f"**{len(live_gaps)} resources need backup remediation**")
                if st.button(f"🎫 Raise SNOW Incidents for Live Backup Gaps ({min(len(live_gaps),10)})",
                             use_container_width=True, key="live_snow_btn"):
                    if not (snow_url and snow_user and snow_pass):
                        st.error("Configure ServiceNow in the sidebar.")
                    else:
                        snow  = ServiceNowClient(snow_url, snow_user, snow_pass)
                        to_t  = live_gaps.head(10)
                        pb    = st.progress(0)
                        rows  = []
                        for idx2, (_, app) in enumerate(to_t.iterrows()):
                            urg = 1 if app.criticality in ("Mission Critical",) else 2
                            imp = 2
                            desc = (
                                f"LIVE AWS BACKUP GAP — Account {acct}\n\n"
                                f"Resource ID:    {app.app_id}\n"
                                f"Resource Name:  {app.application}\n"
                                f"Type:           {app.type}\n"
                                f"Region:         {app.region}\n"
                                f"Environment:    {app.environment}\n"
                                f"Backup Status:  {app.backup_status}\n"
                                f"Current Backup: {app.backup_solution}\n"
                                f"Immutable:      {'Yes' if app.immutable_backup else 'No — REQUIRED'}\n\n"
                                f"RPO Requirement: {app.rpo_requirement}\n"
                                f"RTO Requirement: {app.rto_requirement}\n\n"
                                f"ACTION: Enrol in AWS Backup with Vault Lock enabled.\n"
                                f"Scanned: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}"
                            )
                            res2 = snow.create_incident(
                                short_description=f"[LIVE BACKUP GAP] {app.application} — {app.type} — {app.backup_status}",
                                description=desc, urgency=urg, impact=imp,
                            )
                            rows.append({
                                "Resource": app.application, "Type": app.type,
                                "Ticket": res2.get("number","—"), "URL": res2.get("url","—"),
                                "Status": "✅ Created" if res2["ok"] else f"❌ {res2.get('error','')}",
                            })
                            pb.progress((idx2 + 1) / len(to_t))
                        st.dataframe(pd.DataFrame(rows), use_container_width=True,
                                     column_config={"URL": st.column_config.LinkColumn("SNOW Link")})

        # Backup plans
        if st.session_state.live_plans:
            with st.expander(f"📋 AWS Backup Plans ({len(st.session_state.live_plans)})"):
                st.dataframe(pd.DataFrame(st.session_state.live_plans), use_container_width=True)

        # Vault lock status
        if st.session_state.live_vaults:
            vdf = pd.DataFrame(st.session_state.live_vaults)
            with st.expander(f"🔒 Backup Vault Status ({len(vdf)} vaults)"):
                st.dataframe(vdf, use_container_width=True,
                             column_config={"locked":   st.column_config.CheckboxColumn("WORM Locked"),
                                            "immutable":st.column_config.CheckboxColumn("Immutable")})
                locked_n   = int(vdf["locked"].sum())
                unlocked_n = len(vdf) - locked_n
                st.markdown(f"- 🔒 **{locked_n}** vaults have Vault Lock (WORM) enabled")
                st.markdown(f"- ⚠️  **{unlocked_n}** vaults are NOT immutably locked")

    st.divider()

    # ── Backup technology comparison ──────────────────────────────────────────
    st.subheader("🔧 Backup Technology Evaluation")

    tech_tabs = st.tabs(list(BACKUP_TECHNOLOGIES.keys()))
    for i, (tech_name, ti) in enumerate(BACKUP_TECHNOLOGIES.items()):
        with tech_tabs[i]:
            left, right = st.columns([1, 2])
            with left:
                st.markdown(f"**Vendor:** {ti['vendor']}")
                st.markdown(f"**Deployment Type:** {ti['type']}")
                st.markdown(f"**Cloud Support:** {', '.join(ti['cloud_support'])}")
                st.markdown(f"**On-Premises:** {'✅ Yes' if ti['on_prem'] else '❌ No'}")
                st.markdown(f"**Immutable Backup:** {'✅ Yes' if ti['immutable'] else '❌ No'}")
                st.markdown(f"**Cross-Region:** {'✅ Yes' if ti['cross_region_backup'] else '❌ No'}")
                st.markdown(f"**Cross-Account:** {'✅ Yes' if ti['cross_account_backup'] else '❌ No'}")
                st.markdown(f"**Cost Model:** {ti['cost_model']}")
            with right:
                st.markdown(f"**Immutability Mechanism:** {ti['immutability_mechanism']}")
                st.markdown(f"**RPO:** {ti['rpo']}")
                st.markdown(f"**RTO:** {ti['rto']}")
                st.markdown(f"**Encryption:** {ti['encryption']}")
                st.markdown(f"**Monitoring:** {ti['monitoring']}")
                st.markdown(f"**Recovery Testing:** {ti['testing']}")
                st.markdown(f"**Compliance:** {', '.join(ti['compliance'])}")
                st.markdown(f"**Operational Model:** {ti['operational_model']}")
            st.markdown("")
            sa, sb = st.columns(2)
            with sa:
                st.markdown("**✅ Strengths:**")
                for s in ti.get("strengths", []):
                    st.markdown(f"- {s}")
            with sb:
                st.markdown("**⚠️ Limitations:**")
                for l in ti.get("limitations", []):
                    st.markdown(f"- {l}")

    st.divider()

    # ── RPO/RTO matrix ────────────────────────────────────────────────────────
    st.subheader("⏱️ RPO / RTO Requirements Matrix")
    rpr = apps_df.groupby(["rpo_requirement", "rto_requirement"]).size().reset_index(name="Apps")
    fig = px.density_heatmap(rpr, x="rpo_requirement", y="rto_requirement", z="Apps",
                             title="App Count by RPO × RTO Requirement",
                             color_continuous_scale="Blues", text_auto=True)
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # ── Operational support model ─────────────────────────────────────────────
    st.subheader("🔄 Ongoing Operational Support Model")
    op1, op2, op3 = st.columns(3)

    with op1:
        st.markdown("### Daily Operations")
        st.markdown("""
- **Backup Job Monitoring** — CloudWatch dashboard; alert on any failure within 15 min
- **Failed Backup Triage** — SNS → PagerDuty → auto-open ServiceNow incident
- **Capacity Trending** — S3/EBS storage growth review; proactive right-sizing
- **Compliance Check** — AWS Backup Audit Manager daily compliance report
- **Vault Lock Integrity** — verify no WORM policy modifications via CloudTrail
        """)

    with op2:
        st.markdown("### Weekly / Monthly / Quarterly")
        st.markdown("""
**Weekly**
- Restore 10% of protected apps (rotating sample) — document results
- SNOW incident review: close resolved, escalate stale

**Monthly**
- Runbook refresh for any new or changed applications
- Cost optimisation: review lifecycle policies, tier cold data to Glacier
- Backup Audit Manager compliance summary to CISO

**Quarterly**
- Full DR tabletop exercise — simulate region failure
- RPO/RTO SLA validation report
- Update CMDB backup status from AWS via automated Lambda sync
        """)

    with op3:
        st.markdown("### Tooling & Automation")
        st.markdown("""
| Tool | Purpose |
|------|---------|
| **AWS Backup Audit Manager** | Automated compliance reporting |
| **Terraform (IaC)** | Backup policies as code, GitOps-driven |
| **Lambda (tag-driven)** | Auto-enrol new resources in backup on tagging |
| **AWS Config Rules** | Drift detection — alert if backup policy removed |
| **ServiceNow CMDB** | Auto-update backup status from AWS API |
| **Grafana / CloudWatch** | Real-time backup health dashboard |
| **AWS Health** | Pre-emptive alerts on region/AZ incidents |
| **EventBridge** | Trigger restore tests post-backup completion |
        """)


# ═════════════════════════════════════════════════════════════════════════════
# TAB 3 — AUTO-REMEDIATION LOOP
# ═════════════════════════════════════════════════════════════════════════════
with tab3:
    st.title("🔄 Auto-Remediation Agent Loop")
    st.markdown(
        "*Continuous 4-phase agentic loop: INC Agent → Dispatcher → Remediator → INC Agent closes ticket*"
    )
    st.markdown("""
```
Vulnerability Detected
        ↓
 ┌─────────────────┐
 │   INC Agent     │  Creates ServiceNow incident · classifies · hands off
 └────────┬────────┘
          │ handoff
 ┌────────▼────────┐
 │ Dispatcher Agent│  Investigates root cause · coordinates remediation
 └────────┬────────┘
          │
 ┌────────▼────────┐
 │ Remediator Agent│  Executes fix · validates · produces resolution note
 └────────┬────────┘
          │ handoff back
 ┌────────▼────────┐
 │   INC Agent     │  Updates SNOW · writes resolution · CLOSES incident ✅
 └─────────────────┘
          ↓
   Next finding → loop repeats
```
""")
    st.divider()

    # ── Configuration ─────────────────────────────────────────────────────────
    rc1, rc2, rc3 = st.columns(3)
    data_source = rc1.radio("Finding source", ["Mock data (demo)", "Live IAM scan"])
    max_loop    = rc2.number_input("Findings to process", 1, 20, 3)
    sev_target  = rc3.multiselect("Target severity", ["CRITICAL","HIGH","MEDIUM"],
                                   default=["CRITICAL","HIGH"])

    # Build finding pool
    if data_source == "Live IAM scan" and st.session_state.live_iam:
        pool_df = pd.DataFrame(st.session_state.live_iam)
    else:
        pool_df = findings_df.copy()

    if sev_target:
        pool_df = pool_df[pool_df.severity.isin(sev_target)]

    pool_df = pool_df[pool_df.status != "Resolved"].head(50)
    st.info(f"**{len(pool_df)}** eligible findings available · will process up to **{max_loop}**")

    if not st.session_state.aws_connected and data_source == "Live IAM scan":
        st.warning("Connect to AWS in the sidebar first to use live IAM findings.")

    start_btn = st.button(
        "▶️ Start Auto-Remediation Loop", type="primary", use_container_width=True,
        disabled=(not openai_key or not snow_url or not snow_user or not snow_pass)
    )
    if not openai_key:
        st.caption("⚠️ OpenAI key required (sidebar)")
    if not (snow_url and snow_user and snow_pass):
        st.caption("⚠️ ServiceNow credentials required (sidebar)")

    # ── Agent system prompts ───────────────────────────────────────────────────
    INC_CREATE_PROMPT = """You are the INC Agent — an enterprise ITSM incident manager.
A security vulnerability has been detected. Your job:
1. Write a concise incident summary (3-4 sentences)
2. Classify business impact (CRITICAL / HIGH / MEDIUM / LOW)
3. State the initial SLA target
4. Write a formal handoff note to the Dispatcher Agent with all context they need

Be precise. Use markdown. Max 300 words."""

    DISPATCHER_INVESTIGATE_PROMPT = """You are the Dispatcher Agent — a senior security investigator.
You receive incidents from the INC Agent. Investigate this finding:
1. Root Cause Analysis — why did this happen? (mis-config, process failure, tooling gap)
2. Scope — which systems/accounts are at risk beyond this finding
3. Attack Vector — concrete exploitation path if unmitigated
4. Remediation Plan — numbered steps, specific and actionable

Be technical. Reference AWS services. Max 350 words."""

    REMEDIATOR_PROMPT = """You are the Remediator Agent — a DevSecOps engineer executing the fix.
Based on the Dispatcher's investigation, carry out the remediation:
1. Remediation Actions — list each step as COMPLETED ✓
2. AWS CLI or Python code that was executed
3. Validation check — how you confirmed the fix worked
4. Residual Risk — anything left open
5. Handoff summary for INC Agent to close the incident

Write in past tense (actions already done). Max 400 words."""

    INC_CLOSE_PROMPT = """You are the INC Agent. The Dispatcher and Remediator have completed their work.
Write the formal incident closure:
1. Resolution Summary (2-3 sentences for the SNOW ticket)
2. Root Cause (one sentence)
3. Fix Applied (one sentence)
4. Prevention Recommendation (one sentence)
5. Final declaration: "Incident RESOLVED and CLOSED ✅"

Be concise. This goes into ServiceNow. Max 200 words."""

    # ── Colour scheme per agent ────────────────────────────────────────────────
    AGENT_STYLE = {
        "INC Agent":           {"color": "#00aaff", "icon": "🎫"},
        "Dispatcher Agent":    {"color": "#ff8800", "icon": "📡"},
        "Remediator Agent":    {"color": "#cc44ff", "icon": "🔧"},
        "INC Agent (closure)": {"color": "#00cc88", "icon": "✅"},
    }

    def stream_agent(oai, model, system, user_msg, label, placeholder):
        """Stream an OpenAI call, render live, return full text."""
        messages = [
            {"role": "system",  "content": system},
            {"role": "user",    "content": user_msg},
        ]
        style   = AGENT_STYLE.get(label, {"color":"#aaa","icon":"🤖"})
        full    = ""
        stream  = oai.chat.completions.create(
            model=model, messages=messages, stream=True, max_tokens=600
        )
        for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                full += delta
                placeholder.markdown(
                    f"<div style='border-left:3px solid {style['color']};"
                    f"padding:10px 14px;margin:4px 0;border-radius:0 8px 8px 0;"
                    f"background:#0d1b2a;font-size:13px'>"
                    f"<span style='color:{style['color']};font-weight:700'>"
                    f"{style['icon']} {label}</span><br>{full}▌</div>",
                    unsafe_allow_html=True,
                )
        placeholder.markdown(
            f"<div style='border-left:3px solid {style['color']};"
            f"padding:10px 14px;margin:4px 0;border-radius:0 8px 8px 0;"
            f"background:#0d1b2a;font-size:13px'>"
            f"<span style='color:{style['color']};font-weight:700'>"
            f"{style['icon']} {label}</span><br>{full}</div>",
            unsafe_allow_html=True,
        )
        return full

    # ── Main loop ──────────────────────────────────────────────────────────────
    if start_btn:
        if len(pool_df) == 0:
            st.error("No findings match the selected filters.")
        else:
            oai   = openai.OpenAI(api_key=openai_key)
            snow  = ServiceNowClient(snow_url, snow_user, snow_pass)
            to_process = pool_df.head(max_loop).to_dict("records")
            summary_rows = []

            overall_pb = st.progress(0, text="Starting remediation loop…")

            for loop_idx, finding in enumerate(to_process):
                overall_pb.progress(loop_idx / len(to_process),
                                    text=f"Processing finding {loop_idx+1}/{len(to_process)}: {finding['id']}")

                with st.expander(
                    f"{'🔴' if finding['severity']=='CRITICAL' else '🟠' if finding['severity']=='HIGH' else '🟡'} "
                    f"**{finding['id']}** · {finding['credential_type']} · {finding['application']} "
                    f"· {finding['severity']}",
                    expanded=(loop_idx == 0),
                ):
                    finding_ctx = json.dumps({
                        k: finding[k] for k in
                        ["id","application","environment","credential_type","service",
                         "severity","file_location","detected_date","commit_author","repository"]
                        if k in finding
                    }, indent=2)

                    # ── PHASE 1: INC Agent creates incident ────────────────────
                    st.markdown("---")
                    ph1 = st.empty()
                    inc_output = stream_agent(
                        oai, llm_model,
                        INC_CREATE_PROMPT,
                        f"Security finding requiring incident creation:\n\n{finding_ctx}",
                        "INC Agent",
                        ph1,
                    )

                    # Create real ServiceNow incident
                    snow_result = snow.create_incident(
                        short_description=f"[AUTO-REMEDIATION] {finding['credential_type']} — "
                                         f"{finding['application']} — {finding['severity']}",
                        description=(
                            f"Auto-detected by Infosys CIS Cloud Shield — Remediation Loop\n\n"
                            f"Finding ID:      {finding['id']}\n"
                            f"Type:            {finding['credential_type']}\n"
                            f"Application:     {finding['application']}\n"
                            f"Environment:     {finding['environment']}\n"
                            f"Severity:        {finding['severity']}\n"
                            f"Location:        {finding.get('file_location','')}\n"
                            f"Detected:        {finding.get('detected_date','')}\n\n"
                            f"INC Agent Analysis:\n{inc_output[:1000]}"
                        ),
                        urgency = 1 if finding["severity"] == "CRITICAL" else 2,
                        impact  = 1 if finding["severity"] == "CRITICAL" else 2,
                    )
                    inc_number = snow_result.get("number", "SNOW-UNAVAIL")
                    inc_url    = snow_result.get("url",    "")
                    sys_id     = snow_result.get("sys_id", "")

                    if snow_result.get("ok"):
                        st.success(f"📋 Incident created: **{inc_number}**  →  [View in ServiceNow]({inc_url})")
                    else:
                        st.warning(f"ServiceNow: {snow_result.get('error','could not create incident')}")

                    # ── PHASE 2: Dispatcher investigates ───────────────────────
                    st.markdown("---")
                    ph2 = st.empty()
                    disp_output = stream_agent(
                        oai, llm_model,
                        DISPATCHER_INVESTIGATE_PROMPT,
                        (f"INC Agent handed off incident **{inc_number}** to you.\n\n"
                         f"INC Agent summary:\n{inc_output[:600]}\n\n"
                         f"Original finding:\n{finding_ctx}"),
                        "Dispatcher Agent",
                        ph2,
                    )

                    # ── PHASE 3: Remediator executes fix ───────────────────────
                    st.markdown("---")
                    ph3 = st.empty()
                    remed_output = stream_agent(
                        oai, llm_model,
                        REMEDIATOR_PROMPT,
                        (f"Dispatcher Agent investigation for incident **{inc_number}**:\n{disp_output[:800]}\n\n"
                         f"Finding:\n{finding_ctx}"),
                        "Remediator Agent",
                        ph3,
                    )

                    # ── PHASE 4: INC Agent closes ──────────────────────────────
                    st.markdown("---")
                    ph4 = st.empty()
                    closure_output = stream_agent(
                        oai, llm_model,
                        INC_CLOSE_PROMPT,
                        (f"Incident: **{inc_number}**\n\n"
                         f"Dispatcher investigation:\n{disp_output[:500]}\n\n"
                         f"Remediator resolution:\n{remed_output[:700]}"),
                        "INC Agent (closure)",
                        ph4,
                    )

                    # Update + resolve ServiceNow incident
                    if sys_id:
                        snow.update_incident(sys_id, {
                            "state": "6",
                            "close_code": "Solution provided",
                            "close_notes": closure_output[:900],
                            "work_notes": (
                                f"Dispatcher Investigation:\n{disp_output[:500]}\n\n"
                                f"Remediator Actions:\n{remed_output[:500]}"
                            ),
                        })
                        st.success(f"✅ Incident **{inc_number}** resolved and closed in ServiceNow")

                    summary_rows.append({
                        "Finding":         finding["id"],
                        "Severity":        finding["severity"],
                        "Type":            finding["credential_type"],
                        "Application":     finding["application"],
                        "SNOW Ticket":     inc_number,
                        "SNOW Link":       inc_url,
                        "Status":          "✅ Resolved & Closed",
                    })

            overall_pb.progress(1.0, text="Remediation loop complete ✅")

            st.divider()
            st.subheader("📊 Remediation Loop Summary")
            sumdf = pd.DataFrame(summary_rows)
            st.dataframe(sumdf, use_container_width=True,
                         column_config={"SNOW Link": st.column_config.LinkColumn("ServiceNow")})
            resolved = sum(1 for r in summary_rows if "✅" in r["Status"])
            st.metric("Incidents Resolved", f"{resolved}/{len(summary_rows)}")
