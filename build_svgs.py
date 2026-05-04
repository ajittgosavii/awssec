"""Generate HLD, LLD, and End-User Flow SVG diagrams for CIS Cloud Shield."""

# ═══════════════════════════════════════════════════════════════════════════════
# HLD — High Level Design
# ═══════════════════════════════════════════════════════════════════════════════
HLD_SVG = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1100 720" width="1100" height="720" font-family="Segoe UI,Arial,sans-serif">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#04091a"/>
      <stop offset="100%" stop-color="#020610"/>
    </linearGradient>
    <linearGradient id="hdr" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#003D9C"/>
      <stop offset="100%" stop-color="#0066cc"/>
    </linearGradient>
    <linearGradient id="blue_box" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#001a4d" stop-opacity="0.9"/>
      <stop offset="100%" stop-color="#000d33" stop-opacity="0.9"/>
    </linearGradient>
    <filter id="glow">
      <feGaussianBlur stdDeviation="3" result="blur"/>
      <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <marker id="arr" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto">
      <path d="M0,0 L0,6 L8,3 z" fill="#00aaff"/>
    </marker>
    <marker id="arr_g" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto">
      <path d="M0,0 L0,6 L8,3 z" fill="#00c896"/>
    </marker>
  </defs>

  <!-- Background -->
  <rect width="1100" height="720" fill="url(#bg)"/>

  <!-- Header bar -->
  <rect x="0" y="0" width="1100" height="56" fill="url(#hdr)"/>
  <circle cx="28" cy="28" r="16" fill="none" stroke="#00aaff" stroke-width="2.5"/>
  <text x="28" y="33" text-anchor="middle" font-size="16" fill="white">🛡</text>
  <text x="56" y="22" font-size="18" font-weight="700" fill="white">Infosys CIS Cloud Shield</text>
  <text x="56" y="40" font-size="11" fill="rgba(255,255,255,0.6)">High Level Design (HLD) — Agentic AI Security &amp; Immutable Backup Platform</text>
  <text x="1085" y="33" text-anchor="end" font-size="10" fill="rgba(255,255,255,0.4)">v1.0 · 2026</text>

  <!-- ── LAYER 1: User / Browser ── -->
  <rect x="20" y="76" width="180" height="100" rx="10" fill="url(#blue_box)" stroke="#00aaff" stroke-width="1"/>
  <text x="110" y="100" text-anchor="middle" font-size="12" font-weight="700" fill="#00aaff">👤 Security Operator</text>
  <text x="110" y="118" text-anchor="middle" font-size="10" fill="rgba(255,255,255,0.6)">Browser / Streamlit Cloud</text>
  <text x="110" y="134" text-anchor="middle" font-size="10" fill="rgba(255,255,255,0.5)">Glass UI · Login Gate</text>
  <text x="110" y="150" text-anchor="middle" font-size="10" fill="rgba(255,255,255,0.5)">admin / Infosys@123</text>

  <!-- ── LAYER 2: Platform Core ── -->
  <rect x="240" y="68" width="620" height="290" rx="12" fill="rgba(0,60,120,0.12)" stroke="rgba(0,170,255,0.25)" stroke-width="1.5" stroke-dasharray="6,3"/>
  <text x="550" y="90" text-anchor="middle" font-size="11" font-weight="700" fill="rgba(0,170,255,0.7)" letter-spacing="2">INFOSYS CIS CLOUD SHIELD — APPLICATION LAYER</text>

  <!-- Tab 1 -->
  <rect x="258" y="100" width="170" height="108" rx="8" fill="url(#blue_box)" stroke="#0066ff" stroke-width="1"/>
  <text x="343" y="120" text-anchor="middle" font-size="11" font-weight="700" fill="#8ecfff">🔐 Credential</text>
  <text x="343" y="134" text-anchor="middle" font-size="11" font-weight="700" fill="#8ecfff">Intelligence</text>
  <text x="343" y="152" text-anchor="middle" font-size="9.5" fill="rgba(255,255,255,0.55)">Scanner · Risk · Remediator</text>
  <text x="343" y="166" text-anchor="middle" font-size="9.5" fill="rgba(255,255,255,0.55)">Prevention Agents (×4)</text>
  <text x="343" y="182" text-anchor="middle" font-size="9.5" fill="rgba(255,255,255,0.55)">1,200 Finding Dataset</text>
  <text x="343" y="196" text-anchor="middle" font-size="9.5" fill="rgba(255,255,255,0.55)">SNOW CHG Integration</text>

  <!-- Tab 2 -->
  <rect x="463" y="100" width="170" height="108" rx="8" fill="url(#blue_box)" stroke="#7c3aed" stroke-width="1"/>
  <text x="548" y="120" text-anchor="middle" font-size="11" font-weight="700" fill="#c4b5fd">💾 Backup</text>
  <text x="548" y="134" text-anchor="middle" font-size="11" font-weight="700" fill="#c4b5fd">Intelligence</text>
  <text x="548" y="152" text-anchor="middle" font-size="9.5" fill="rgba(255,255,255,0.55)">250 App Coverage Map</text>
  <text x="548" y="166" text-anchor="middle" font-size="9.5" fill="rgba(255,255,255,0.55)">AWS Backup · Veeam</text>
  <text x="548" y="182" text-anchor="middle" font-size="9.5" fill="rgba(255,255,255,0.55)">Commvault · S3 Lock</text>
  <text x="548" y="196" text-anchor="middle" font-size="9.5" fill="rgba(255,255,255,0.55)">SNOW INC Integration</text>

  <!-- Tab 3 -->
  <rect x="668" y="100" width="170" height="108" rx="8" fill="url(#blue_box)" stroke="#00c896" stroke-width="1"/>
  <text x="753" y="120" text-anchor="middle" font-size="11" font-weight="700" fill="#6ee7b7">🔄 Auto-Remediation</text>
  <text x="753" y="134" text-anchor="middle" font-size="11" font-weight="700" fill="#6ee7b7">Loop</text>
  <text x="753" y="152" text-anchor="middle" font-size="9.5" fill="rgba(255,255,255,0.55)">INC → Dispatcher</text>
  <text x="753" y="166" text-anchor="middle" font-size="9.5" fill="rgba(255,255,255,0.55)">→ Remediator → Close</text>
  <text x="753" y="182" text-anchor="middle" font-size="9.5" fill="rgba(255,255,255,0.55)">Closed-Loop Agentic</text>
  <text x="753" y="196" text-anchor="middle" font-size="9.5" fill="rgba(255,255,255,0.55)">SNOW Full Lifecycle</text>

  <!-- AI Engine bar -->
  <rect x="258" y="224" width="580" height="50" rx="8" fill="rgba(124,58,237,0.18)" stroke="rgba(124,58,237,0.5)" stroke-width="1"/>
  <text x="548" y="244" text-anchor="middle" font-size="11" font-weight="700" fill="#c4b5fd">🤖 AI Orchestration — Anthropic Claude Opus 4.7 (claude-opus-4-7)</text>
  <text x="548" y="262" text-anchor="middle" font-size="9.5" fill="rgba(255,255,255,0.55)">Streaming agents · Tool use · Extended context · Constitutional AI safety · 99.9% SLA</text>

  <!-- STS Auth bar -->
  <rect x="258" y="288" width="580" height="50" rx="8" fill="rgba(0,200,100,0.1)" stroke="rgba(0,200,100,0.35)" stroke-width="1"/>
  <text x="548" y="308" text-anchor="middle" font-size="11" font-weight="700" fill="#6ee7b7">🔐 AWS Authentication — STS AssumeRole (No Long-Lived Keys)</text>
  <text x="548" y="326" text-anchor="middle" font-size="9.5" fill="rgba(255,255,255,0.55)">CISCloudShieldBootstrap → sts:AssumeRole → CISCloudShieldRole → 1-hour temp credentials</text>

  <!-- ── LAYER 3: External Systems ── -->
  <!-- AWS -->
  <rect x="20" y="400" width="200" height="190" rx="10" fill="url(#blue_box)" stroke="#f5a623" stroke-width="1.5"/>
  <text x="120" y="422" text-anchor="middle" font-size="12" font-weight="700" fill="#f5a623">☁️ AWS Account</text>
  <text x="120" y="438" text-anchor="middle" font-size="9" fill="rgba(255,255,255,0.45)">448549863273</text>
  <line x1="40" y1="446" x2="200" y2="446" stroke="rgba(245,166,35,0.2)" stroke-width="1"/>
  <text x="120" y="462" text-anchor="middle" font-size="9.5" fill="rgba(255,255,255,0.6)">IAM · Credential Report</text>
  <text x="120" y="478" text-anchor="middle" font-size="9.5" fill="rgba(255,255,255,0.6)">Secrets Manager</text>
  <text x="120" y="494" text-anchor="middle" font-size="9.5" fill="rgba(255,255,255,0.6)">Security Hub</text>
  <text x="120" y="510" text-anchor="middle" font-size="9.5" fill="rgba(255,255,255,0.6)">AWS Backup + Vault Lock</text>
  <text x="120" y="526" text-anchor="middle" font-size="9.5" fill="rgba(255,255,255,0.6)">EC2 · RDS · S3 · DynamoDB</text>
  <text x="120" y="542" text-anchor="middle" font-size="9.5" fill="rgba(255,255,255,0.6)">CloudTrail · CloudWatch</text>
  <text x="120" y="558" text-anchor="middle" font-size="9.5" fill="rgba(255,255,255,0.6)">STS AssumeRole</text>
  <text x="120" y="574" text-anchor="middle" font-size="9" fill="#f5a623">CISCloudShieldRole (read-only)</text>

  <!-- ServiceNow -->
  <rect x="260" y="400" width="200" height="190" rx="10" fill="url(#blue_box)" stroke="#00aaff" stroke-width="1.5"/>
  <text x="360" y="422" text-anchor="middle" font-size="12" font-weight="700" fill="#00aaff">🎫 ServiceNow</text>
  <text x="360" y="438" text-anchor="middle" font-size="9" fill="rgba(255,255,255,0.45)">dev218436.service-now.com</text>
  <line x1="280" y1="446" x2="440" y2="446" stroke="rgba(0,170,255,0.2)" stroke-width="1"/>
  <text x="360" y="462" text-anchor="middle" font-size="9.5" fill="rgba(255,255,255,0.6)">Incident Management (INC)</text>
  <text x="360" y="478" text-anchor="middle" font-size="9.5" fill="rgba(255,255,255,0.6)">Change Requests (CHG)</text>
  <text x="360" y="494" text-anchor="middle" font-size="9.5" fill="rgba(255,255,255,0.6)">Auto-assignment to users</text>
  <text x="360" y="510" text-anchor="middle" font-size="9.5" fill="rgba(255,255,255,0.6)">10 real engineer profiles</text>
  <text x="360" y="526" text-anchor="middle" font-size="9.5" fill="rgba(255,255,255,0.6)">Lifecycle: Open → Closed</text>
  <text x="360" y="542" text-anchor="middle" font-size="9.5" fill="rgba(255,255,255,0.6)">Table REST API</text>
  <text x="360" y="558" text-anchor="middle" font-size="9.5" fill="rgba(255,255,255,0.6)">PATCH · POST · GET</text>

  <!-- OpenAI -->
  <rect x="500" y="400" width="200" height="190" rx="10" fill="url(#blue_box)" stroke="#7c3aed" stroke-width="1.5"/>
  <text x="600" y="422" text-anchor="middle" font-size="12" font-weight="700" fill="#c4b5fd">🤖 AI API</text>
  <text x="600" y="438" text-anchor="middle" font-size="9" fill="rgba(255,255,255,0.45)">Anthropic / OpenAI</text>
  <line x1="520" y1="446" x2="680" y2="446" stroke="rgba(124,58,237,0.2)" stroke-width="1"/>
  <text x="600" y="462" text-anchor="middle" font-size="9.5" fill="rgba(255,255,255,0.6)">claude-opus-4-7</text>
  <text x="600" y="478" text-anchor="middle" font-size="9.5" fill="rgba(255,255,255,0.6)">gpt-4o / gpt-4o-mini</text>
  <text x="600" y="494" text-anchor="middle" font-size="9.5" fill="rgba(255,255,255,0.6)">Streaming completions</text>
  <text x="600" y="510" text-anchor="middle" font-size="9.5" fill="rgba(255,255,255,0.6)">Tool use / function calls</text>
  <text x="600" y="526" text-anchor="middle" font-size="9.5" fill="rgba(255,255,255,0.6)">200K context window</text>
  <text x="600" y="542" text-anchor="middle" font-size="9.5" fill="rgba(255,255,255,0.6)">Constitutional AI safety</text>

  <!-- GitHub -->
  <rect x="740" y="400" width="200" height="190" rx="10" fill="url(#blue_box)" stroke="#00c896" stroke-width="1.5"/>
  <text x="840" y="422" text-anchor="middle" font-size="12" font-weight="700" fill="#6ee7b7">⚙️ Deployment</text>
  <text x="840" y="438" text-anchor="middle" font-size="9" fill="rgba(255,255,255,0.45)">GitHub + Streamlit Cloud</text>
  <line x1="760" y1="446" x2="920" y2="446" stroke="rgba(0,200,150,0.2)" stroke-width="1"/>
  <text x="840" y="462" text-anchor="middle" font-size="9.5" fill="rgba(255,255,255,0.6)">github.com/ajittgosavii/awssec</text>
  <text x="840" y="478" text-anchor="middle" font-size="9.5" fill="rgba(255,255,255,0.6)">Streamlit Cloud (auto-deploy)</text>
  <text x="840" y="494" text-anchor="middle" font-size="9.5" fill="rgba(255,255,255,0.6)">Secrets: Role ARN + Bootstrap</text>
  <text x="840" y="510" text-anchor="middle" font-size="9.5" fill="rgba(255,255,255,0.6)">Dark theme config.toml</text>
  <text x="840" y="526" text-anchor="middle" font-size="9.5" fill="rgba(255,255,255,0.6)">Python 3.11 · boto3 · openai</text>
  <text x="840" y="542" text-anchor="middle" font-size="9.5" fill="rgba(255,255,255,0.6)">pandas · plotly · requests</text>

  <!-- Arrows: User → Platform -->
  <line x1="200" y1="126" x2="252" y2="160" stroke="#00aaff" stroke-width="1.5" marker-end="url(#arr)"/>

  <!-- Arrows: Platform → External -->
  <line x1="343" y1="356" x2="120" y2="400" stroke="#f5a623" stroke-width="1.5" stroke-dasharray="5,3" marker-end="url(#arr)"/>
  <line x1="430" y1="356" x2="360" y2="400" stroke="#00aaff" stroke-width="1.5" stroke-dasharray="5,3" marker-end="url(#arr)"/>
  <line x1="548" y1="356" x2="600" y2="400" stroke="#7c3aed" stroke-width="1.5" stroke-dasharray="5,3" marker-end="url(#arr)"/>
  <line x1="753" y1="356" x2="840" y2="400" stroke="#00c896" stroke-width="1.5" stroke-dasharray="5,3" marker-end="url(#arr)"/>

  <!-- Label arrows -->
  <text x="220" y="390" font-size="9" fill="#f5a623" transform="rotate(-30,220,390)">boto3 / STS</text>
  <text x="385" y="385" font-size="9" fill="#00aaff">REST API</text>
  <text x="548" y="385" font-size="9" fill="#7c3aed">HTTPS / SSE</text>
  <text x="740" y="385" font-size="9" fill="#00c896">git push</text>

  <!-- Footer -->
  <rect x="0" y="698" width="1100" height="22" fill="rgba(0,61,156,0.4)"/>
  <text x="550" y="713" text-anchor="middle" font-size="9" fill="rgba(255,255,255,0.4)">Infosys Limited · CIS Cloud Shield · HLD · Confidential · v1.0 · 2026</text>
</svg>'''


# ═══════════════════════════════════════════════════════════════════════════════
# LLD — Low Level Design
# ═══════════════════════════════════════════════════════════════════════════════
LLD_SVG = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 800" width="1200" height="800" font-family="Segoe UI,Arial,sans-serif">
  <defs>
    <linearGradient id="bg2" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#04091a"/><stop offset="100%" stop-color="#020610"/>
    </linearGradient>
    <linearGradient id="hdr2" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#003D9C"/><stop offset="100%" stop-color="#7c3aed"/>
    </linearGradient>
    <marker id="a1" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto">
      <path d="M0,0 L0,6 L8,3 z" fill="#00aaff"/>
    </marker>
    <marker id="a2" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto">
      <path d="M0,0 L0,6 L8,3 z" fill="#00c896"/>
    </marker>
    <marker id="a3" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto">
      <path d="M0,0 L0,6 L8,3 z" fill="#f5a623"/>
    </marker>
  </defs>

  <rect width="1200" height="800" fill="url(#bg2)"/>
  <rect x="0" y="0" width="1200" height="54" fill="url(#hdr2)"/>
  <text x="20" y="22" font-size="17" font-weight="700" fill="white">Infosys CIS Cloud Shield — Low Level Design (LLD)</text>
  <text x="20" y="42" font-size="10" fill="rgba(255,255,255,0.6)">Component interactions, data flows, API contracts, and IAM authentication chain</text>
  <text x="1185" y="32" text-anchor="end" font-size="9" fill="rgba(255,255,255,0.35)">v1.0 · 2026</text>

  <!-- ── COLUMN 1: Frontend ── -->
  <rect x="16" y="66" width="190" height="680" rx="10" fill="rgba(0,40,100,0.15)" stroke="rgba(0,170,255,0.2)" stroke-width="1"/>
  <rect x="16" y="66" width="190" height="28" rx="10" fill="rgba(0,100,200,0.3)"/>
  <text x="111" y="85" text-anchor="middle" font-size="11" font-weight="700" fill="#8ecfff">FRONTEND</text>

  <!-- Boxes inside Frontend -->
  <rect x="26" y="104" width="170" height="52" rx="6" fill="rgba(0,60,140,0.4)" stroke="rgba(0,170,255,0.3)" stroke-width="1"/>
  <text x="111" y="122" text-anchor="middle" font-size="10" font-weight="600" fill="#8ecfff">Streamlit App (app.py)</text>
  <text x="111" y="138" text-anchor="middle" font-size="8.5" fill="rgba(255,255,255,0.5)">st.tabs · session_state · st.secrets</text>
  <text x="111" y="150" text-anchor="middle" font-size="8.5" fill="rgba(255,255,255,0.5)">st.set_page_config · layout=wide</text>

  <rect x="26" y="166" width="170" height="44" rx="6" fill="rgba(0,60,140,0.3)" stroke="rgba(0,170,255,0.2)" stroke-width="1"/>
  <text x="111" y="183" text-anchor="middle" font-size="10" font-weight="600" fill="#8ecfff">Login Gate</text>
  <text x="111" y="197" text-anchor="middle" font-size="8.5" fill="rgba(255,255,255,0.5)">st.session_state.authenticated</text>
  <text x="111" y="209" text-anchor="middle" font-size="8.5" fill="rgba(255,255,255,0.5)">admin / Infosys@123</text>

  <rect x="26" y="220" width="170" height="44" rx="6" fill="rgba(0,60,140,0.3)" stroke="rgba(0,170,255,0.2)" stroke-width="1"/>
  <text x="111" y="237" text-anchor="middle" font-size="10" font-weight="600" fill="#8ecfff">CSS Glass Theme</text>
  <text x="111" y="251" text-anchor="middle" font-size="8.5" fill="rgba(255,255,255,0.5)">backdrop-filter · conic-gradient</text>
  <text x="111" y="263" text-anchor="middle" font-size="8.5" fill="rgba(255,255,255,0.5)">Inter font · topbar HTML</text>

  <rect x="26" y="274" width="170" height="44" rx="6" fill="rgba(0,60,140,0.3)" stroke="rgba(0,170,255,0.2)" stroke-width="1"/>
  <text x="111" y="291" text-anchor="middle" font-size="10" font-weight="600" fill="#8ecfff">Mock Data (mock_data.py)</text>
  <text x="111" y="305" text-anchor="middle" font-size="8.5" fill="rgba(255,255,255,0.5)">1,200 findings · 250 apps</text>
  <text x="111" y="317" text-anchor="middle" font-size="8.5" fill="rgba(255,255,255,0.5)">seed=42 · deterministic</text>

  <rect x="26" y="328" width="170" height="44" rx="6" fill="rgba(0,60,140,0.3)" stroke="rgba(0,170,255,0.2)" stroke-width="1"/>
  <text x="111" y="345" text-anchor="middle" font-size="10" font-weight="600" fill="#8ecfff">Plotly Charts</text>
  <text x="111" y="359" text-anchor="middle" font-size="8.5" fill="rgba(255,255,255,0.5)">Bar · Donut · Scatter</text>
  <text x="111" y="371" text-anchor="middle" font-size="8.5" fill="rgba(255,255,255,0.5)">plotly.express / graph_objects</text>

  <rect x="26" y="382" width="170" height="44" rx="6" fill="rgba(0,60,140,0.3)" stroke="rgba(0,170,255,0.2)" stroke-width="1"/>
  <text x="111" y="399" text-anchor="middle" font-size="10" font-weight="600" fill="#8ecfff">User Guide Tab</text>
  <text x="111" y="413" text-anchor="middle" font-size="8.5" fill="rgba(255,255,255,0.5)">Embedded HTML cards</text>
  <text x="111" y="425" text-anchor="middle" font-size="8.5" fill="rgba(255,255,255,0.5)">st.expander FAQ sections</text>

  <!-- ── COLUMN 2: AI Layer ── -->
  <rect x="222" y="66" width="200" height="680" rx="10" fill="rgba(60,20,120,0.15)" stroke="rgba(124,58,237,0.25)" stroke-width="1"/>
  <rect x="222" y="66" width="200" height="28" rx="10" fill="rgba(124,58,237,0.3)"/>
  <text x="322" y="85" text-anchor="middle" font-size="11" font-weight="700" fill="#c4b5fd">AI ORCHESTRATION</text>

  <rect x="232" y="104" width="180" height="52" rx="6" fill="rgba(80,30,160,0.4)" stroke="rgba(124,58,237,0.4)" stroke-width="1"/>
  <text x="322" y="122" text-anchor="middle" font-size="10" font-weight="600" fill="#c4b5fd">Claude Opus 4.7 / GPT-4o</text>
  <text x="322" y="138" text-anchor="middle" font-size="8.5" fill="rgba(255,255,255,0.5)">openai.OpenAI(api_key=...)</text>
  <text x="322" y="150" text-anchor="middle" font-size="8.5" fill="rgba(255,255,255,0.5)">stream=True · temp=0.1</text>

  <rect x="232" y="166" width="180" height="52" rx="6" fill="rgba(80,30,160,0.3)" stroke="rgba(124,58,237,0.3)" stroke-width="1"/>
  <text x="322" y="184" text-anchor="middle" font-size="10" font-weight="600" fill="#c4b5fd">Scanner Agent</text>
  <text x="322" y="200" text-anchor="middle" font-size="8.5" fill="rgba(255,255,255,0.5)">Catalogues 1,200 findings</text>
  <text x="322" y="212" text-anchor="middle" font-size="8.5" fill="rgba(255,255,255,0.5)">system: scanner role prompt</text>

  <rect x="232" y="228" width="180" height="52" rx="6" fill="rgba(80,30,160,0.3)" stroke="rgba(124,58,237,0.3)" stroke-width="1"/>
  <text x="322" y="246" text-anchor="middle" font-size="10" font-weight="600" fill="#c4b5fd">Risk Analyst Agent</text>
  <text x="322" y="262" text-anchor="middle" font-size="8.5" fill="rgba(255,255,255,0.5)">PCI-DSS / SOC2 mapping</text>
  <text x="322" y="274" text-anchor="middle" font-size="8.5" fill="rgba(255,255,255,0.5)">ctx: Scanner output[:800]</text>

  <rect x="232" y="290" width="180" height="52" rx="6" fill="rgba(80,30,160,0.3)" stroke="rgba(124,58,237,0.3)" stroke-width="1"/>
  <text x="322" y="308" text-anchor="middle" font-size="10" font-weight="600" fill="#c4b5fd">Remediator Agent</text>
  <text x="322" y="324" text-anchor="middle" font-size="8.5" fill="rgba(255,255,255,0.5)">Secrets Mgr migration plan</text>
  <text x="322" y="336" text-anchor="middle" font-size="8.5" fill="rgba(255,255,255,0.5)">ctx: Risk output[:800]</text>

  <rect x="232" y="352" width="180" height="52" rx="6" fill="rgba(80,30,160,0.3)" stroke="rgba(124,58,237,0.3)" stroke-width="1"/>
  <text x="322" y="370" text-anchor="middle" font-size="10" font-weight="600" fill="#c4b5fd">Prevention Agent</text>
  <text x="322" y="386" text-anchor="middle" font-size="8.5" fill="rgba(255,255,255,0.5)">SCP · pre-commit hooks</text>
  <text x="322" y="398" text-anchor="middle" font-size="8.5" fill="rgba(255,255,255,0.5)">ctx: Remediator output[:800]</text>

  <rect x="232" y="414" width="180" height="52" rx="6" fill="rgba(80,30,160,0.3)" stroke="rgba(124,58,237,0.3)" stroke-width="1"/>
  <text x="322" y="432" text-anchor="middle" font-size="10" font-weight="600" fill="#c4b5fd">Auto-Remediation Loop</text>
  <text x="322" y="448" text-anchor="middle" font-size="8.5" fill="rgba(255,255,255,0.5)">INC → Dispatcher</text>
  <text x="322" y="460" text-anchor="middle" font-size="8.5" fill="rgba(255,255,255,0.5)">→ Remediator → Close</text>

  <!-- ── COLUMN 3: AWS Layer ── -->
  <rect x="438" y="66" width="210" height="680" rx="10" fill="rgba(80,50,0,0.15)" stroke="rgba(245,166,35,0.25)" stroke-width="1"/>
  <rect x="438" y="66" width="210" height="28" rx="10" fill="rgba(245,166,35,0.25)"/>
  <text x="543" y="85" text-anchor="middle" font-size="11" font-weight="700" fill="#f5a623">AWS LAYER</text>

  <rect x="448" y="104" width="190" height="52" rx="6" fill="rgba(100,65,0,0.4)" stroke="rgba(245,166,35,0.4)" stroke-width="1"/>
  <text x="543" y="122" text-anchor="middle" font-size="10" font-weight="600" fill="#f5a623">IAM Auth Chain</text>
  <text x="543" y="138" text-anchor="middle" font-size="8.5" fill="rgba(255,255,255,0.5)">Bootstrap (AKIAWQ35...) →</text>
  <text x="543" y="150" text-anchor="middle" font-size="8.5" fill="rgba(255,255,255,0.5)">sts:AssumeRole → temp creds (1h)</text>

  <rect x="448" y="166" width="190" height="44" rx="6" fill="rgba(100,65,0,0.3)" stroke="rgba(245,166,35,0.3)" stroke-width="1"/>
  <text x="543" y="183" text-anchor="middle" font-size="10" font-weight="600" fill="#f5a623">IAM Credential Report</text>
  <text x="543" y="197" text-anchor="middle" font-size="8.5" fill="rgba(255,255,255,0.5)">iam:GenerateCredentialReport</text>
  <text x="543" y="209" text-anchor="middle" font-size="8.5" fill="rgba(255,255,255,0.5)">Root keys · MFA · stale keys</text>

  <rect x="448" y="220" width="190" height="44" rx="6" fill="rgba(100,65,0,0.3)" stroke="rgba(245,166,35,0.3)" stroke-width="1"/>
  <text x="543" y="237" text-anchor="middle" font-size="10" font-weight="600" fill="#f5a623">Secrets Manager</text>
  <text x="543" y="251" text-anchor="middle" font-size="8.5" fill="rgba(255,255,255,0.5)">secretsmanager:ListSecrets</text>
  <text x="543" y="263" text-anchor="middle" font-size="8.5" fill="rgba(255,255,255,0.5)">Rotation status · ARN listing</text>

  <rect x="448" y="274" width="190" height="44" rx="6" fill="rgba(100,65,0,0.3)" stroke="rgba(245,166,35,0.3)" stroke-width="1"/>
  <text x="543" y="291" text-anchor="middle" font-size="10" font-weight="600" fill="#f5a623">Security Hub</text>
  <text x="543" y="305" text-anchor="middle" font-size="8.5" fill="rgba(255,255,255,0.5)">securityhub:GetFindings</text>
  <text x="543" y="317" text-anchor="middle" font-size="8.5" fill="rgba(255,255,255,0.5)">CIS Benchmark FAILED controls</text>

  <rect x="448" y="328" width="190" height="44" rx="6" fill="rgba(100,65,0,0.3)" stroke="rgba(245,166,35,0.3)" stroke-width="1"/>
  <text x="543" y="345" text-anchor="middle" font-size="10" font-weight="600" fill="#f5a623">AWS Backup</text>
  <text x="543" y="359" text-anchor="middle" font-size="8.5" fill="rgba(255,255,255,0.5)">backup:ListBackupVaults</text>
  <text x="543" y="371" text-anchor="middle" font-size="8.5" fill="rgba(255,255,255,0.5)">Vault Lock · WORM · recovery pts</text>

  <rect x="448" y="382" width="190" height="44" rx="6" fill="rgba(100,65,0,0.3)" stroke="rgba(245,166,35,0.3)" stroke-width="1"/>
  <text x="543" y="399" text-anchor="middle" font-size="10" font-weight="600" fill="#f5a623">EC2 · RDS · S3 · DynamoDB</text>
  <text x="543" y="413" text-anchor="middle" font-size="8.5" fill="rgba(255,255,255,0.5)">Describe APIs · Object Lock</text>
  <text x="543" y="425" text-anchor="middle" font-size="8.5" fill="rgba(255,255,255,0.5)">PITR status · versioning</text>

  <rect x="448" y="436" width="190" height="44" rx="6" fill="rgba(100,65,0,0.3)" stroke="rgba(245,166,35,0.3)" stroke-width="1"/>
  <text x="543" y="453" text-anchor="middle" font-size="10" font-weight="600" fill="#f5a623">aws_client.py</text>
  <text x="543" y="467" text-anchor="middle" font-size="8.5" fill="rgba(255,255,255,0.5)">AWSIntelligenceClient class</text>
  <text x="543" y="479" text-anchor="middle" font-size="8.5" fill="rgba(255,255,255,0.5)">boto3.Session · paginator</text>

  <!-- ── COLUMN 4: ServiceNow Layer ── -->
  <rect x="664" y="66" width="210" height="680" rx="10" fill="rgba(0,50,100,0.15)" stroke="rgba(0,170,255,0.25)" stroke-width="1"/>
  <rect x="664" y="66" width="210" height="28" rx="10" fill="rgba(0,120,200,0.3)"/>
  <text x="769" y="85" text-anchor="middle" font-size="11" font-weight="700" fill="#8ecfff">SERVICENOW LAYER</text>

  <rect x="674" y="104" width="190" height="52" rx="6" fill="rgba(0,60,130,0.4)" stroke="rgba(0,170,255,0.4)" stroke-width="1"/>
  <text x="769" y="122" text-anchor="middle" font-size="10" font-weight="600" fill="#8ecfff">servicenow.py</text>
  <text x="769" y="138" text-anchor="middle" font-size="8.5" fill="rgba(255,255,255,0.5)">ServiceNowClient class</text>
  <text x="769" y="150" text-anchor="middle" font-size="8.5" fill="rgba(255,255,255,0.5)">HTTPBasicAuth · requests</text>

  <rect x="674" y="166" width="190" height="44" rx="6" fill="rgba(0,60,130,0.3)" stroke="rgba(0,170,255,0.3)" stroke-width="1"/>
  <text x="769" y="183" text-anchor="middle" font-size="10" font-weight="600" fill="#8ecfff">SNOW_USER_MAP</text>
  <text x="769" y="197" text-anchor="middle" font-size="8.5" fill="rgba(255,255,255,0.5)">10 users · sys_id lookup</text>
  <text x="769" y="209" text-anchor="middle" font-size="8.5" fill="rgba(255,255,255,0.5)">commit_author → assigned_to</text>

  <rect x="674" y="220" width="190" height="44" rx="6" fill="rgba(0,60,130,0.3)" stroke="rgba(0,170,255,0.3)" stroke-width="1"/>
  <text x="769" y="237" text-anchor="middle" font-size="10" font-weight="600" fill="#8ecfff">create_incident()</text>
  <text x="769" y="251" text-anchor="middle" font-size="8.5" fill="rgba(255,255,255,0.5)">POST /api/now/table/incident</text>
  <text x="769" y="263" text-anchor="middle" font-size="8.5" fill="rgba(255,255,255,0.5)">severity → urgency/impact auto</text>

  <rect x="674" y="274" width="190" height="44" rx="6" fill="rgba(0,60,130,0.3)" stroke="rgba(0,170,255,0.3)" stroke-width="1"/>
  <text x="769" y="291" text-anchor="middle" font-size="10" font-weight="600" fill="#8ecfff">create_change_request()</text>
  <text x="769" y="305" text-anchor="middle" font-size="8.5" fill="rgba(255,255,255,0.5)">POST /api/now/table/change_request</text>
  <text x="769" y="317" text-anchor="middle" font-size="8.5" fill="rgba(255,255,255,0.5)">Emergency / Normal type</text>

  <rect x="674" y="328" width="190" height="44" rx="6" fill="rgba(0,60,130,0.3)" stroke="rgba(0,170,255,0.3)" stroke-width="1"/>
  <text x="769" y="345" text-anchor="middle" font-size="10" font-weight="600" fill="#8ecfff">update_incident()</text>
  <text x="769" y="359" text-anchor="middle" font-size="8.5" fill="rgba(255,255,255,0.5)">PATCH /api/now/table/incident/</text>
  <text x="769" y="371" text-anchor="middle" font-size="8.5" fill="rgba(255,255,255,0.5)">state=6 to close</text>

  <rect x="674" y="382" width="190" height="44" rx="6" fill="rgba(0,60,130,0.3)" stroke="rgba(0,170,255,0.3)" stroke-width="1"/>
  <text x="769" y="399" text-anchor="middle" font-size="10" font-weight="600" fill="#8ecfff">10 Real Users</text>
  <text x="769" y="413" text-anchor="middle" font-size="8.5" fill="rgba(255,255,255,0.5)">jane.smith · grace.lee · john.doe</text>
  <text x="769" y="425" text-anchor="middle" font-size="8.5" fill="rgba(255,255,255,0.5)">bob.wilson · alice.jones + 5 more</text>

  <!-- ── COLUMN 5: Deployment ── -->
  <rect x="890" y="66" width="294" height="680" rx="10" fill="rgba(0,80,40,0.15)" stroke="rgba(0,200,150,0.25)" stroke-width="1"/>
  <rect x="890" y="66" width="294" height="28" rx="10" fill="rgba(0,160,100,0.25)"/>
  <text x="1037" y="85" text-anchor="middle" font-size="11" font-weight="700" fill="#6ee7b7">DEPLOYMENT &amp; SECRETS</text>

  <rect x="900" y="104" width="274" height="80" rx="6" fill="rgba(0,60,35,0.4)" stroke="rgba(0,200,150,0.4)" stroke-width="1"/>
  <text x="1037" y="122" text-anchor="middle" font-size="10" font-weight="600" fill="#6ee7b7">Streamlit Secrets (.streamlit/secrets.toml)</text>
  <text x="900" y="142" font-size="8.5" fill="rgba(255,255,255,0.55)">   OPENAI_API_KEY     = sk-...</text>
  <text x="900" y="156" font-size="8.5" fill="rgba(255,255,255,0.55)">   AWS_ROLE_ARN       = arn:aws:iam::448549863273:role/CISCloudShieldRole</text>
  <text x="900" y="170" font-size="8.5" fill="rgba(255,255,255,0.55)">   AWS_ACCESS_KEY_ID  = AKIAWQ35HX5UTGMEE5C3  (bootstrap only)</text>

  <rect x="900" y="196" width="274" height="52" rx="6" fill="rgba(0,60,35,0.3)" stroke="rgba(0,200,150,0.3)" stroke-width="1"/>
  <text x="1037" y="214" text-anchor="middle" font-size="10" font-weight="600" fill="#6ee7b7">IAM Auth Flow</text>
  <text x="1037" y="230" text-anchor="middle" font-size="8.5" fill="rgba(255,255,255,0.5)">Bootstrap key → STS:AssumeRole</text>
  <text x="1037" y="242" text-anchor="middle" font-size="8.5" fill="rgba(255,255,255,0.5)">→ Temp creds (1h) → All AWS calls</text>

  <rect x="900" y="258" width="274" height="52" rx="6" fill="rgba(0,60,35,0.3)" stroke="rgba(0,200,150,0.3)" stroke-width="1"/>
  <text x="1037" y="276" text-anchor="middle" font-size="10" font-weight="600" fill="#6ee7b7">GitHub Repo</text>
  <text x="1037" y="292" text-anchor="middle" font-size="8.5" fill="rgba(255,255,255,0.5)">github.com/ajittgosavii/awssec</text>
  <text x="1037" y="304" text-anchor="middle" font-size="8.5" fill="rgba(255,255,255,0.5)">main branch · auto-deploy on push</text>

  <rect x="900" y="320" width="274" height="52" rx="6" fill="rgba(0,60,35,0.3)" stroke="rgba(0,200,150,0.3)" stroke-width="1"/>
  <text x="1037" y="338" text-anchor="middle" font-size="10" font-weight="600" fill="#6ee7b7">requirements.txt</text>
  <text x="1037" y="354" text-anchor="middle" font-size="8.5" fill="rgba(255,255,255,0.5)">streamlit · openai · boto3 · botocore</text>
  <text x="1037" y="366" text-anchor="middle" font-size="8.5" fill="rgba(255,255,255,0.5)">pandas · plotly · requests</text>

  <!-- Cross-layer arrows -->
  <line x1="206" y1="180" x2="222" y2="192" stroke="#7c3aed" stroke-width="1.3" stroke-dasharray="4,2" marker-end="url(#a1)"/>
  <line x1="412" y1="250" x2="438" y2="250" stroke="#f5a623" stroke-width="1.3" stroke-dasharray="4,2" marker-end="url(#a3)"/>
  <line x1="412" y1="370" x2="664" y2="230" stroke="#00aaff" stroke-width="1.3" stroke-dasharray="4,2" marker-end="url(#a1)"/>
  <line x1="648" y1="200" x2="664" y2="200" stroke="#00aaff" stroke-width="1.3" stroke-dasharray="4,2" marker-end="url(#a1)"/>

  <!-- Footer -->
  <rect x="0" y="778" width="1200" height="22" fill="rgba(0,61,156,0.4)"/>
  <text x="600" y="793" text-anchor="middle" font-size="9" fill="rgba(255,255,255,0.4)">Infosys Limited · CIS Cloud Shield · LLD · Confidential · v1.0 · 2026</text>
</svg>'''


# ═══════════════════════════════════════════════════════════════════════════════
# END USER FLOW
# ═══════════════════════════════════════════════════════════════════════════════
FLOW_SVG = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 1080" width="900" height="1080" font-family="Segoe UI,Arial,sans-serif">
  <defs>
    <linearGradient id="bg3" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#04091a"/><stop offset="100%" stop-color="#020610"/>
    </linearGradient>
    <linearGradient id="hdr3" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#003D9C"/><stop offset="100%" stop-color="#0066cc"/>
    </linearGradient>
    <marker id="af" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto">
      <path d="M0,0 L0,6 L8,3 z" fill="#00aaff"/>
    </marker>
    <marker id="afg" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto">
      <path d="M0,0 L0,6 L8,3 z" fill="#00c896"/>
    </marker>
    <marker id="afy" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto">
      <path d="M0,0 L0,6 L8,3 z" fill="#f5a623"/>
    </marker>
  </defs>

  <rect width="900" height="1080" fill="url(#bg3)"/>
  <rect x="0" y="0" width="900" height="54" fill="url(#hdr3)"/>
  <text x="450" y="22" text-anchor="middle" font-size="17" font-weight="700" fill="white">Infosys CIS Cloud Shield — End User Flow</text>
  <text x="450" y="42" text-anchor="middle" font-size="10" fill="rgba(255,255,255,0.6)">Step-by-step journey from login to closed ServiceNow ticket</text>

  <!-- Step helper: each step is a rounded box with number badge -->

  <!-- STEP 1 -->
  <rect x="100" y="74" width="700" height="68" rx="10" fill="rgba(0,60,140,0.4)" stroke="rgba(0,170,255,0.4)" stroke-width="1.5"/>
  <circle cx="136" cy="108" r="18" fill="#003D9C"/>
  <text x="136" y="113" text-anchor="middle" font-size="14" font-weight="700" fill="white">1</text>
  <text x="170" y="100" font-size="13" font-weight="700" fill="#8ecfff">Login to Infosys CIS Cloud Shield</text>
  <text x="170" y="118" font-size="10" fill="rgba(255,255,255,0.6)">Navigate to Streamlit Cloud URL · Enter username: admin · Password: Infosys@123 · Click Sign In</text>
  <text x="170" y="132" font-size="10" fill="rgba(255,255,255,0.45)">Session persists until browser tab is closed</text>

  <line x1="450" y1="142" x2="450" y2="160" stroke="#00aaff" stroke-width="2" marker-end="url(#af)"/>

  <!-- STEP 2 -->
  <rect x="100" y="162" width="700" height="68" rx="10" fill="rgba(0,60,140,0.35)" stroke="rgba(0,170,255,0.3)" stroke-width="1.5"/>
  <circle cx="136" cy="196" r="18" fill="#003D9C"/>
  <text x="136" y="201" text-anchor="middle" font-size="14" font-weight="700" fill="white">2</text>
  <text x="170" y="188" font-size="13" font-weight="700" fill="#8ecfff">Configure OpenAI in Sidebar</text>
  <text x="170" y="206" font-size="10" fill="rgba(255,255,255,0.6)">Sidebar → OpenAI section · Paste sk-... API key (or pre-loaded from Streamlit secrets)</text>
  <text x="170" y="220" font-size="10" fill="rgba(255,255,255,0.45)">Select model: gpt-4o (recommended) · gpt-4o-mini (faster) · gpt-4-turbo</text>

  <line x1="450" y1="230" x2="450" y2="248" stroke="#00aaff" stroke-width="2" marker-end="url(#af)"/>

  <!-- STEP 3 -->
  <rect x="100" y="250" width="700" height="68" rx="10" fill="rgba(0,60,140,0.35)" stroke="rgba(0,170,255,0.3)" stroke-width="1.5"/>
  <circle cx="136" cy="284" r="18" fill="#003D9C"/>
  <text x="136" y="289" text-anchor="middle" font-size="14" font-weight="700" fill="white">3</text>
  <text x="170" y="276" font-size="13" font-weight="700" fill="#8ecfff">Connect ServiceNow</text>
  <text x="170" y="294" font-size="10" fill="rgba(255,255,255,0.6)">Sidebar → ServiceNow · URL: dev218436.service-now.com · User: admin · Click Test SNOW Connection</text>
  <text x="170" y="308" font-size="10" fill="rgba(255,255,255,0.45)">Green banner confirms API reachable · 10 real engineer profiles pre-created</text>

  <line x1="450" y1="318" x2="450" y2="336" stroke="#00aaff" stroke-width="2" marker-end="url(#af)"/>

  <!-- STEP 4 -->
  <rect x="100" y="338" width="700" height="80" rx="10" fill="rgba(0,80,30,0.35)" stroke="rgba(0,200,150,0.4)" stroke-width="1.5"/>
  <circle cx="136" cy="378" r="18" fill="#006030"/>
  <text x="136" y="383" text-anchor="middle" font-size="14" font-weight="700" fill="white">4</text>
  <text x="170" y="364" font-size="13" font-weight="700" fill="#6ee7b7">Connect AWS via IAM Role (AssumeRole)</text>
  <text x="170" y="382" font-size="10" fill="rgba(255,255,255,0.6)">Select Auth Method: IAM Role · Paste ARN: arn:aws:iam::448549863273:role/CISCloudShieldRole</text>
  <text x="170" y="396" font-size="10" fill="rgba(255,255,255,0.6)">Bootstrap credentials auto-loaded from secrets · Select Region · Click Connect to AWS</text>
  <text x="170" y="410" font-size="10" fill="rgba(255,255,255,0.45)">Green: Connected Account 448549863273 · Role assumed · 1-hour temp credentials active</text>

  <line x1="450" y1="418" x2="450" y2="436" stroke="#00aaff" stroke-width="2" marker-end="url(#af)"/>

  <!-- STEP 5 -->
  <rect x="100" y="438" width="700" height="80" rx="10" fill="rgba(60,20,120,0.35)" stroke="rgba(124,58,237,0.4)" stroke-width="1.5"/>
  <circle cx="136" cy="478" r="18" fill="#5b21b6"/>
  <text x="136" y="483" text-anchor="middle" font-size="14" font-weight="700" fill="white">5</text>
  <text x="170" y="460" font-size="13" font-weight="700" fill="#c4b5fd">Tab 1: Run Credential Intelligence</text>
  <text x="170" y="478" font-size="10" fill="rgba(255,255,255,0.6)">Open 🔐 Credential Intelligence · Review KPI cards (CRITICAL/HIGH/MEDIUM counts)</text>
  <text x="170" y="494" font-size="10" fill="rgba(255,255,255,0.6)">Filter findings by severity/environment · Click Launch AI Security Analysis</text>
  <text x="170" y="508" font-size="10" fill="rgba(255,255,255,0.45)">4 agents stream output: Scanner → Risk → Remediator → Prevention (live token-by-token)</text>

  <line x1="450" y1="518" x2="450" y2="536" stroke="#00aaff" stroke-width="2" marker-end="url(#af)"/>

  <!-- STEP 6 -->
  <rect x="100" y="538" width="700" height="68" rx="10" fill="rgba(60,20,120,0.3)" stroke="rgba(124,58,237,0.3)" stroke-width="1.5"/>
  <circle cx="136" cy="572" r="18" fill="#5b21b6"/>
  <text x="136" y="577" text-anchor="middle" font-size="14" font-weight="700" fill="white">6</text>
  <text x="170" y="560" font-size="13" font-weight="700" fill="#c4b5fd">Raise ServiceNow Change Requests</text>
  <text x="170" y="578" font-size="10" fill="rgba(255,255,255,0.6)">Set slider (1-10 max CHGs) · Click Create SNOW Change Requests (Critical Findings)</text>
  <text x="170" y="592" font-size="10" fill="rgba(255,255,255,0.45)">CHG auto-assigned to commit author (e.g. jane.smith) · Results table shows CHG number + SNOW link</text>

  <line x1="450" y1="606" x2="450" y2="624" stroke="#00aaff" stroke-width="2" marker-end="url(#af)"/>

  <!-- STEP 7 -->
  <rect x="100" y="626" width="700" height="68" rx="10" fill="rgba(80,50,0,0.35)" stroke="rgba(245,166,35,0.4)" stroke-width="1.5"/>
  <circle cx="136" cy="660" r="18" fill="#92400e"/>
  <text x="136" y="665" text-anchor="middle" font-size="14" font-weight="700" fill="white">7</text>
  <text x="170" y="648" font-size="13" font-weight="700" fill="#f5a623">Tab 2: Assess Backup Coverage</text>
  <text x="170" y="666" font-size="10" fill="rgba(255,255,255,0.6)">Open 💾 Backup Intelligence · Review donut chart and KPI tiles (Protected/Partial/Unprotected)</text>
  <text x="170" y="680" font-size="10" fill="rgba(255,255,255,0.45)">Click Scan AWS Backup Coverage for live data · Create SNOW Incidents for unprotected apps</text>

  <line x1="450" y1="694" x2="450" y2="712" stroke="#00aaff" stroke-width="2" marker-end="url(#af)"/>

  <!-- STEP 8 -->
  <rect x="100" y="714" width="700" height="80" rx="10" fill="rgba(0,80,50,0.35)" stroke="rgba(0,200,150,0.4)" stroke-width="1.5"/>
  <circle cx="136" cy="754" r="18" fill="#065f46"/>
  <text x="136" y="759" text-anchor="middle" font-size="14" font-weight="700" fill="white">8</text>
  <text x="170" y="736" font-size="13" font-weight="700" fill="#6ee7b7">Tab 3: Run Auto-Remediation Loop</text>
  <text x="170" y="754" font-size="10" fill="rgba(255,255,255,0.6)">Open 🔄 Auto-Remediation Loop · Set source (Mock/Live), count (1-3 for demo), severity (CRITICAL)</text>
  <text x="170" y="770" font-size="10" fill="rgba(255,255,255,0.6)">Click ▶ Start Remediation Loop · Watch INC→Dispatcher→Remediator→Close stream in real time</text>
  <text x="170" y="784" font-size="10" fill="rgba(255,255,255,0.45)">INC created → CHG raised → remediated → INC closed in ServiceNow automatically</text>

  <line x1="450" y1="794" x2="450" y2="812" stroke="#afg" stroke-width="2" marker-end="url(#afg)"/>

  <!-- STEP 9 -->
  <rect x="100" y="814" width="700" height="68" rx="10" fill="rgba(0,80,50,0.3)" stroke="rgba(0,200,150,0.3)" stroke-width="1.5"/>
  <circle cx="136" cy="848" r="18" fill="#065f46"/>
  <text x="136" y="853" text-anchor="middle" font-size="14" font-weight="700" fill="white">9</text>
  <text x="170" y="836" font-size="13" font-weight="700" fill="#6ee7b7">Review Summary &amp; ServiceNow Tickets</text>
  <text x="170" y="854" font-size="10" fill="rgba(255,255,255,0.6)">Loop Summary table: INC numbers, SNOW links, assigned engineers, status (✅ Resolved)</text>
  <text x="170" y="868" font-size="10" fill="rgba(255,255,255,0.45)">Click SNOW links to open tickets in ServiceNow · Confirm INC state = Closed</text>

  <line x1="450" y1="882" x2="450" y2="900" stroke="#00c896" stroke-width="2" marker-end="url(#afg)"/>

  <!-- STEP 10 — OUTCOME -->
  <rect x="60" y="902" width="780" height="84" rx="12" fill="rgba(0,61,156,0.3)" stroke="#00aaff" stroke-width="2"/>
  <text x="450" y="928" text-anchor="middle" font-size="14" font-weight="700" fill="#00aaff">✅ Outcome Achieved</text>
  <text x="450" y="950" text-anchor="middle" font-size="10" fill="rgba(255,255,255,0.7)">Credentials scanned · AI analysis complete · CHGs raised and assigned · Backup gaps identified</text>
  <text x="450" y="966" text-anchor="middle" font-size="10" fill="rgba(255,255,255,0.7)">Auto-remediation loop executed · ServiceNow incidents created, progressed, and closed</text>
  <text x="450" y="982" text-anchor="middle" font-size="10" fill="rgba(255,255,255,0.5)">Full audit trail in CloudTrail · SNOW tickets with real user assignment · Live AWS data if connected</text>

  <!-- Footer -->
  <rect x="0" y="1058" width="900" height="22" fill="rgba(0,61,156,0.4)"/>
  <text x="450" y="1073" text-anchor="middle" font-size="9" fill="rgba(255,255,255,0.4)">Infosys Limited · CIS Cloud Shield · End User Flow · Confidential · v1.0 · 2026</text>
</svg>'''

# ── Write files ────────────────────────────────────────────────────────────────
files = {
    "hld_diagram.svg":       HLD_SVG,
    "lld_diagram.svg":       LLD_SVG,
    "enduser_flow.svg":      FLOW_SVG,
}
base = r"c:\aidemos\aws-security-backup-platform"
for fname, content in files.items():
    path = f"{base}\\{fname}"
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Saved: {path}")
