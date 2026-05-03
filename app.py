"""
AWS Security & Backup Intelligence Platform
Two-module Streamlit prototype using OpenAI multi-agent orchestration and ServiceNow integration.
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

# ── Page config (must be first Streamlit call) ────────────────────────────────
st.set_page_config(
    page_title="AWS Security & Backup Intelligence",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
[data-testid="stSidebar"] { background:#0d1117; }
.agent-card {
    background:#0d1b2a; border:1px solid #1f3a5f;
    border-radius:10px; padding:14px 16px; margin-bottom:10px; text-align:center;
}
.agent-idle   { border-color:#334; }
.agent-active { border-color:#00aaff; box-shadow:0 0 14px rgba(0,170,255,0.25); }
.agent-done   { border-color:#00cc88; }
.kpi-box {
    background:#111827; border:1px solid #1f2937;
    border-radius:8px; padding:14px; text-align:center;
}
.snow-row { background:#0f2218; border:1px solid #1a4a2a; border-radius:6px; padding:8px 12px; margin:4px 0; }
</style>
""", unsafe_allow_html=True)

# ── Session state initialisation ──────────────────────────────────────────────
if "findings" not in st.session_state:
    st.session_state.findings = get_credential_findings(1200)
if "apps" not in st.session_state:
    st.session_state.apps = get_app_inventory(250)
if "agent_outputs" not in st.session_state:
    st.session_state.agent_outputs = {}
if "agent_statuses" not in st.session_state:
    st.session_state.agent_statuses = {1: "idle", 2: "idle", 3: "idle", 4: "idle"}
if "snow_tickets" not in st.session_state:
    st.session_state.snow_tickets = {}      # app_id → {number, sys_id, url}
if "cred_tickets" not in st.session_state:
    st.session_state.cred_tickets = {}      # finding_id → {number, sys_id, url}

findings_df = pd.DataFrame(st.session_state.findings)
apps_df     = pd.DataFrame(st.session_state.apps)

# ── Load secrets (Streamlit Cloud injects these; sidebar inputs used as fallback) ──
_secrets = st.secrets if hasattr(st, "secrets") else {}
_oai_from_secrets   = _secrets.get("OPENAI_API_KEY", "")
_snow_url_default   = _secrets.get("SNOW_URL",  "https://dev218436.service-now.com")
_snow_user_default  = _secrets.get("SNOW_USER", "admin")
_snow_pass_default  = _secrets.get("SNOW_PASS", "")

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
tab1, tab2 = st.tabs([
    "🔐  Credential Intelligence",
    "💾  Backup Intelligence",
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

    # ── Charts ────────────────────────────────────────────────────────────────
    st.subheader("📊 Analytics")
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
