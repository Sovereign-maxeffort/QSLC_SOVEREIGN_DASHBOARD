$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$QslcRoot = "C:\QSLC"
$VaultRoot = "C:\QSLC_VAULT"

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
python -m pip install -r requirements.txt
python -m streamlit run streamlit_app.py --server.port 8502
