param(
    [int]$BackendPort = 8000,
    [int]$FrontendPort = 5173,
    [switch]$Quiet
)

$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$BackendDir = Join-Path $Root "backend"
$FrontendDir = Join-Path $Root "frontend"
$LogDir = Join-Path $Root "logs"
$PythonExe = Join-Path $Root ".venv\Scripts\python.exe"
$FrontendUrl = "http://127.0.0.1:$FrontendPort"
$BackendHealthUrl = "http://127.0.0.1:$BackendPort/api/health"
$QuietMode = [bool]$Quiet

function Write-Status {
    param([string]$Message)

    if (-not $QuietMode) {
        Write-Host $Message
    }
}

function Stop-PortProcess {
    param([int]$Port)

    $processIds = @()
    $lines = & netstat.exe -ano -p tcp | Select-String -Pattern "^\s*TCP\s+\S+:$Port\s+"
    foreach ($line in $lines) {
        $parts = ($line.Line -split "\s+") | Where-Object { $_ }
        if ($parts.Length -ge 5 -and $parts[3] -eq "LISTENING") {
            $processIds += [int]$parts[4]
        }
    }
    $processIds = $processIds | Select-Object -Unique

    foreach ($processId in $processIds) {
        if ($processId -and $processId -ne 0) {
            Write-Status "Stopping old process on port $Port : PID $processId"
            Stop-Process -Id $processId -Force -ErrorAction SilentlyContinue
            Wait-Process -Id $processId -Timeout 5 -ErrorAction SilentlyContinue
        }
    }
}

function Wait-HttpReady {
    param(
        [string]$Url,
        [int]$TimeoutSeconds = 40
    )

    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    while ((Get-Date) -lt $deadline) {
        try {
            Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 2 | Out-Null
            return $true
        }
        catch {
            Start-Sleep -Milliseconds 700
        }
    }
    return $false
}

if (-not (Test-Path $BackendDir)) {
    throw "Backend directory not found: $BackendDir"
}

if (-not (Test-Path $FrontendDir)) {
    throw "Frontend directory not found: $FrontendDir"
}

if (-not (Test-Path $PythonExe)) {
    $PythonExe = "python"
}

New-Item -ItemType Directory -Force -Path $LogDir | Out-Null

Write-Status "Starting AI Travel Assistant..."
Write-Status "Project root: $Root"
Write-Status "Backend port: $BackendPort"
Write-Status "Frontend port: $FrontendPort"

Stop-PortProcess -Port $BackendPort
Stop-PortProcess -Port $FrontendPort
Start-Sleep -Seconds 1

$runStamp = Get-Date -Format "yyyyMMdd-HHmmss"
$backendOutLog = Join-Path $LogDir "backend-$runStamp.out.log"
$backendErrLog = Join-Path $LogDir "backend-$runStamp.err.log"
$frontendOutLog = Join-Path $LogDir "frontend-$runStamp.out.log"
$frontendErrLog = Join-Path $LogDir "frontend-$runStamp.err.log"

Write-Status "Starting backend FastAPI..."
$backendProcess = Start-Process -FilePath $PythonExe `
    -ArgumentList @("-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "$BackendPort") `
    -WorkingDirectory $BackendDir `
    -WindowStyle Hidden `
    -RedirectStandardOutput $backendOutLog `
    -RedirectStandardError $backendErrLog `
    -PassThru

Write-Status "Starting frontend Vite..."
$frontendProcess = Start-Process -FilePath "npm.cmd" `
    -ArgumentList @("run", "dev") `
    -WorkingDirectory $FrontendDir `
    -WindowStyle Hidden `
    -RedirectStandardOutput $frontendOutLog `
    -RedirectStandardError $frontendErrLog `
    -PassThru

Write-Status "Waiting for backend health: $BackendHealthUrl"
$backendReady = Wait-HttpReady -Url $BackendHealthUrl -TimeoutSeconds 45

Write-Status "Waiting for frontend page: $FrontendUrl"
$frontendReady = Wait-HttpReady -Url $FrontendUrl -TimeoutSeconds 45

if ($backendReady -and $frontendReady) {
    Write-Status "Startup complete. Opening browser: $FrontendUrl"
    Start-Process $FrontendUrl
    if (-not $QuietMode) {
        Write-Host ""
        Write-Host "Backend PID: $($backendProcess.Id)"
        Write-Host "Frontend PID: $($frontendProcess.Id)"
        Write-Host "Backend health: $BackendHealthUrl"
        Write-Host "Logs: $LogDir"
    }
}
else {
    Write-Host ""
    Write-Host "Startup incomplete. Please check the status below:"
    Write-Host "Backend: $(if ($backendReady) { 'ready' } else { 'health check failed' })"
    Write-Host "Frontend: $(if ($frontendReady) { 'ready' } else { 'page check failed' })"
    Write-Host "Backend stdout: $backendOutLog"
    Write-Host "Backend stderr: $backendErrLog"
    Write-Host "Frontend stdout: $frontendOutLog"
    Write-Host "Frontend stderr: $frontendErrLog"
    exit 1
}
