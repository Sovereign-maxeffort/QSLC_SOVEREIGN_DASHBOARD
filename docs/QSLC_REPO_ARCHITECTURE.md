# QSLC Repository Architecture

This document locks the working structure so the dashboard, SSOT, agents, and products stop drifting across random folders and repos.

## Active command repo

`Sovereign-maxeffort/QSLC_SOVEREIGN_DASHBOARD`

This repo is the current launch point because it already contains the Streamlit dashboard.

Run locally:

```powershell
cd C:\QSLC\QSLC_SOVEREIGN_DASHBOARD
python -m streamlit run .\streamlit_app.py --server.port 8502 --server.address 127.0.0.1
```

One-command local installer:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\INSTALL_ROGLEX_EVE.ps1
```

## Three-repo operating model

### 1. QSLC_SOVEREIGN_CORE

Purpose: infrastructure, SSOT, automations, agents, and backend services.

Target folders:

```text
/infrastructure
  /cloudflare
  /azure
  /bigquery
  /workers
  /pipelines
/data
  /ssot
  /ledger
  /schemas
/agents
  /terminal
  /gateway
  /sync
/automations
  /power_automate
  /monday
  /cloudflare
/security
  env.example
  secrets-template.md
/docs
  architecture.md
  deployment.md
  integrations.md
```

### 2. QSLC_SOVEREIGN_DASHBOARD

Purpose: CEO dashboard, Streamlit runtime, live metrics, Paychex export, legal/task/patent trackers.

Current folders:

```text
/app
/dashboard
/data
/docs
/pages
/scripts
/services
```

The live app reads local files from:

```text
C:\QSLC\SSOT\real_time_log.csv
C:\QSLC\SSOT\paychex_export.csv
C:\QSLC\SSOT\tasks.csv
C:\QSLC\SSOT\ledger.csv
C:\QSLC\SSOT\eve_metrics.json
```

### 3. QSLC_PRODUCTS

Purpose: sellable product kits, agent packages, workflow templates, client deliverables.

Target folders:

```text
/agents
  /notetaker
  /workflow_engine
  /terminal_agent
/workflows
  /monday_mcp
  /power_automate
  /copilot
/templates
  /client_sop
  /onboarding
  /automations
/deliverables
  /client_packages
  /documentation
/docs
  product_catalog.md
  pricing.md
```

## Repo triage

### Keep active

- `Sovereign-maxeffort/QSLC_SOVEREIGN_DASHBOARD`
- `QSLC/QSLC_SSOT`
- `QSLC/Sovereign-QSLC_SSOT`
- `Sovereign-maxeffort/llama3.2` if used for private model experiments

### Archive candidates

- `Sovereign-maxeffort/vscode-mssql`
- `Sovereign-maxeffort/login`
- `Sovereign-maxeffort/turbo-console-log`
- `Sovereign-maxeffort/codex-relay`
- `Sovereign-maxeffort/vite-react-template`
- `Sovereign-maxeffort/gdp-dashboard`

Do not delete until checked for useful code. Archive first.

## Dashboard truth rules

1. Live operational truth comes from `C:\QSLC\SSOT`.
2. GitHub stores code, templates, docs, and safe configuration examples.
3. API keys never go in GitHub, chat, Make, monday, or Streamlit source files.
4. Crypto seed phrases never go into any agent or automation.
5. The EVE Coverage Index is a private/proprietary metric in `eve_metrics.json`; public NASA metrics are shown separately.
6. No open task should go untouched for more than 24 hours.

## Make / monday agent prompt

Use this prompt inside a Make.com or monday.com agent when connecting to QSLC dashboard data:

```text
You are the QSLC EVE operations agent. Your job is to keep all QSLC tasks, dashboard metrics, patent readiness, Paychex exports, and daily content updates synchronized from the SSOT. Do not expose secrets, API keys, crypto seed phrases, or private formulas. Every run must check open tasks older than 24 hours, flag overdue items, update the dashboard status, and generate a short executive summary for Antwan. Use C:\QSLC\SSOT as the local truth source and the GitHub dashboard repo as the code source. If a task is missing owner, due date, priority, or status, mark it as NEEDS_DATA instead of guessing. If funds allocated to patent filing reach the target, create a patent-readiness alert and require human review before payment or filing.
```
