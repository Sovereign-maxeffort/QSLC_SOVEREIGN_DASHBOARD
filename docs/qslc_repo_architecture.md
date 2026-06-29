# QSLC Sovereign Repo Architecture

## Purpose
This document locks the clean operating structure for QSLC so the dashboard, SSOT, products, and agent workflows stop drifting across random repositories.

## Active repositories

### 1. QSLC_SOVEREIGN_CORE
Core business brain and infrastructure.

Recommended folders:

```text
infrastructure/
  cloudflare/
  azure/
  bigquery/
  workers/
  pipelines/
data/
  ssot/
  ledger/
  schemas/
agents/
  terminal/
  gateway/
  sync/
automations/
  power_automate/
  monday/
  cloudflare/
security/
  env.example
  secrets-template.md
docs/
  architecture.md
  deployment.md
  integrations.md
```

### 2. QSLC_SOVEREIGN_DASHBOARD
Live CEO dashboard and Streamlit app.

Current repository: `Sovereign-maxeffort/QSLC_SOVEREIGN_DASHBOARD`

Recommended folders:

```text
app/
  streamlit_app.py
  components/
  styles/
dashboard/
  finance/
  operations/
  legal/
  metrics/
  agents/
data/
  ssot/
  ledger/
  cache/
services/
  bigquery_client.py
  cloudflare_client.py
  azure_ml_client.py
scripts/
  INSTALL_ROGLEX_EVE.ps1
docs/
  dashboard-overview.md
  qslc_repo_architecture.md
```

### 3. QSLC_PRODUCTS
Sellable agents, workflows, templates, and deliverables.

Recommended folders:

```text
agents/
  notetaker/
  workflow_engine/
  terminal_agent/
workflows/
  monday_mcp/
  power_automate/
  copilot/
templates/
  client_sop/
  onboarding/
  automations/
deliverables/
  client_packages/
  documentation/
docs/
  product_catalog.md
  pricing.md
```

## Repos to archive or ignore
These should not be treated as QSLC operating assets unless intentionally promoted:

- `vscode-mssql`
- `login`
- `turbo-console-log`
- `codex-relay`
- `vite-react-template`
- `gdp-dashboard`
- `llama3.2` unless moved into QSLC_PRODUCTS as a model experiment

## Live dashboard source of truth
The Streamlit app reads local SSOT data from:

```text
C:\QSLC\SSOT\real_time_log.csv
C:\QSLC\SSOT\paychex_export.csv
C:\QSLC\Reports\timecard_report_latest.html
C:\QSLC_VAULT
```

The local run command is:

```powershell
streamlit run streamlit_app.py --server.port 8502
```

## Security rules

- No plaintext API keys in GitHub.
- `.env` stays local only.
- Streamlit secrets stay in Streamlit Cloud settings.
- Wallet seed phrases never go into any agent, repo, dashboard, or chat.
- Any key pasted into chat or committed to GitHub must be rotated.

## Status
Architecture plan added. Repo creation, repo archiving, Azure billing cancellation, Monday board editing, and Microsoft 365 admin actions require the matching enabled connector or direct account access.
