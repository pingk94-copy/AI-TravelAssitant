param(
    [int]$BackendPort = 8000,
    [int]$FrontendPort = 5173
)

$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$BackendDir = Join-Path $Root "backend"
$FrontendDir = Join-Path $Root "frontend"
$PythonExe = Join-Path $Root ".venv\Scripts\python.exe"

function Stop-PortProcess {
    param([int]$Port)

    $connections = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue
    $processIds = $connections | Select-Object -ExpandProperty OwningProcess -Unique

    foreach ($processId in $processIds) {
        if ($processId -and $processId -ne 0) {
            $process = Get-Process -Id $processId -ErrorAction SilentlyContinue
            if ($process) {
                Write-Host "Stopping process $($process.ProcessName) (PID $processId) on port $Port..."
                Stop-Process -Id $processId -Force
            }
        }
    }
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

Write-Host "Cleaning old dev-server ports..."
Stop-PortProcess -Port $BackendPort
Stop-PortProcess -Port $FrontendPort

Start-Sleep -Seconds 1

Write-Host "Starting backend on http://127.0.0.1:$BackendPort ..."
$backendPath = $BackendDir.Replace("'", "''")
$pythonPath = $PythonExe.Replace("'", "''")
$backendCommand = "Set-Location -LiteralPath '$backendPath'; & '$pythonPath' -m uvicorn app.main:app --host 127.0.0.1 --port $BackendPort"
Start-Process powershell.exe -ArgumentList @("-NoExit", "-Command", $backendCommand) -WorkingDirectory $BackendDir

Write-Host "Starting frontend on http://127.0.0.1:$FrontendPort ..."
$frontendPath = $FrontendDir.Replace("'", "''")
$frontendCommand = "Set-Location -LiteralPath '$frontendPath'; npm run dev"
Start-Process powershell.exe -ArgumentList @("-NoExit", "-Command", $frontendCommand) -WorkingDirectory $FrontendDir

Write-Host ""
Write-Host "Project is starting. Open http://127.0.0.1:$FrontendPort"
