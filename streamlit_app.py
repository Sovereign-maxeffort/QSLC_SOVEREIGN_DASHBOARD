import os
import csv
import json
from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="QSLC EVE Command Center",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

APP_VERSION = "EVE-SSOT-v1.0"
LOCAL_ROOT = Path(os.getenv("QSLC_ROOT", r"C:\QSLC"))
VAULT_ROOT = Path(os.getenv("QSLC_VAULT", r"C:\QSLC_VAULT"))
SSOT_LOG = LOCAL_ROOT / "SSOT" / "real_time_log.csv"
PAYCHEX_EXPORT = LOCAL_ROOT / "SSOT" / "paychex_export.csv"
REPORT_HTML = LOCAL_ROOT / "Reports" / "timecard_report_latest.html"

st.markdown(
    """
<style>
    .stApp { background: radial-gradient(circle at top, #10172a 0%, #020617 48%, #000 100%); color: #dffbff; }
    [data-testid="stSidebar"] { background: #020617; }
    h1, h2, h3 { font-family: 'Arial Black', sans-serif; letter-spacing: .04em; }
    .eve-card { border: 1px solid rgba(0,243,255,.35); border-radius: 18px; padding: 18px; background: rgba(15,23,42,.72); box-shadow: 0 0 28px rgba(0,243,255,.10); }
    .gold { color: #ffd700; }
    .cyan { color: #00f3ff; }
    .danger { color: #ff5d73; }
    .ok { color: #5dffb2; }
    .cmd { background: #0b1220; border: 1px solid rgba(0,243,255,.22); padding: 12px; border-radius: 10px; font-family: monospace; }
</style>
""",
    unsafe_allow_html=True,
)


def ensure_local_structure() -> None:
    for path in [
        LOCAL_ROOT,
        LOCAL_ROOT / "SSOT",
        LOCAL_ROOT / "Reports",
        LOCAL_ROOT / "Finance",
        LOCAL_ROOT / "Dashboard",
        VAULT_ROOT,
        VAULT_ROOT / "exports",
        VAULT_ROOT / "reports",
        VAULT_ROOT / "inventory",
    ]:
        try:
            path.mkdir(parents=True, exist_ok=True)
        except Exception:
            pass


def read_time_log() -> pd.DataFrame:
    if SSOT_LOG.exists():
        try:
            return pd.read_csv(SSOT_LOG)
        except Exception:
            return pd.DataFrame(columns=["Start", "End", "Employee", "Hours", "Source", "Note"])
    return pd.DataFrame(columns=["Start", "End", "Employee", "Hours", "Source", "Note"])


def build_paychex(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, row in df.iterrows():
        try:
            hours = float(row.get("Hours", 0) or 0)
        except Exception:
            hours = 0
        employee = row.get("Employee", "WHITE ANTWAN") or "WHITE ANTWAN"
        rate = 75 if str(employee).upper().strip() == "WHITE ANTWAN" else 20
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


def render_header() -> None:
    st.markdown("# 🧠 QSLC EVE Command Center")
    st.caption(f"{APP_VERSION} · one SSOT · local-first · no raw secrets in repo")
    st.markdown("---")


def command_card(title: str, command: str, help_text: str) -> None:
    st.markdown(f"### {title}")
    st.code(local_command(command), language="powershell")
    st.caption(help_text)


ensure_local_structure()
render_header()

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

log_df = read_time_log()
paychex_df = build_paychex(log_df)

total_hours = round(float(paychex_df["Hours"].sum()), 2) if not paychex_df.empty else 0.0
total_gross = round(float(paychex_df["Gross"].sum()), 2) if not paychex_df.empty else 0.0
last_entry = "No local time log loaded"
if not log_df.empty and "End" in log_df.columns:
    last_entry = str(log_df.tail(1).iloc[0].get("End", "No end time"))

m1, m2, m3, m4 = st.columns(4)
m1.metric("System", "READY")
m2.metric("Total Hours", total_hours)
m3.metric("Gross Estimate", f"${total_gross:,.2f}")
m4.metric("Last Entry", last_entry[:22])

st.markdown("---")
tabs = st.tabs(["🧭 Command Board", "💸 Paychex", "📊 Dashboard", "🔐 Security", "📱 iPhone/ROG"])

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
        command_card("Diagnose", "diagnose", "Checks printer, folders, cloud paths, Azure CLI, and SSH.")

    st.markdown("### Natural-language command explanations")
    term = st.selectbox("Explain command", ["dism", "acl", "alias", "function", "cmd", "powershell", "bitlocker", "virtual disk", "virtual desktop", "ssh"])
    explanations = {
        "dism": "DISM repairs/manages Windows images. Do not run destructive repair commands without a backup.",
        "acl": "ACL is file/folder permission control. Wrong ACL changes can lock you out.",
        "alias": "Alias is a shortcut command. In this repo, eve/e are shortcuts for the EVE PowerShell shell.",
        "function": "Function is reusable PowerShell code that can accept arguments and run logic.",
        "cmd": "CMD is the older Windows shell. Use PowerShell for EVE.",
        "powershell": "PowerShell is the automation shell. Windows Terminal is only the window hosting it.",
        "bitlocker": "BitLocker encrypts the drive. Save the recovery key before enabling it.",
        "virtual disk": "A VHD/VHDX file behaves like a drive. Useful for vaults/backups.",
        "virtual desktop": "A separate/remote desktop environment. EVE runs locally unless remote access is enabled.",
        "ssh": "Secure terminal access. Use this for iPhone-to-ROG command control if configured.",
    }
    st.info(explanations[term])

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
            temp = pd.DataFrame([{"Date": datetime.now().strftime("%Y-%m-%d"), "Employee": employee, "Hours": hours, "Rate": 75 if employee.upper()=="WHITE ANTWAN" else 20, "Gross": round(hours*(75 if employee.upper()=="WHITE ANTWAN" else 20), 2), "Source": note}])
            st.dataframe(temp, use_container_width=True)
            st.download_button("Download manual Paychex row", temp.to_csv(index=False), "manual_paychex_row.csv", "text/csv")

with tabs[2]:
    st.markdown("## Live visual command center")
    st.markdown("""
<div class="eve-card">
  <h2 class="cyan">EVE HEI ACTIVE</h2>
  <p>Local SSOT: <b>C:\\QSLC\\SSOT</b></p>
  <p>Vault: <b>C:\\QSLC_VAULT</b></p>
  <p class="gold">Control mode: local-first, cloud-assisted only when you explicitly connect it.</p>
</div>
""", unsafe_allow_html=True)
    st.markdown("### Generated files")
    st.write(f"Paychex CSV: `{PAYCHEX_EXPORT}`")
    st.write(f"Timecard report: `{REPORT_HTML}`")

with tabs[3]:
    st.markdown("## Security lock")
    st.error("Any API key already pasted into chat or committed to GitHub must be treated as compromised and rotated.")
    st.markdown("**Rules locked into this repo:**")
    st.markdown("- No plaintext API keys in source code")
    st.markdown("- `.env` stays local only")
    st.markdown("- Streamlit secrets stay in Streamlit Cloud settings")
    st.markdown("- Passwords stay in Apple Passwords / password manager")
    st.markdown("- The local encrypted vault is for backups, not raw public commits")

with tabs[4]:
    st.markdown("## iPhone → ROG control")
    st.markdown("Use one of these two lanes:")
    st.markdown("**Lane A: local only** — open ROGLEX, double-click EVE ONE BUTTON, run `eve help`.")
    st.markdown("**Lane B: mobile SSH** — enable OpenSSH on the ROG and connect from an iPhone SSH app.")
    st.code("powershell -ExecutionPolicy Bypass -File C:\\QSLC\\Agent\\OPTIONAL_enable_iphone_ssh.ps1", language="powershell")

st.markdown("---")
st.caption("QSLC EVE consolidated from previous dashboard prototypes into one safe GitHub/Streamlit control lane.")
