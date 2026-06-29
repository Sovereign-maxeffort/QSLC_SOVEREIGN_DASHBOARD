import os
import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="QSLC EVE Command Center",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

APP_VERSION = "EVE-SSOT-v2.0-live"
LOCAL_ROOT = Path(os.getenv("QSLC_ROOT", r"C:\QSLC"))
VAULT_ROOT = Path(os.getenv("QSLC_VAULT", r"C:\QSLC_VAULT"))
SSOT_DIR = LOCAL_ROOT / "SSOT"
REPORTS_DIR = LOCAL_ROOT / "Reports"
CLI_DIR = LOCAL_ROOT / "CLI"
FINANCE_DIR = LOCAL_ROOT / "Finance"
LEGAL_DIR = LOCAL_ROOT / "Legal"
DASHBOARD_DIR = LOCAL_ROOT / "Dashboard"

SSOT_LOG = SSOT_DIR / "real_time_log.csv"
TASKS_CSV = SSOT_DIR / "tasks.csv"
LEDGER_CSV = SSOT_DIR / "ledger.csv"
PAYCHEX_EXPORT = SSOT_DIR / "paychex_export.csv"
EVE_METRICS_JSON = SSOT_DIR / "eve_metrics.json"
REPORT_HTML = REPORTS_DIR / "timecard_report_latest.html"

NASA_DESI_GALAXIES_QUASARS = 47_000_000
NASA_SPHEREX_COLORS = 102
DARK_ENERGY_LOW = 68.3
DARK_ENERGY_HIGH = 70.0
PATENT_READY_TARGET = float(os.getenv("QSLC_PATENT_TARGET", "30000"))
CEO_DEFAULT_RATE = float(os.getenv("QSLC_CEO_RATE", "75"))
TASK_SLA_HOURS = float(os.getenv("QSLC_TASK_SLA_HOURS", "24"))

st.markdown(
    """
<style>
    .stApp { background: radial-gradient(circle at top, #111827 0%, #020617 45%, #000 100%); color: #dffbff; }
    [data-testid="stSidebar"] { background: #020617; }
    h1, h2, h3 { font-family: 'Arial Black', sans-serif; letter-spacing: .04em; }
    .eve-card { border: 1px solid rgba(0,243,255,.35); border-radius: 18px; padding: 18px; background: rgba(15,23,42,.72); box-shadow: 0 0 28px rgba(0,243,255,.10); }
    .gold { color: #ffd700; }
    .cyan { color: #00f3ff; }
    .danger { color: #ff5d73; }
    .ok { color: #5dffb2; }
    .cmd { background: #0b1220; border: 1px solid rgba(0,243,255,.22); padding: 12px; border-radius: 10px; font-family: monospace; }
    .small { opacity: .72; font-size: .88rem; }
</style>
""",
    unsafe_allow_html=True,
)


def ensure_local_structure() -> None:
    for path in [
        LOCAL_ROOT,
        SSOT_DIR,
        REPORTS_DIR,
        FINANCE_DIR,
        LEGAL_DIR,
        DASHBOARD_DIR,
        CLI_DIR,
        VAULT_ROOT,
        VAULT_ROOT / "exports",
        VAULT_ROOT / "reports",
        VAULT_ROOT / "inventory",
    ]:
        path.mkdir(parents=True, exist_ok=True)

    if not EVE_METRICS_JSON.exists():
        default_metrics = {
            "eve_coverage_index_percent": 80,
            "psi_balance": 0,
            "sol_balance": 0,
            "patent_fund_usd": 0,
            "public_message": "Hello. We build with discipline, love, and raw technology. The code knows the way; the team stays humble.",
            "last_updated": datetime.now().isoformat(),
        }
        EVE_METRICS_JSON.write_text(json.dumps(default_metrics, indent=2), encoding="utf-8")

    if not TASKS_CSV.exists():
        pd.DataFrame(
            [
                {"Task": "Rotate exposed API keys", "Owner": "EVE", "Status": "Open", "Priority": "High", "UpdatedAt": datetime.now().isoformat()},
                {"Task": "Review patent fund tracker", "Owner": "CEO", "Status": "Open", "Priority": "High", "UpdatedAt": datetime.now().isoformat()},
                {"Task": "Publish daily dashboard content", "Owner": "EVE", "Status": "Open", "Priority": "Medium", "UpdatedAt": datetime.now().isoformat()},
            ]
        ).to_csv(TASKS_CSV, index=False)

    if not SSOT_LOG.exists():
        pd.DataFrame(columns=["Start", "End", "Employee", "Hours", "Source", "Note"]).to_csv(SSOT_LOG, index=False)

    if not LEDGER_CSV.exists():
        pd.DataFrame(columns=["Date", "Category", "Description", "Amount", "Source"]).to_csv(LEDGER_CSV, index=False)


def safe_read_csv(path: Path, columns: list[str]) -> pd.DataFrame:
    if path.exists():
        try:
            return pd.read_csv(path)
        except Exception:
            return pd.DataFrame(columns=columns)
    return pd.DataFrame(columns=columns)


def read_metrics() -> dict:
    try:
        return json.loads(EVE_METRICS_JSON.read_text(encoding="utf-8"))
    except Exception:
        return {}


def build_paychex(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, row in df.iterrows():
        try:
            hours = float(row.get("Hours", 0) or 0)
        except Exception:
            hours = 0
        employee = row.get("Employee", "WHITE ANTWAN") or "WHITE ANTWAN"
        rate = CEO_DEFAULT_RATE if str(employee).upper().strip() == "WHITE ANTWAN" else 20
        gross = round(hours * rate, 2)
        start = row.get("Start", "")
        try:
            date = pd.to_datetime(start).strftime("%Y-%m-%d")
        except Exception:
            date = datetime.now().strftime("%Y-%m-%d")
        rows.append({"Date": date, "Employee": employee, "Hours": hours, "Rate": rate, "Gross": gross, "Source": row.get("Source", "EVE")})
    return pd.DataFrame(rows, columns=["Date", "Employee", "Hours", "Rate", "Gross", "Source"])


def local_command(command: str) -> str:
    return f'powershell -ExecutionPolicy Bypass -File C:\\QSLC\\CLI\\eve.ps1 {command}'


def command_card(title: str, command: str, help_text: str) -> None:
    st.markdown(f"### {title}")
    st.code(local_command(command), language="powershell")
    st.caption(help_text)


def task_age_hours(updated_at) -> float:
    try:
        dt = pd.to_datetime(updated_at, utc=True)
        return round((pd.Timestamp.now(tz="UTC") - dt).total_seconds() / 3600, 2)
    except Exception:
        return 9999.0


def render_header() -> None:
    st.markdown("# 🧠 QSLC EVE Command Center")
    st.caption(f"{APP_VERSION} · one SSOT · live local files · Streamlit port 8502 · no raw secrets in repo")
    st.markdown("---")


ensure_local_structure()
render_header()

log_df = safe_read_csv(SSOT_LOG, ["Start", "End", "Employee", "Hours", "Source", "Note"])
paychex_df = build_paychex(log_df)
tasks_df = safe_read_csv(TASKS_CSV, ["Task", "Owner", "Status", "Priority", "UpdatedAt"])
ledger_df = safe_read_csv(LEDGER_CSV, ["Date", "Category", "Description", "Amount", "Source"])
metrics = read_metrics()

total_hours = round(float(paychex_df["Hours"].sum()), 2) if not paychex_df.empty else 0.0
total_gross = round(float(paychex_df["Gross"].sum()), 2) if not paychex_df.empty else 0.0
patent_fund = float(metrics.get("patent_fund_usd", 0) or 0)
patent_remaining = max(PATENT_READY_TARGET - patent_fund, 0)
patent_pct = min(round((patent_fund / PATENT_READY_TARGET) * 100, 1), 100) if PATENT_READY_TARGET else 0
open_tasks = 0
stale_tasks = 0
if not tasks_df.empty:
    open_tasks = len(tasks_df[~tasks_df["Status"].astype(str).str.lower().isin(["done", "closed", "complete", "completed"])] )
    tasks_df["AgeHours"] = tasks_df["UpdatedAt"].apply(task_age_hours)
    stale_tasks = len(tasks_df[(tasks_df["AgeHours"] > TASK_SLA_HOURS) & (~tasks_df["Status"].astype(str).str.lower().isin(["done", "closed", "complete", "completed"]))])

with st.sidebar:
    st.markdown("## 🔐 Control Lane")
    st.success("Use Windows Terminal → PowerShell")
    st.markdown("**Master local path**")
    st.code(str(LOCAL_ROOT), language="text")
    st.markdown("**Vault path**")
    st.code(str(VAULT_ROOT), language="text")
    st.markdown("---")
    st.markdown("## 🚀 One-line install")
    st.code("powershell -ExecutionPolicy Bypass -File .\\scripts\\INSTALL_ROGLEX_EVE.ps1", language="powershell")
    st.warning("Do not paste API keys into GitHub. Use .env locally or Streamlit Secrets.")

m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("System", "LIVE")
m2.metric("Total Hours", total_hours)
m3.metric("Gross Estimate", f"${total_gross:,.2f}")
m4.metric("Open Tasks", open_tasks, delta=f"{stale_tasks} stale", delta_color="inverse" if stale_tasks else "normal")
m5.metric("Patent Fund", f"{patent_pct}%", delta=f"${patent_remaining:,.0f} left")

st.markdown("---")
tabs = st.tabs(["🧭 Command Board", "💸 Paychex", "📊 Live Dashboard", "🌌 Star Map", "⚖️ Patent & Legal", "🔐 Security", "📱 iPhone/ROG"])

with tabs[0]:
    st.markdown("## One control point")
    st.markdown("Run these from **Windows Terminal → PowerShell** on the ROGLEX.")
    c1, c2, c3 = st.columns(3)
    with c1:
        command_card("Start work", "start", "Starts a local work session.")
        command_card("Stop work", "stop", "Stops session and writes hours into the SSOT CSV.")
    with c2:
        command_card("Export Paychex", "export", "Creates C:\\QSLC\\SSOT\\paychex_export.csv.")
        command_card("Generate report", "pdf", "Builds the professional timecard report.")
    with c3:
        command_card("Print report", "print", "Sends latest timecard report to default printer.")
        command_card("Diagnose", "diagnose", "Checks folders, Python, Streamlit, Git, and local files.")

    st.markdown("### Live task SLA")
    st.caption(f"Rule: no open task should remain untouched for more than {TASK_SLA_HOURS:g} hours.")
    st.dataframe(tasks_df, use_container_width=True)

with tabs[1]:
    st.markdown("## Paychex-ready export")
    if paychex_df.empty:
        st.warning("No local SSOT time entries found yet. Run `eve start`, then `eve stop`, then refresh this app on the ROG.")
    else:
        st.dataframe(paychex_df, use_container_width=True)
        st.download_button("Download Paychex CSV", paychex_df.to_csv(index=False), "paychex_export.csv", "text/csv")
    st.markdown("### Manual entry fallback")
    with st.form("manual_time_entry"):
        col_a, col_b = st.columns(2)
        employee = col_a.text_input("Employee", "WHITE ANTWAN")
        hours = col_b.number_input("Hours", min_value=0.0, max_value=24.0, value=8.0, step=0.25)
        note = st.text_input("Note", "Manual dashboard entry")
        submitted = st.form_submit_button("Generate standalone CSV row")
        if submitted:
            rate = CEO_DEFAULT_RATE if employee.upper() == "WHITE ANTWAN" else 20
            temp = pd.DataFrame([{"Date": datetime.now().strftime("%Y-%m-%d"), "Employee": employee, "Hours": hours, "Rate": rate, "Gross": round(hours * rate, 2), "Source": note}])
            st.dataframe(temp, use_container_width=True)
            st.download_button("Download manual Paychex row", temp.to_csv(index=False), "manual_paychex_row.csv", "text/csv")

with tabs[2]:
    st.markdown("## Live visual command center")
    col_a, col_b = st.columns([2, 1])
    with col_a:
        st.markdown(f"""
<div class="eve-card">
  <h2 class="cyan">EVE HEI ACTIVE</h2>
  <p>Local SSOT: <b>{SSOT_DIR}</b></p>
  <p>Vault: <b>{VAULT_ROOT}</b></p>
  <p class="gold">Control mode: local-first, cloud-assisted only when you explicitly connect it.</p>
  <p>{metrics.get('public_message', 'Hello. We build with discipline, love, and raw technology.')}</p>
</div>
""", unsafe_allow_html=True)
    with col_b:
        st.metric("SOL Balance", metrics.get("sol_balance", 0))
        st.metric("PSI Balance", metrics.get("psi_balance", 0))
        st.metric("Last Metrics Update", str(metrics.get("last_updated", "not set"))[:19])

    if not ledger_df.empty:
        st.markdown("### Ledger activity")
        st.dataframe(ledger_df.tail(50), use_container_width=True)
        if "Amount" in ledger_df.columns:
            chart_df = ledger_df.copy()
            chart_df["Amount"] = pd.to_numeric(chart_df["Amount"], errors="coerce").fillna(0)
            if "Category" in chart_df.columns:
                st.bar_chart(chart_df.groupby("Category")["Amount"].sum())
    else:
        st.info("Ledger file is ready at C:\\QSLC\\SSOT\\ledger.csv. Add rows there and refresh.")

with tabs[3]:
    st.markdown("## Universe benchmark + proprietary EVE index")
    st.caption("This tab separates public science benchmarks from your private EVE coverage index so the public page stays clean and defensible.")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("DESI public map", f"{NASA_DESI_GALAXIES_QUASARS:,}+", "galaxies/quasars")
    c2.metric("SPHEREx colors", NASA_SPHEREX_COLORS, "infrared maps")
    c3.metric("Dark Energy", f"{DARK_ENERGY_LOW}-{DARK_ENERGY_HIGH}%", "public estimate")
    c4.metric("EVE Coverage Index", f"{metrics.get('eve_coverage_index_percent', 0)}%", "private metric")

    star_html = """
    <div class="eve-card" style="height:360px; position:relative; overflow:hidden; background:radial-gradient(circle, rgba(0,243,255,.18), rgba(2,6,23,.95));">
      <div style="position:absolute; left:45%; top:40%; width:80px; height:80px; border-radius:50%; background:#00f3ff; box-shadow:0 0 60px #00f3ff;"></div>
      <div style="position:absolute; left:20%; top:20%; width:9px; height:9px; border-radius:50%; background:#ffd700; box-shadow:0 0 18px #ffd700;"></div>
      <div style="position:absolute; left:70%; top:22%; width:10px; height:10px; border-radius:50%; background:#a78bfa; box-shadow:0 0 18px #a78bfa;"></div>
      <div style="position:absolute; left:62%; top:72%; width:7px; height:7px; border-radius:50%; background:#5dffb2; box-shadow:0 0 18px #5dffb2;"></div>
      <div style="position:absolute; left:30%; top:68%; width:11px; height:11px; border-radius:50%; background:#ff5d73; box-shadow:0 0 18px #ff5d73;"></div>
      <p style="position:absolute; bottom:12px; left:16px; color:#dffbff;">5D Star Map UI placeholder · replace with Three.js/WebGL component when connected.</p>
    </div>
    """
    st.markdown(star_html, unsafe_allow_html=True)

with tabs[4]:
    st.markdown("## Patent readiness and legal tracker")
    p1, p2, p3 = st.columns(3)
    p1.metric("Patent target", f"${PATENT_READY_TARGET:,.0f}")
    p2.metric("Funds allocated", f"${patent_fund:,.0f}")
    p3.metric("Remaining", f"${patent_remaining:,.0f}")
    st.progress(patent_pct / 100)
    st.info("Update C:\\QSLC\\SSOT\\eve_metrics.json → patent_fund_usd to drive this tracker.")

with tabs[5]:
    st.markdown("## Security lock")
    st.error("Any API key already pasted into chat or committed to GitHub must be treated as compromised and rotated.")
    st.markdown("**Rules locked into this repo:**")
    st.markdown("- No plaintext API keys in source code")
    st.markdown("- `.env` stays local only")
    st.markdown("- Streamlit secrets stay in Streamlit Cloud settings")
    st.markdown("- Crypto seed phrases never go into agents, GitHub, Streamlit, Make, monday, or chat")
    st.markdown("- The local encrypted vault is for backups, not raw public commits")

with tabs[6]:
    st.markdown("## iPhone → ROG control")
    st.markdown("**Lane A: local only** — open ROGLEX, double-click EVE ONE BUTTON, run `eve help`.")
    st.markdown("**Lane B: mobile SSH** — enable OpenSSH on the ROG and connect from an iPhone SSH app.")
    st.code("powershell -ExecutionPolicy Bypass -File C:\\QSLC\\Agent\\OPTIONAL_enable_iphone_ssh.ps1", language="powershell")

st.markdown("---")
st.caption("QSLC EVE consolidated into one safe GitHub/Streamlit control lane. Live files load from C:\\QSLC\\SSOT.")
