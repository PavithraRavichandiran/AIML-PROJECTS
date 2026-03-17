$ErrorActionPreference = 'Stop'

$workspace = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$pythonExe = Join-Path $workspace '.venv\Scripts\python.exe'
$refreshScript = Join-Path $workspace 'scripts\refresh_kpis.py'
$taskName = 'AmazonIndia_KPI_Refresh_Nightly'
$startTime = '02:00'

if (-not (Test-Path $pythonExe)) {
    throw "Python executable not found at: $pythonExe"
}

if (-not (Test-Path $refreshScript)) {
    throw "Refresh script not found at: $refreshScript"
}

$taskCmd = '"' + $pythonExe + '" "' + $refreshScript + '"'

Write-Host "Creating/updating scheduled task: $taskName"
Write-Host "Command: $taskCmd"
Write-Host "Schedule: Daily at $startTime"

schtasks /Create /TN $taskName /SC DAILY /ST $startTime /TR $taskCmd /F | Out-Host

Write-Host "`nTask created/updated. Current task details:`n"
schtasks /Query /TN $taskName /V /FO LIST | Out-Host
