$ErrorActionPreference = "Stop"

function Write-Step($Message) {
  Write-Host "[QSLC] $Message" -ForegroundColor Cyan
}

function Get-PythonCommand {
  $python = Get-Command python -ErrorAction SilentlyContinue
  if ($python) { return "python" }

  $py = Get-Command py -ErrorAction SilentlyContinue
  if ($py) { return "py -3" }

  return $null
}

$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$QslcRoot = "C:\QSLC"
$VaultRoot = "C:\QSLC_VAULT"

Write-Step "Building local folders."
@(
  $QslcRoot,
  "$QslcRoot\SSOT",
  "$QslcRoot\Reports",
  "$QslcRoot\Finance",
  "$QslcRoot\Dashboard",
  $VaultRoot,
  "$VaultRoot\exports",
  "$VaultRoot\reports"
) | ForEach-Object {
  New-Item -ItemType Directory -Path $_ -Force | Out-Null
}

$TimeLog = "$QslcRoot\SSOT\real_time_log.csv"
if (!(Test-Path $TimeLog)) {
  "Start,End,Employee,Hours,Source,Note" | Out-File -FilePath $TimeLog -Encoding utf8
}

Set-Location $Root

$PythonCmd = Get-PythonCommand
if (-not $PythonCmd) {
  Write-Host "[QSLC] Python was not found. Installing Python through winget..." -ForegroundColor Yellow
  $winget = Get-Command winget -ErrorAction SilentlyContinue
  if (-not $winget) {
    Write-Host "[QSLC] winget is not available. Install Python 3 from Microsoft Store or python.org, then rerun this script." -ForegroundColor Red
    exit 1
  }

  winget install --id Python.Python.3.12 -e --source winget --accept-package-agreements --accept-source-agreements

  $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
  $PythonCmd = Get-PythonCommand

  if (-not $PythonCmd) {
    Write-Host "[QSLC] Python installed, but this terminal has not refreshed PATH yet." -ForegroundColor Yellow
    Write-Host "[QSLC] Close PowerShell, reopen it, then rerun this script." -ForegroundColor Yellow
    exit 1
  }
}

Write-Step "Using Python command: $PythonCmd"
Write-Step "Installing dashboard requirements."
Invoke-Expression "$PythonCmd -m pip install --upgrade pip"
Invoke-Expression "$PythonCmd -m pip install -r requirements.txt"

Write-Step "Starting live dashboard on http://localhost:8502"
Invoke-Expression "$PythonCmd -m streamlit run streamlit_app.py --server.port 8502 --server.address 0.0.0.0"
