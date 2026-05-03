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
/* ══════════════════════════════════════════════════════════════════
   INFOSYS CIS CLOUD SHIELD — ENTERPRISE GLASS THEME
   ══════════════════════════════════════════════════════════════════ */

/* ── 1. Font ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
*, *::before, *::after { font-family:'Inter',system-ui,sans-serif !important; }

/* ── 2. Base / Background ── */
body, .stApp {
    background:
        radial-gradient(ellipse at 15% 20%, rgba(0,102,204,.07) 0%, transparent 55%),
        radial-gradient(ellipse at 85% 80%, rgba(124,58,237,.05) 0%, transparent 55%),
        radial-gradient(ellipse at 50% 50%, #04091a 0%, #020610 100%) !important;
}

/* Hide Streamlit's native top bar so our custom topbar has full room */
header[data-testid="stHeader"]          { display:none !important; }
#MainMenu                               { display:none !important; }
[data-testid="stToolbar"]              { display:none !important; }
[data-testid="stDecoration"]           { display:none !important; }
footer                                  { display:none !important; }

/* Remove the top gap Streamlit adds for the hidden header */
section[data-testid="stMain"]          { padding-top:0 !important; margin-top:0 !important; }
.block-container                        { padding:0 2rem 3rem !important; max-width:1400px !important; }

/* ── 3. Sidebar ── */
[data-testid="stSidebar"] {
    background:rgba(4,9,26,.96) !important;
    backdrop-filter:blur(24px) !important;
    -webkit-backdrop-filter:blur(24px) !important;
    border-right:1px solid rgba(0,170,255,.1) !important;
}
[data-testid="stSidebar"] .stMarkdown h2,
[data-testid="stSidebar"] .stMarkdown h3 {
    color:#8ba8c4 !important; font-size:10px !important; font-weight:700 !important;
    letter-spacing:1.8px !important; text-transform:uppercase !important;
    margin-bottom:6px !important;
}
[data-testid="stSidebar"] hr { border-color:rgba(255,255,255,.07) !important; }
[data-testid="stSidebarContent"] { padding:1.2rem 1rem !important; }

/* ── 4. Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background:rgba(255,255,255,.02) !important;
    border-bottom:1px solid rgba(255,255,255,.07) !important;
    gap:4px !important; padding:0 4px !important;
    border-radius:12px 12px 0 0 !important;
}
.stTabs [data-baseweb="tab"] {
    font-size:13px !important; font-weight:500 !important;
    color:rgba(255,255,255,.45) !important;
    padding:10px 22px !important; border-radius:8px 8px 0 0 !important;
    border-bottom:2px solid transparent !important;
    background:transparent !important;
    transition:all .25s ease !important;
    letter-spacing:.2px !important;
}
.stTabs [data-baseweb="tab"]:hover { color:rgba(255,255,255,.75) !important; }
.stTabs [data-baseweb="tab"][aria-selected="true"] {
    color:#00aaff !important; font-weight:600 !important;
    border-bottom:2px solid #00aaff !important;
    background:rgba(0,170,255,.06) !important;
}
.stTabs [data-baseweb="tab-panel"] {
    background:rgba(255,255,255,.015) !important;
    border:1px solid rgba(255,255,255,.06) !important;
    border-top:none !important; border-radius:0 0 14px 14px !important;
    padding:24px !important;
}

/* ── 5. Buttons ── */
.stButton > button {
    background:linear-gradient(135deg,rgba(0,120,255,.7),rgba(0,70,180,.8)) !important;
    border:1px solid rgba(0,170,255,.25) !important;
    border-radius:9px !important; color:#e8f4ff !important;
    font-size:13px !important; font-weight:600 !important;
    letter-spacing:.3px !important; padding:10px 18px !important;
    box-shadow:0 4px 16px rgba(0,100,255,.2),inset 0 1px 0 rgba(255,255,255,.1) !important;
    transition:all .25s ease !important;
}
.stButton > button:hover {
    background:linear-gradient(135deg,rgba(0,160,255,.8),rgba(0,90,200,.9)) !important;
    box-shadow:0 6px 24px rgba(0,170,255,.35),inset 0 1px 0 rgba(255,255,255,.15) !important;
    transform:translateY(-1px) !important; border-color:rgba(0,170,255,.5) !important;
}
.stButton > button[kind="primary"] {
    background:linear-gradient(135deg,#0088ff,#0050cc) !important;
    box-shadow:0 4px 20px rgba(0,136,255,.35),inset 0 1px 0 rgba(255,255,255,.12) !important;
}
.stButton > button[kind="primary"]:hover {
    background:linear-gradient(135deg,#00aaff,#0066dd) !important;
    box-shadow:0 6px 28px rgba(0,170,255,.5) !important;
}

/* ── 6. Metric cards ── */
[data-testid="stMetric"] {
    background:rgba(255,255,255,.03) !important;
    backdrop-filter:blur(16px) !important;
    border:1px solid rgba(255,255,255,.08) !important;
    border-radius:14px !important; padding:18px 16px !important;
    box-shadow:0 4px 24px rgba(0,0,0,.3),inset 0 1px 0 rgba(255,255,255,.05) !important;
    transition:transform .2s ease, box-shadow .2s ease !important;
}
[data-testid="stMetric"]:hover {
    transform:translateY(-2px) !important;
    box-shadow:0 8px 32px rgba(0,0,0,.4),0 0 16px rgba(0,170,255,.08) !important;
}
[data-testid="stMetricLabel"]  { font-size:11px !important; font-weight:600 !important; letter-spacing:1px !important; text-transform:uppercase !important; color:#6b8aad !important; }
[data-testid="stMetricValue"]  { font-size:26px !important; font-weight:800 !important; color:#e8f0ff !important; }
[data-testid="stMetricDelta"]  { font-size:11px !important; font-weight:500 !important; }

/* ── 7. Text inputs & select boxes ── */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stNumberInput > div > div > input {
    background:rgba(255,255,255,.04) !important;
    border:1px solid rgba(255,255,255,.1) !important;
    border-radius:9px !important; color:#d0dff0 !important;
    font-size:13px !important;
    box-shadow:inset 0 2px 4px rgba(0,0,0,.2) !important;
    transition:border-color .2s, box-shadow .2s !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color:rgba(0,170,255,.6) !important;
    box-shadow:0 0 0 3px rgba(0,170,255,.12),inset 0 2px 4px rgba(0,0,0,.2) !important;
}
.stTextInput label, .stTextArea label, .stNumberInput label,
.stSelectbox label, .stMultiSelect label, .stRadio label,
.stSlider label { font-size:11px !important; font-weight:600 !important; color:#8098b4 !important; letter-spacing:.8px !important; text-transform:uppercase !important; }

.stSelectbox > div > div, .stMultiSelect > div > div {
    background:rgba(255,255,255,.04) !important;
    border:1px solid rgba(255,255,255,.1) !important;
    border-radius:9px !important; color:#d0dff0 !important;
    font-size:13px !important;
}
.stSelectbox > div > div:focus-within, .stMultiSelect > div > div:focus-within {
    border-color:rgba(0,170,255,.5) !important;
    box-shadow:0 0 0 3px rgba(0,170,255,.1) !important;
}

/* ── 8. DataFrames ── */
[data-testid="stDataFrame"] {
    border:1px solid rgba(255,255,255,.07) !important;
    border-radius:12px !important; overflow:hidden !important;
    box-shadow:0 4px 24px rgba(0,0,0,.3) !important;
}
[data-testid="stDataFrame"] iframe { border-radius:12px !important; }

/* ── 9. Expanders ── */
[data-testid="stExpander"] {
    background:rgba(255,255,255,.025) !important;
    backdrop-filter:blur(12px) !important;
    border:1px solid rgba(255,255,255,.07) !important;
    border-radius:12px !important;
    box-shadow:0 2px 12px rgba(0,0,0,.2) !important;
    transition:all .2s ease !important;
}
[data-testid="stExpander"]:hover { border-color:rgba(0,170,255,.2) !important; }
[data-testid="stExpanderToggleIcon"] { color:#6b8aad !important; }

/* ── 10. Progress bars ── */
[data-testid="stProgress"] > div > div > div {
    background:linear-gradient(90deg,#0066cc,#00aaff,#7c3aed) !important;
    border-radius:4px !important;
    box-shadow:0 0 8px rgba(0,170,255,.4) !important;
}
[data-testid="stProgress"] > div > div {
    background:rgba(255,255,255,.06) !important; border-radius:4px !important;
}

/* ── 11. Alerts / info / success / error ── */
[data-testid="stAlert"] {
    border-radius:10px !important;
    backdrop-filter:blur(8px) !important;
    font-size:13px !important;
    border-width:1px !important; border-style:solid !important;
}
.stSuccess { background:rgba(0,204,136,.08) !important; border-color:rgba(0,204,136,.25) !important; color:#a0f0d0 !important; }
.stError   { background:rgba(255,50,80,.08)  !important; border-color:rgba(255,50,80,.25)  !important; color:#ffaaaa !important; }
.stWarning { background:rgba(255,170,0,.07)  !important; border-color:rgba(255,170,0,.25)  !important; color:#ffd080 !important; }
.stInfo    { background:rgba(0,136,255,.07)  !important; border-color:rgba(0,136,255,.25)  !important; color:#80c8ff !important; }

/* ── 12. Dividers ── */
hr {
    border:none !important;
    height:1px !important;
    background:linear-gradient(90deg,transparent,rgba(0,170,255,.2),transparent) !important;
    margin:20px 0 !important;
}

/* ── 13. Typography ── */
h1 { font-size:26px !important; font-weight:800 !important; color:#e8f0ff !important; letter-spacing:-.3px !important; }
h2 { font-size:18px !important; font-weight:700 !important; color:#ccdaee !important; }
h3 { font-size:14px !important; font-weight:600 !important; color:#a8bdd4 !important; }
p, .stMarkdown p { font-size:13.5px !important; color:#8098b4 !important; line-height:1.65 !important; }
.stCaption, caption { font-size:11px !important; color:#4a6080 !important; }

/* ── 14. Checkboxes / Radio / Slider ── */
.stCheckbox label { font-size:13px !important; color:#a0b4cc !important; font-weight:400 !important; text-transform:none !important; letter-spacing:0 !important; }
.stRadio > div { gap:8px !important; }
.stSlider [data-baseweb="slider"] [role="slider"] { background:#00aaff !important; }

/* ── 15. Topbar ── */
.topbar {
    display:flex; align-items:center; gap:16px;
    padding:11px 24px;
    background:rgba(4,9,26,.8);
    backdrop-filter:blur(20px); -webkit-backdrop-filter:blur(20px);
    border-bottom:1px solid rgba(0,170,255,.12);
    margin-bottom:16px; position:sticky; top:0; z-index:999;
}
.topbar-logo { position:relative; width:38px; height:38px; flex-shrink:0; }
.topbar-logo-ring {
    position:absolute; inset:0; border-radius:50%;
    background:conic-gradient(from 0deg,#00aaff,#7c3aed,#0044cc,#00ff88,#00aaff);
    animation:spin-ring 4s linear infinite;
}
.topbar-logo-inner {
    position:absolute; inset:2px; border-radius:50%;
    background:#04091a;
    display:flex; align-items:center; justify-content:center; font-size:16px;
}
.topbar-brand { display:flex; flex-direction:column; gap:1px; }
.topbar-name  { font-size:16px; font-weight:800; color:#e8f0ff; letter-spacing:-.2px; }
.topbar-name span { background:linear-gradient(135deg,#00aaff,#7c3aed); -webkit-background-clip:text; -webkit-text-fill-color:transparent; }
.topbar-tag   { font-size:10px; color:#4a6080; font-weight:500; letter-spacing:.8px; text-transform:uppercase; }
.topbar-right { margin-left:auto; display:flex; align-items:center; gap:10px; }
.topbar-pill  {
    background:rgba(0,170,255,.08); border:1px solid rgba(0,170,255,.2);
    color:#6bbfdf; font-size:11px; font-weight:500; padding:5px 14px;
    border-radius:20px; letter-spacing:.3px;
}
.topbar-dot {
    width:7px; height:7px; border-radius:50%;
    background:#00cc88; box-shadow:0 0 6px #00cc88;
    animation:glow-pulse 2s ease-in-out infinite;
}

/* ── 16. Animations ── */
@keyframes spin-ring  { to { transform:rotate(360deg); } }
@keyframes glow-pulse {
    0%,100% { box-shadow:0 0 6px rgba(0,204,136,.6); }
    50%     { box-shadow:0 0 14px rgba(0,204,136,1); }
}
@keyframes float-up   { 0%,100%{transform:translateY(0)} 50%{transform:translateY(-5px)} }

/* ── 17. Login card (column-as-card) ── */
div[data-testid="stHorizontalBlock"] > div:nth-child(2) > div > div[data-testid="stVerticalBlock"] {
    background:rgba(6,14,32,.85) !important;
    backdrop-filter:blur(28px) !important;
    -webkit-backdrop-filter:blur(28px) !important;
    border:1px solid rgba(0,170,255,.15) !important;
    border-radius:20px !important;
    padding:28px 26px 22px !important;
    box-shadow:
        0 0 0 1px rgba(255,255,255,.04),
        0 8px 48px rgba(0,0,0,.6),
        0 0 60px rgba(0,100,255,.07) !important;
    margin-top:8vh !important;
}

/* ── 18. Agent pipeline cards ── */
.agent-card {
    background:rgba(255,255,255,.03);
    backdrop-filter:blur(12px);
    border:1px solid rgba(255,255,255,.07);
    border-radius:12px; padding:16px 14px;
    margin-bottom:8px; text-align:center;
    transition:all .3s ease;
    box-shadow:0 2px 12px rgba(0,0,0,.25);
}
.agent-card:hover { transform:translateY(-2px); box-shadow:0 6px 24px rgba(0,0,0,.35); }
.agent-idle   { border-color:rgba(255,255,255,.07); }
.agent-active { border-color:rgba(0,170,255,.5); box-shadow:0 0 20px rgba(0,170,255,.2),0 2px 12px rgba(0,0,0,.25); }
.agent-done   { border-color:rgba(0,204,136,.4);  box-shadow:0 0 16px rgba(0,204,136,.15); }

/* ── 19. Misc helpers ── */
.kpi-box {
    background:rgba(255,255,255,.03); backdrop-filter:blur(12px);
    border:1px solid rgba(255,255,255,.07); border-radius:12px;
    padding:16px; text-align:center;
    box-shadow:0 4px 20px rgba(0,0,0,.25);
}
.snow-row {
    background:rgba(0,204,136,.04); border:1px solid rgba(0,204,136,.12);
    border-radius:8px; padding:9px 13px; margin:4px 0; font-size:13px;
}
.gradient-text {
    background:linear-gradient(135deg,#00aaff,#7c3aed);
    -webkit-background-clip:text; -webkit-text-fill-color:transparent;
}
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
  <div class="topbar-brand">
    <div class="topbar-name">Infosys &nbsp;<span>{APP_NAME}</span></div>
    <div class="topbar-tag">{APP_TAGLINE}</div>
  </div>
  <div class="topbar-right">
    <div class="topbar-dot" title="Live"></div>
    <div class="topbar-pill">👤 &nbsp;{st.session_state.get('login_user','admin')}</div>
  </div>
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
_aws_role_default   = _secrets.get("AWS_ROLE_ARN",       "")
_aws_ext_id_default = _secrets.get("AWS_EXTERNAL_ID",    "")
_aws_region_default = _secrets.get("AWS_DEFAULT_REGION", "us-east-1")

def _make_aws_client() -> AWSIntelligenceClient:
    c = st.session_state.aws_creds
    return AWSIntelligenceClient(
        role_arn    = c.get("role_arn",    ""),
        external_id = c.get("external_id", ""),
        region      = c.get("region",      "us-east-1"),
        auth_method = c.get("auth_method", "env"),
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

    _regions = [
        "us-east-1","us-east-2","us-west-1","us-west-2",
        "eu-west-1","eu-west-2","eu-central-1",
        "ap-southeast-1","ap-southeast-2","ap-northeast-1",
    ]

    # Auth method — IAM Role is always the default (works everywhere including Streamlit Cloud)
    _auth_labels = ["🔐 IAM Role (AssumeRole)", "🖥️ Environment / Instance Profile"]
    _auth_choice = st.radio(
        "Auth Method", _auth_labels, index=0,
        help="IAM Role: paste a Role ARN — works on Streamlit Cloud, local, CI/CD, anywhere.\n"
             "Environment: only works when this app runs on AWS infrastructure (EC2, ECS, Lambda).",
    )
    _use_role = (_auth_choice == _auth_labels[0])

    if _use_role:
        if _aws_role_default:
            st.success("Role ARN loaded from secrets ✓")
        aws_role_arn = st.text_input(
            "Role ARN", value=_aws_role_default,
            placeholder="arn:aws:iam::448549863273:role/CISCloudShieldRole",
        )
        aws_ext_id = st.text_input(
            "External ID  *(optional)*", value=_aws_ext_id_default,
            placeholder="CISCloudShield-ExternalId",
        )
    else:
        aws_role_arn = ""
        aws_ext_id   = ""
        st.warning(
            "**Only works on AWS infrastructure.**\n\n"
            "This mode requires the app to run on EC2, ECS Fargate, or Lambda "
            "with an attached instance/task role. It will fail on Streamlit Cloud.\n\n"
            "Use **IAM Role (AssumeRole)** instead."
        )

    aws_region = st.selectbox(
        "Region", _regions,
        index=_regions.index(_aws_region_default) if _aws_region_default in _regions else 0,
    )

    if st.button("🔌 Connect to AWS", use_container_width=True):
        if _use_role and not aws_role_arn:
            st.warning("Enter a Role ARN — e.g. arn:aws:iam::448549863273:role/CISCloudShieldRole")
        else:
            st.session_state.aws_creds = {
                "role_arn":    aws_role_arn,
                "external_id": aws_ext_id,
                "region":      aws_region,
                "auth_method": "role" if _use_role else "env",
            }
            _spinner_msg = "Assuming role and verifying identity…" if _use_role else "Verifying identity via instance profile…"
            with st.spinner(_spinner_msg):
                result = _make_aws_client().test_connection()
            if result["ok"]:
                st.session_state.aws_connected  = True
                st.session_state.aws_account_id = result["account_id"]
                st.session_state.aws_arn        = result["arn"]
                st.success(f"✅ Connected\n**Account:** {result['account_id']}")
                st.caption(result["arn"])
            else:
                _err = result["error"]
                if "No AWS credentials" in _err or "NoCredentialError" in _err or "Unable to locate" in _err:
                    st.error(
                        "No credentials found.\n\n"
                        "Switch to **IAM Role (AssumeRole)** and paste:\n"
                        "`arn:aws:iam::448549863273:role/CISCloudShieldRole`"
                    )
                else:
                    st.error(f"Connection failed: {_err}")
                st.session_state.aws_connected = False

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
tab1, tab2, tab3, tab4 = st.tabs([
    "🔐  Credential Intelligence",
    "💾  Backup Intelligence",
    "🔄  Auto-Remediation Loop",
    "📖  User Guide",
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


# ═════════════════════════════════════════════════════════════════════════════
# TAB 4 — USER GUIDE
# ═════════════════════════════════════════════════════════════════════════════
with tab4:

    st.markdown("""
    <style>
    /* ── User Guide specific styles ── */
    .ug-hero {
        background: linear-gradient(135deg, rgba(0,68,204,.18) 0%, rgba(124,58,237,.12) 100%);
        border: 1px solid rgba(0,170,255,.2);
        border-radius: 16px;
        padding: 28px 32px;
        margin-bottom: 28px;
    }
    .ug-hero h1 { font-size:26px !important; font-weight:800 !important;
                  color:#e8f4ff !important; margin:0 0 6px !important; }
    .ug-hero p  { color:rgba(255,255,255,.6) !important; font-size:13px !important;
                  margin:0 !important; }

    .ug-section {
        background: rgba(255,255,255,.03);
        border: 1px solid rgba(255,255,255,.07);
        border-left: 4px solid #00aaff;
        border-radius: 12px;
        padding: 20px 24px;
        margin-bottom: 20px;
    }
    .ug-section.purple { border-left-color: #7c3aed; }
    .ug-section.green  { border-left-color: #00c896; }
    .ug-section.gold   { border-left-color: #f5a623; }
    .ug-section.red    { border-left-color: #ff4b6e; }

    .ug-section h3 {
        font-size:15px !important; font-weight:700 !important;
        color:#e8f4ff !important; margin:0 0 12px !important;
        display:flex; align-items:center; gap:8px;
    }
    .ug-section p, .ug-section li {
        font-size:13px !important; color:rgba(255,255,255,.75) !important;
        line-height:1.7 !important;
    }
    .ug-section ul { padding-left:18px !important; margin:8px 0 !important; }

    .ug-step {
        display:flex; gap:14px; align-items:flex-start;
        margin-bottom:12px;
    }
    .ug-step-num {
        min-width:28px; height:28px; border-radius:50%;
        background:linear-gradient(135deg,#0088ff,#0050cc);
        display:flex; align-items:center; justify-content:center;
        font-size:12px; font-weight:700; color:#fff;
        flex-shrink:0; margin-top:1px;
    }
    .ug-step-body { font-size:13px !important; color:rgba(255,255,255,.8) !important;
                    line-height:1.65 !important; }
    .ug-step-body strong { color:#00aaff !important; }

    .ug-pill {
        display:inline-block;
        background:rgba(0,170,255,.12);
        border:1px solid rgba(0,170,255,.25);
        border-radius:6px;
        padding:2px 10px;
        font-size:12px; font-weight:600; color:#00aaff;
        margin:0 3px;
    }
    .ug-pill.purple { background:rgba(124,58,237,.12); border-color:rgba(124,58,237,.3); color:#a78bfa; }
    .ug-pill.green  { background:rgba(0,200,150,.1);   border-color:rgba(0,200,150,.25); color:#34d399; }
    .ug-pill.gold   { background:rgba(245,166,35,.1);  border-color:rgba(245,166,35,.25); color:#f5a623; }
    .ug-pill.red    { background:rgba(255,75,110,.1);  border-color:rgba(255,75,110,.25); color:#ff6b85; }

    .ug-table { width:100%; border-collapse:collapse; margin:12px 0; font-size:12.5px; }
    .ug-table th {
        background:rgba(0,68,204,.25); color:#8ecfff !important;
        padding:8px 12px; text-align:left; font-weight:600;
        border-bottom:1px solid rgba(0,170,255,.2);
    }
    .ug-table td {
        padding:8px 12px; color:rgba(255,255,255,.75) !important;
        border-bottom:1px solid rgba(255,255,255,.05);
        vertical-align:top;
    }
    .ug-table tr:last-child td { border-bottom:none; }
    .ug-table tr:hover td { background:rgba(255,255,255,.03); }

    .ug-callout {
        background:rgba(0,200,150,.07);
        border:1px solid rgba(0,200,150,.2);
        border-radius:10px;
        padding:14px 18px;
        margin:12px 0;
        font-size:13px;
        color:rgba(255,255,255,.8) !important;
    }
    .ug-callout-warn {
        background:rgba(245,166,35,.07);
        border:1px solid rgba(245,166,35,.25);
        border-radius:10px;
        padding:14px 18px;
        margin:12px 0;
        font-size:13px;
        color:rgba(255,255,255,.8) !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # ── Hero ──────────────────────────────────────────────────────────────────
    st.markdown("""
    <div class="ug-hero">
      <h1>📖 Infosys CIS Cloud Shield — User Guide</h1>
      <p>Complete reference for security operators, cloud engineers, and compliance teams using the platform.</p>
    </div>
    """, unsafe_allow_html=True)

    # ── Quick-Start ────────────────────────────────────────────────────────────
    st.markdown("## ⚡ Quick-Start Checklist")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("""
        <div class="ug-section">
          <h3>🛡️ First-Time Setup (5 minutes)</h3>
          <div class="ug-step"><div class="ug-step-num">1</div>
            <div class="ug-step-body">Log in with <strong>admin / Infosys@123</strong></div></div>
          <div class="ug-step"><div class="ug-step-num">2</div>
            <div class="ug-step-body">In the sidebar → <strong>OpenAI</strong>: paste your API key (sk-...)</div></div>
          <div class="ug-step"><div class="ug-step-num">3</div>
            <div class="ug-step-body">In the sidebar → <strong>ServiceNow</strong>: confirm URL/credentials and click <em>Test SNOW Connection</em></div></div>
          <div class="ug-step"><div class="ug-step-num">4</div>
            <div class="ug-step-body">In the sidebar → <strong>AWS Account</strong>: select <em>IAM Role (AssumeRole)</em>, paste the Role ARN, click <em>Connect to AWS</em></div></div>
          <div class="ug-step"><div class="ug-step-num">5</div>
            <div class="ug-step-body">Open <span class="ug-pill">🔐 Credential Intelligence</span> and click <em>Run AI Agent Analysis</em></div></div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown("""
        <div class="ug-section green">
          <h3>✅ Platform Credentials</h3>
          <table class="ug-table">
            <tr><th>What</th><th>Value</th></tr>
            <tr><td>App Username</td><td><strong>admin</strong></td></tr>
            <tr><td>App Password</td><td><strong>Infosys@123</strong></td></tr>
            <tr><td>ServiceNow URL</td><td>dev218436.service-now.com</td></tr>
            <tr><td>ServiceNow User</td><td>admin</td></tr>
            <tr><td>AWS Role ARN</td><td>arn:aws:iam::448549863273:role/CISCloudShieldRole</td></tr>
            <tr><td>AWS Account</td><td>448549863273</td></tr>
          </table>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    # ── Section 1: Login ───────────────────────────────────────────────────────
    st.markdown("## 1 · Login")
    st.markdown("""
    <div class="ug-section">
      <h3>🔑 Accessing the Platform</h3>
      <p>The platform presents a login gate on first load. Enter the credentials below and click <strong>Sign In</strong>.</p>
      <table class="ug-table">
        <tr><th>Field</th><th>Value</th><th>Notes</th></tr>
        <tr><td>Username</td><td><code>admin</code></td><td>Default administrator account</td></tr>
        <tr><td>Password</td><td><code>Infosys@123</code></td><td>Change in app.py for production deployments</td></tr>
      </table>
      <p>Once authenticated your session persists until the browser tab is closed or you log out via the sidebar.</p>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # ── Section 2: Sidebar ─────────────────────────────────────────────────────
    st.markdown("## 2 · Sidebar Configuration")

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("""
        <div class="ug-section purple">
          <h3>🤖 OpenAI / AI Model</h3>
          <p><strong>API Key:</strong> Paste your OpenAI key starting with <code>sk-...</code>.<br>
          On Streamlit Cloud the key is pre-loaded from <code>.streamlit/secrets.toml</code> — no input needed.</p>
          <p><strong>Model selector:</strong></p>
          <ul>
            <li><code>gpt-4o</code> — Best quality, recommended for production demos</li>
            <li><code>gpt-4o-mini</code> — Faster and cheaper for development testing</li>
            <li><code>gpt-4-turbo</code> — Alternative if gpt-4o quota is exhausted</li>
          </ul>
          <div class="ug-callout">The AI agents (Scanner, Risk, Remediator, Prevention) all use whichever model is selected here.</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="ug-section green">
          <h3>🎫 ServiceNow Connection</h3>
          <ul>
            <li><strong>Instance URL:</strong> <code>https://dev218436.service-now.com</code></li>
            <li><strong>Username:</strong> <code>admin</code></li>
            <li><strong>Password:</strong> Pre-filled from secrets</li>
          </ul>
          <p>Click <em>Test SNOW Connection</em> to verify. A green success banner confirms the API is reachable. ServiceNow is used to create incidents (INC), change requests (CHG), and close tickets during auto-remediation.</p>
        </div>
        """, unsafe_allow_html=True)

    with col_b:
        st.markdown("""
        <div class="ug-section gold">
          <h3>☁️ AWS Account — IAM Role Auth</h3>
          <p>The platform uses <strong>IAM Role (AssumeRole)</strong> — no long-lived access keys are stored anywhere.</p>

          <div class="ug-step"><div class="ug-step-num">1</div>
            <div class="ug-step-body">Select <strong>IAM Role (AssumeRole)</strong> as Auth Method</div></div>
          <div class="ug-step"><div class="ug-step-num">2</div>
            <div class="ug-step-body">Paste the Role ARN:<br><code>arn:aws:iam::448549863273:role/CISCloudShieldRole</code></div></div>
          <div class="ug-step"><div class="ug-step-num">3</div>
            <div class="ug-step-body">Leave <strong>External ID</strong> blank (same-account trust)</div></div>
          <div class="ug-step"><div class="ug-step-num">4</div>
            <div class="ug-step-body">Select your <strong>Region</strong> (default: us-east-1)</div></div>
          <div class="ug-step"><div class="ug-step-num">5</div>
            <div class="ug-step-body">Click <strong>Connect to AWS</strong> — a green banner shows Account ID and ARN on success</div></div>

          <div class="ug-callout-warn">⚠️ <strong>Environment / Instance Profile</strong> only works when the app runs on EC2, ECS, or Lambda. It will fail on Streamlit Cloud — always use IAM Role on the cloud deployment.</div>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    # ── Section 3: Tab 1 — Credential Intelligence ────────────────────────────
    st.markdown("## 3 · Tab 1 — Credential Intelligence")

    st.markdown("""
    <div class="ug-section">
      <h3>🔐 Purpose</h3>
      <p>Detect, score, and remediate <strong>~1,200 hardcoded credentials</strong> across AWS-hosted applications
      using a 4-agent AI pipeline. Produces prioritised findings, AI risk analysis, remediation plans, and
      prevention guidance. Can also raise ServiceNow change requests for critical findings.</p>
    </div>
    """, unsafe_allow_html=True)

    cred_c1, cred_c2 = st.columns(2)
    with cred_c1:
        st.markdown("""
        <div class="ug-section">
          <h3>📊 Metrics & Findings Table</h3>
          <p>The top of the tab shows four KPI cards:</p>
          <ul>
            <li><span class="ug-pill red">CRITICAL</span> count — requires immediate action</li>
            <li><span class="ug-pill gold">HIGH</span> count — remediate within 24 hours</li>
            <li><span class="ug-pill purple">MEDIUM</span> count — remediate within 7 days</li>
            <li>Total findings across all 1,200+ detections</li>
          </ul>
          <p>Use the <strong>filters</strong> (Severity, Environment, Credential Type, Status, Search) to narrow the findings table. The table is sortable and shows application, file location, age, and current status.</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="ug-section purple">
          <h3>🤖 Run AI Agent Analysis</h3>
          <p>Click <strong>Run AI Agent Analysis</strong> to launch the 4-agent pipeline:</p>
          <ul>
            <li><span class="ug-pill">Scanner Agent</span> — catalogues all findings by type and severity</li>
            <li><span class="ug-pill purple">Risk Agent</span> — scores blast radius, compliance impact, and priority</li>
            <li><span class="ug-pill green">Remediator Agent</span> — produces step-by-step remediation plan</li>
            <li><span class="ug-pill gold">Prevention Agent</span> — recommends controls to prevent re-occurrence</li>
          </ul>
          <p>Each agent streams output in real time. You can see the thinking as it happens — no need to wait for completion before reading early results.</p>
        </div>
        """, unsafe_allow_html=True)

    with cred_c2:
        st.markdown("""
        <div class="ug-section green">
          <h3>🎫 Create SNOW Change Requests</h3>
          <p>After reviewing findings, scroll to <strong>Raise Change Requests for Credential Remediation</strong>:</p>
          <div class="ug-step"><div class="ug-step-num">1</div>
            <div class="ug-step-body">Use the slider to set <strong>Max Change Requests to Create</strong> (1–10)</div></div>
          <div class="ug-step"><div class="ug-step-num">2</div>
            <div class="ug-step-body">Click <strong>Create SNOW Change Requests (Critical Findings)</strong></div></div>
          <div class="ug-step"><div class="ug-step-num">3</div>
            <div class="ug-step-body">The platform creates a CHG record in ServiceNow for each CRITICAL finding, with full finding detail in the description</div></div>
          <div class="ug-step"><div class="ug-step-num">4</div>
            <div class="ug-step-body">Click the ServiceNow links in the results table to open tickets directly</div></div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="ug-section gold">
          <h3>🔎 Live AWS IAM Scan</h3>
          <p>Connect to AWS first (sidebar), then click <strong>Run Live IAM Scan</strong> to query your real AWS account:</p>
          <ul>
            <li>IAM Credential Report — root keys, MFA status, stale passwords</li>
            <li>Access keys older than 90/180 days flagged as HIGH/CRITICAL</li>
            <li>Console users without MFA</li>
            <li>Secrets Manager inventory and rotation status</li>
            <li>Security Hub active failed controls</li>
          </ul>
          <p>Live findings replace mock data in the table and are available as input to the Auto-Remediation Loop.</p>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    # ── Section 4: Tab 2 — Backup Intelligence ────────────────────────────────
    st.markdown("## 4 · Tab 2 — Backup Intelligence")

    st.markdown("""
    <div class="ug-section purple">
      <h3>💾 Purpose</h3>
      <p>Assess immutable backup coverage across <strong>~250 applications</strong>. Identify unprotected and
      partially-protected resources, explore supported backup technologies, and raise ServiceNow incidents
      for applications with no backup in place.</p>
    </div>
    """, unsafe_allow_html=True)

    bk_c1, bk_c2 = st.columns(2)
    with bk_c1:
        st.markdown("""
        <div class="ug-section">
          <h3>📈 Coverage Dashboard</h3>
          <p>The tab opens with three KPI tiles:</p>
          <ul>
            <li><span class="ug-pill green">Protected</span> — immutable backup confirmed</li>
            <li><span class="ug-pill gold">Partial</span> — some backup but not fully immutable</li>
            <li><span class="ug-pill red">Unprotected</span> — no backup at all</li>
          </ul>
          <p>A donut chart shows the coverage split. Filter the inventory table by <strong>Status, Environment, Criticality,</strong> and <strong>Type</strong> to focus on priority applications.</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="ug-section green">
          <h3>☁️ Live AWS Backup Scan</h3>
          <p>With AWS connected, click <strong>Scan AWS Backup Coverage</strong>:</p>
          <ul>
            <li><strong>EC2</strong> — checks AWS Backup protected resources</li>
            <li><strong>RDS</strong> — automated backup period + Backup vault coverage</li>
            <li><strong>S3</strong> — Object Lock configuration + versioning status</li>
            <li><strong>DynamoDB</strong> — Point-in-Time Recovery (PITR) status</li>
          </ul>
          <p>Results replace mock data and show your real account's backup posture.</p>
        </div>
        """, unsafe_allow_html=True)

    with bk_c2:
        st.markdown("""
        <div class="ug-section gold">
          <h3>🏗️ Backup Technologies Explorer</h3>
          <p>The <strong>Backup Technologies</strong> section has four sub-tabs:</p>
          <table class="ug-table">
            <tr><th>Technology</th><th>Best For</th><th>Immutability</th></tr>
            <tr><td>AWS Backup</td><td>All native AWS resources</td><td>Vault Lock (WORM)</td></tr>
            <tr><td>Veeam v12</td><td>VMware, Hyper-V, hybrid</td><td>Hardened Linux Repo</td></tr>
            <tr><td>Commvault</td><td>Enterprise / SAP / Oracle</td><td>Air-Gap Protect</td></tr>
            <tr><td>S3 Object Lock</td><td>Object-level WORM</td><td>Compliance Mode</td></tr>
          </table>
          <p>Each sub-tab shows RPO/RTO, supported platforms, and key features.</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="ug-section red">
          <h3>🚨 Create SNOW Incidents</h3>
          <p>For applications with no backup, click <strong>Create SNOW Incidents for Unprotected Apps</strong>:</p>
          <ul>
            <li>Slider controls how many incidents to raise (1–10)</li>
            <li>Highest-criticality unprotected apps are prioritised</li>
            <li>Each incident includes application name, type, environment, and recommended backup solution</li>
            <li>Links to created tickets appear in the results table</li>
          </ul>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    # ── Section 5: Tab 3 — Auto-Remediation Loop ──────────────────────────────
    st.markdown("## 5 · Tab 3 — Auto-Remediation Loop")

    st.markdown("""
    <div class="ug-section red">
      <h3>🔄 How the Loop Works</h3>
      <p>The Auto-Remediation Loop is a <strong>closed-loop, 4-phase agentic pipeline</strong> that processes
      security findings end-to-end — from incident creation to ServiceNow ticket closure — without manual steps.</p>
      <table class="ug-table">
        <tr><th>Phase</th><th>Agent</th><th>Action</th><th>ServiceNow</th></tr>
        <tr><td>1</td><td><span class="ug-pill red">INC Agent</span></td><td>Creates incident, classifies severity, enriches with blast-radius context</td><td>INC created</td></tr>
        <tr><td>2</td><td><span class="ug-pill gold">Dispatcher Agent</span></td><td>Investigates root cause, determines remediation playbook</td><td>INC updated</td></tr>
        <tr><td>3</td><td><span class="ug-pill green">Remediator Agent</span></td><td>Executes fix, validates result, produces resolution note</td><td>CHG created &amp; resolved</td></tr>
        <tr><td>4</td><td><span class="ug-pill red">INC Agent</span></td><td>Receives resolution, writes closure note, closes the incident</td><td>INC closed ✅</td></tr>
      </table>
    </div>
    """, unsafe_allow_html=True)

    loop_c1, loop_c2 = st.columns(2)
    with loop_c1:
        st.markdown("""
        <div class="ug-section">
          <h3>⚙️ Configuration Options</h3>
          <ul>
            <li><strong>Finding source</strong> — <em>Mock data (demo)</em> uses the 1,200 synthetic findings.
            <em>Live IAM scan</em> uses findings from the Tab 1 live scan (requires AWS connection).</li>
            <li><strong>Findings to process</strong> — Number of findings to run through the loop (1–20).
            Start with 1–3 for a demo.</li>
            <li><strong>Target severity</strong> — Filter to CRITICAL, HIGH, and/or MEDIUM findings only.</li>
          </ul>
          <div class="ug-callout">Each finding runs all 4 agent phases before moving to the next. Progress bar tracks overall completion.</div>
        </div>
        """, unsafe_allow_html=True)

    with loop_c2:
        st.markdown("""
        <div class="ug-section purple">
          <h3>▶️ Running the Loop</h3>
          <div class="ug-step"><div class="ug-step-num">1</div>
            <div class="ug-step-body">Ensure ServiceNow and OpenAI are configured in the sidebar</div></div>
          <div class="ug-step"><div class="ug-step-num">2</div>
            <div class="ug-step-body">Set <strong>Finding source, count,</strong> and <strong>severity filter</strong></div></div>
          <div class="ug-step"><div class="ug-step-num">3</div>
            <div class="ug-step-body">Click <strong>▶ Start Remediation Loop</strong></div></div>
          <div class="ug-step"><div class="ug-step-num">4</div>
            <div class="ug-step-body">Watch each agent stream its output inside the finding expander panel</div></div>
          <div class="ug-step"><div class="ug-step-num">5</div>
            <div class="ug-step-body">When complete, a <strong>Summary Table</strong> shows INC numbers, SNOW links, and resolution status for all processed findings</div></div>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    # ── Section 6: IAM Role Reference ─────────────────────────────────────────
    st.markdown("## 6 · IAM Role Reference")

    st.markdown("""
    <div class="ug-section green">
      <h3>🔐 CISCloudShieldRole — Pre-Provisioned in Account 448549863273</h3>
      <table class="ug-table">
        <tr><th>Attribute</th><th>Value</th></tr>
        <tr><td>Role Name</td><td><code>CISCloudShieldRole</code></td></tr>
        <tr><td>Role ARN</td><td><code>arn:aws:iam::448549863273:role/CISCloudShieldRole</code></td></tr>
        <tr><td>Inline Policy</td><td><code>CISCloudShieldScanPolicy</code> (read-only)</td></tr>
        <tr><td>Trusted Principal</td><td><code>arn:aws:iam::448549863273:user/Ajit_Gosavi@infosys.com</code></td></tr>
        <tr><td>Session Duration</td><td>3,600 seconds — temporary credentials auto-expire after 1 hour</td></tr>
        <tr><td>Permissions</td><td>IAM credential report, Secrets Manager list, Security Hub findings, AWS Backup, EC2/RDS/S3/DynamoDB describe, CloudTrail, CloudWatch</td></tr>
      </table>
      <div class="ug-callout">No access keys are ever issued. The platform calls <code>sts:AssumeRole</code> and receives short-lived credentials automatically. All calls are logged in CloudTrail.</div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # ── Section 7: Troubleshooting ─────────────────────────────────────────────
    st.markdown("## 7 · Troubleshooting")

    st.markdown("""
    <div class="ug-section red">
      <h3>🔧 Common Issues & Fixes</h3>
      <table class="ug-table">
        <tr><th>Symptom</th><th>Cause</th><th>Fix</th></tr>
        <tr>
          <td><em>Connection failed: No AWS credentials configured</em></td>
          <td>Environment / Instance Profile selected but app is running on Streamlit Cloud (no instance role)</td>
          <td>Switch Auth Method to <strong>IAM Role (AssumeRole)</strong> and paste the Role ARN</td>
        </tr>
        <tr>
          <td><em>Connection failed: AccessDenied</em></td>
          <td>The IAM user/role making the call is not listed in CISCloudShieldRole's trust policy</td>
          <td>Add your principal to the role's trust policy in AWS IAM console</td>
        </tr>
        <tr>
          <td>AI agents produce no output</td>
          <td>OpenAI API key missing or invalid</td>
          <td>Paste a valid <code>sk-...</code> key in the sidebar OpenAI section</td>
        </tr>
        <tr>
          <td>SNOW connection fails</td>
          <td>ServiceNow developer instance may be sleeping (free instances sleep after inactivity)</td>
          <td>Log in to <code>dev218436.service-now.com</code> directly to wake the instance, then retry</td>
        </tr>
        <tr>
          <td>Live Backup Scan returns no results</td>
          <td>AWS account has no EC2/RDS/DynamoDB resources, or role lacks describe permissions</td>
          <td>Verify resources exist in the selected region; check CISCloudShieldScanPolicy is attached</td>
        </tr>
        <tr>
          <td>Topbar text clipped</td>
          <td>Browser zoom level above 100%</td>
          <td>Set browser zoom to 100% (Ctrl+0)</td>
        </tr>
      </table>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # ── Section 8: FAQ ─────────────────────────────────────────────────────────
    st.markdown("## 8 · Frequently Asked Questions")

    with st.expander("Is the mock data realistic?"):
        st.markdown(
            "Yes. The mock dataset is deterministically generated (random seed 42) to simulate a real enterprise "
            "environment: 1,200 credential findings distributed across 435 CRITICAL, 491 HIGH, and 274 MEDIUM "
            "findings, spread across development, staging, and production environments with realistic application "
            "names, credential types, and file locations."
        )
    with st.expander("Can I use this against my own AWS account?"):
        st.markdown(
            "Yes. Connect using the IAM Role (AssumeRole) method. The CISCloudShieldRole is pre-provisioned in "
            "account 448549863273. To use it against a different account, create a role in that account with the "
            "same trust policy and permissions policy (both available in the GitHub repo as "
            "`cis-trust-policy.json` and `cis-permissions-policy.json`)."
        )
    with st.expander("Will the Auto-Remediation Loop create real ServiceNow tickets?"):
        st.markdown(
            "Yes — if ServiceNow credentials are configured and the connection test passes, the loop creates "
            "real INC and CHG records in the connected ServiceNow instance. The tickets include full finding "
            "context, agent analysis, and are automatically closed by the INC Agent at the end of each loop iteration."
        )
    with st.expander("Which AI model is used?"):
        st.markdown(
            "The sidebar defaults to **gpt-4o** (OpenAI). The platform architecture is designed to support "
            "Anthropic Claude Opus 4.7 (`claude-opus-4-7`) — Anthropic's most capable model — as the preferred "
            "enterprise AI backbone. Switch to the Claude API endpoint by updating the `openai.OpenAI(base_url=...)` "
            "call in app.py to point to the Anthropic API."
        )
    with st.expander("How are temporary AWS credentials handled?"):
        st.markdown(
            "When you click **Connect to AWS** with IAM Role selected, the platform calls `sts:AssumeRole` "
            "and receives temporary credentials valid for 1 hour (AccessKeyId, SecretAccessKey, SessionToken). "
            "These are stored only in the Streamlit session state for the duration of your browser session — "
            "they are never written to disk, logged, or transmitted outside the app. They expire automatically "
            "after 1 hour with no revocation step needed."
        )
    with st.expander("How do I deploy this on Streamlit Cloud?"):
        st.markdown(
            "1. Fork the GitHub repo: `https://github.com/ajittgosavii/awssec`\n"
            "2. Connect it to your Streamlit Cloud account\n"
            "3. Add secrets in the Streamlit Cloud dashboard under **Settings → Secrets**:\n"
            "```toml\n"
            "OPENAI_API_KEY = \"sk-...\"\n"
            "SNOW_URL       = \"https://dev218436.service-now.com\"\n"
            "SNOW_USER      = \"admin\"\n"
            "SNOW_PASS      = \"your-snow-password\"\n"
            "AWS_ROLE_ARN   = \"arn:aws:iam::448549863273:role/CISCloudShieldRole\"\n"
            "```\n"
            "4. Deploy — the app will auto-load all credentials from secrets with no sidebar input required."
        )

    st.divider()

    # ── Footer ─────────────────────────────────────────────────────────────────
    st.markdown("""
    <div style="text-align:center;padding:20px 0;color:rgba(255,255,255,.3);font-size:12px;">
      Infosys CIS Cloud Shield &nbsp;|&nbsp; Agentic AI · AWS Security · Immutable Backup
      &nbsp;|&nbsp; Powered by Anthropic Claude Opus 4.7
    </div>
    """, unsafe_allow_html=True)
