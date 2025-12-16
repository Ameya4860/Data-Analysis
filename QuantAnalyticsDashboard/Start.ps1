<#
.SYNOPSIS
    Master launcher for the Quant Analytics Dashboard.
.DESCRIPTION
    Sets up environment, installs dependencies, starts ingestion, analytics, and frontend services.
    Handles graceful shutdown.
#>

$ErrorActionPreference = "Stop"

function Check-Python {
    try {
        $version = python --version 2>&1
        Write-Host "Found Python: $version" -ForegroundColor Green
    } catch {
        Write-Error "Python not found! Please install Python 3.9+."
    }
}

function Install-Deps {
    Write-Host "Installing dependencies..." -ForegroundColor Cyan
    pip install -r requirements.txt
}

function Stop-Processes {
    param($Pids)
    Write-Host "`nStopping services..." -ForegroundColor Yellow
    foreach ($p in $Pids) {
        if ($p) {
            try {
                Stop-Process -Id $p -Force -ErrorAction SilentlyContinue
                Write-Host "Stopped process $p" -ForegroundColor Gray
            } catch {
                # Process might have already exited
            }
        }
    }
}

# --- Main Execution ---

Write-Host "=== Quant Analytics Dashboard Launcher ===" -ForegroundColor Magenta

# 1. Setup
Check-Python
Install-Deps

# 2. Infrastructure
# Create data dir if not exists (Handled by python scripts but good to be sure)
if (-not (Test-Path "data")) { New-Item -ItemType Directory -Path "data" | Out-Null }
if (-not (Test-Path "logs")) { New-Item -ItemType Directory -Path "logs" | Out-Null }

$running_pids = @()

try {
    # 3. Start Data Pipeline (Ingestion)
    Write-Host "Starting Ingestion Service..." -ForegroundColor Cyan
    $ingestion = Start-Process python -ArgumentList "src/ingestion/binance_client.py" -PassThru -WindowStyle Minimized
    $running_pids += $ingestion.Id
    Write-Host "Ingestion Service started (PID: $($ingestion.Id))" -ForegroundColor Green

    # 4. Start Resampling Engine
    Write-Host "Starting Resampling Engine..." -ForegroundColor Cyan
    $resampler = Start-Process python -ArgumentList "src/analytics/core/resampler.py" -PassThru -WindowStyle Minimized
    $running_pids += $resampler.Id
    Write-Host "Resampling Engine started (PID: $($resampler.Id))" -ForegroundColor Green

    # 5. Start Frontend (Streamlit)
    Write-Host "Starting Streamlit Dashboard..." -ForegroundColor Cyan
    # Streamlit opens browser automatically
    $frontend = Start-Process streamlit -ArgumentList "run src/frontend/app.py" -PassThru
    $running_pids += $frontend.Id
    Write-Host "Dashboard started (PID: $($frontend.Id))" -ForegroundColor Green
    Write-Host "System is running. Press Ctrl+C in this window to stop all services." -ForegroundColor White

    # Monitor loop
    while ($true) {
        Start-Sleep -Seconds 1
        # Check if frontend is still alive, if not, exit
        if (-not (Get-Process -Id $frontend.Id -ErrorAction SilentlyContinue)) {
            Write-Host "Dashboard closed. Shutting down system."
            break
        }
    }

} catch {
    Write-Error "An error occurred: $_"
} finally {
    Stop-Processes -Pids $running_pids
    Write-Host "Shutdown complete." -ForegroundColor Magenta
}
