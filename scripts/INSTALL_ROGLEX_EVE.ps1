# QSLC ROGLEX EVE ONE-COMMAND INSTALLER
# Runs local-first. Creates C:\QSLC, installs Streamlit dependencies, creates EVE CLI, launches dashboard on port 8502.
# Run from Windows Terminal / PowerShell:
# powershell -ExecutionPolicy Bypass -File .\scripts\INSTALL_ROGLEX_EVE.ps1

$ErrorActionPreference = "Continue"
$RepoUrl = "https://github.com/Sovereign-maxeffort/QSLC_SOVEREIGN_DASHBOARD.git"
$Root = "C:\QSLC"
$RepoPath = Join-Path $Root "QSLC_SOVEREIGN_DASHBOARD"
$SSOT = Join-Path $Root "SSOT"
$CLI = Join-Path $Root "CLI"
$Reports = Join-Path $Root "Reports"
$Vault = "C:\QSLC_VAULT"
$Port = 8502

function Write-QSLC($msg) { Write-Host "[QSLC] $msg" -ForegroundColor Cyan }
function Write-Good($msg) { Write-Host "[OK] $msg" -ForegroundColor Green }
function Write-Warn2($msg) { Write-Host "[WARN] $msg" -ForegroundColor Yellow }

Write-QSLC "Creating Sovereign root folders..."
New-Item -ItemType Directory -Force -Path $Root, $SSOT, $CLI, $Reports, $Vault, (Join-Path $Vault "exports"), (Join-Path $Vault "reports") | Out-Null

Write-QSLC "Checking Python..."
$pythonCmd = "python"
try {
    & python --version | Out-Host
} catch {
    try {
        & py --version | Out-Host
        $pythonCmd = "py"
    } catch {
        Write-Warn2 "Python was not found. Install Python 3.11+ from https://python.org, then run this script again."
        exit 1
    }
}

Write-QSLC "Checking Git..."
$gitAvailable = $true
try { git --version | Out-Host } catch { $gitAvailable = $false }

if ($gitAvailable) {
    if (!(Test-Path $RepoPath)) {
        Write-QSLC "Cloning dashboard repo into $RepoPath..."
        git clone $RepoUrl $RepoPath
    } else {
        Write-QSLC "Repo exists. Pulling latest updates..."
        Push-Location $RepoPath
        git pull
        Pop-Location
    }
} else {
    Write-Warn2 "Git was not found. Install Git for Windows, or download repo ZIP manually. Continuing with existing folder if present."
}

if (!(Test-Path $RepoPath)) {
    Write-Warn2 "Dashboard repo folder missing: $RepoPath"
    Write-Warn2 "Install Git or download the repo ZIP into C:\QSLC\QSLC_SOVEREIGN_DASHBOARD."
    exit 1
}

Write-QSLC "Installing dashboard requirements..."
Push-Location $RepoPath
if (Test-Path ".\requirements.txt") {
    & $pythonCmd -m pip install --upgrade pip
    & $pythonCmd -m pip install -r .\requirements.txt
} else {
    & $pythonCmd -m pip install --upgrade streamlit pandas
}
Pop-Location

Write-QSLC "Creating default SSOT files if missing..."
$TimeLog = Join-Path $SSOT "real_time_log.csv"
if (!(Test-Path $TimeLog)) {
    "Start,End,Employee,Hours,Source,Note" | Set-Content -Path $TimeLog -Encoding UTF8
}
$Tasks = Join-Path $SSOT "tasks.csv"
if (!(Test-Path $Tasks)) {
    @"
Task,Owner,Status,Priority,UpdatedAt
Rotate exposed API keys,EVE,Open,High,$((Get-Date).ToString("o"))
Review patent fund tracker,CEO,Open,High,$((Get-Date).ToString("o"))
Publish daily dashboard content,EVE,Open,Medium,$((Get-Date).ToString("o"))
"@ | Set-Content -Path $Tasks -Encoding UTF8
}
$Ledger = Join-Path $SSOT "ledger.csv"
if (!(Test-Path $Ledger)) {
    "Date,Category,Description,Amount,Source" | Set-Content -Path $Ledger -Encoding UTF8
}
$Metrics = Join-Path $SSOT "eve_metrics.json"
if (!(Test-Path $Metrics)) {
    @"
{
  "eve_coverage_index_percent": 80,
  "psi_balance": 0,
  "sol_balance": 0,
  "patent_fund_usd": 0,
  "public_message": "Hello. We build with discipline, love, and raw technology. The code knows the way; the team stays humble.",
  "last_updated": "$((Get-Date).ToString("o"))"
}
"@ | Set-Content -Path $Metrics -Encoding UTF8
}

Write-QSLC "Creating EVE PowerShell CLI at C:\QSLC\CLI\eve.ps1..."
$EveCli = Join-Path $CLI "eve.ps1"
@'
param(
    [string]$Command = "help"
)

$Root = "C:\QSLC"
$SSOT = Join-Path $Root "SSOT"
$TimeLog = Join-Path $SSOT "real_time_log.csv"
$Paychex = Join-Path $SSOT "paychex_export.csv"
$Session = Join-Path $SSOT "current_session.json"
$Rate = 75

New-Item -ItemType Directory -Force -Path $SSOT | Out-Null
if (!(Test-Path $TimeLog)) { "Start,End,Employee,Hours,Source,Note" | Set-Content -Path $TimeLog -Encoding UTF8 }

switch ($Command.ToLower()) {
    "start" {
        $now = Get-Date
        @{ start = $now.ToString("o"); employee = "WHITE ANTWAN" } | ConvertTo-Json | Set-Content $Session -Encoding UTF8
        Write-Host "EVE session started: $($now.ToString("s"))"
    }
    "stop" {
        if (!(Test-Path $Session)) { Write-Host "No active session found. Run: eve start"; exit 1 }
        $s = Get-Content $Session | ConvertFrom-Json
        $start = [datetime]$s.start
        $end = Get-Date
        $hours = [math]::Round(($end - $start).TotalHours, 2)
        $line = '"{0}","{1}","WHITE ANTWAN",{2},"EVE","local session"' -f $start.ToString("o"), $end.ToString("o"), $hours
        Add-Content -Path $TimeLog -Value $line
        Remove-Item $Session -Force
        Write-Host "EVE session stopped. Hours logged: $hours"
    }
    "export" {
        $rows = Import-Csv $TimeLog
        $out = foreach ($r in $rows) {
            $h = [double]($r.Hours)
            [PSCustomObject]@{
                Date = ([datetime]$r.Start).ToString("yyyy-MM-dd")
                Employee = $r.Employee
                Hours = $h
                Rate = $Rate
                Gross = [math]::Round($h * $Rate, 2)
                Source = $r.Source
            }
        }
        $out | Export-Csv -Path $Paychex -NoTypeInformation
        Write-Host "Paychex export created: $Paychex"
    }
    "pdf" {
        Write-Host "Report generation placeholder. Dashboard report path: C:\QSLC\Reports\timecard_report_latest.html"
    }
    "print" {
        Write-Host "Print placeholder. Export first, then print the report from dashboard."
    }
    "diagnose" {
        Write-Host "Root: $Root"
        Write-Host "SSOT exists: $(Test-Path $SSOT)"
        Write-Host "Time log exists: $(Test-Path $TimeLog)"
        Write-Host "Python:"
        python --version
        Write-Host "Streamlit:"
        python -m streamlit --version
    }
    default {
        Write-Host "EVE CLI commands: start | stop | export | pdf | print | diagnose"
    }
}
'@ | Set-Content -Path $EveCli -Encoding UTF8

Write-QSLC "Adding current PowerShell session alias: eve"
Set-Alias eve $EveCli

Write-QSLC "Releasing dashboard port $Port if an old Streamlit session is stuck..."
try {
    $listeners = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
    foreach ($l in $listeners) {
        $pidToKill = $l.OwningProcess
        if ($pidToKill -and $pidToKill -ne $PID) {
            Stop-Process -Id $pidToKill -Force -ErrorAction SilentlyContinue
            Write-Warn2 "Killed old listener on port $Port PID $pidToKill"
        }
    }
} catch { }

Write-Good "QSLC local structure ready."
Write-Good "Dashboard repo: $RepoPath"
Write-Good "SSOT live data: $SSOT"
Write-Good "EVE CLI: $EveCli"

Write-QSLC "Launching Streamlit dashboard on http://localhost:$Port ..."
Push-Location $RepoPath
& $pythonCmd -m streamlit run .\streamlit_app.py --server.port $Port --server.address 127.0.0.1
Pop-Location
