# EcoStream AI Forecasting Service Startup Script
# Automatically checks Python, activates virtual environment, installs dependencies, and starts the service

Write-Host "Starting EcoStream AI Forecasting Service..." -ForegroundColor Cyan

# Check if Python is installed
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python 3.9+ from https://www.python.org/downloads/" -ForegroundColor Yellow
    exit 1
}
Write-Host "Found: $pythonVersion" -ForegroundColor Green

# Navigate to service directory
$serviceDir = Join-Path $PSScriptRoot "services\ai-forecasting-python"
if (-not (Test-Path $serviceDir)) {
    Write-Host "Error: Service directory not found at $serviceDir" -ForegroundColor Red
    exit 1
}
Set-Location $serviceDir

# Check for virtual environment
$venvPath = Join-Path $serviceDir ".venv"
if (-not (Test-Path $venvPath)) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv .venv
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Error: Failed to create virtual environment" -ForegroundColor Red
        exit 1
    }
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& "$venvPath\Scripts\Activate.ps1"
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Failed to activate virtual environment" -ForegroundColor Red
    exit 1
}

# Install/upgrade dependencies
Write-Host "Installing dependencies..." -ForegroundColor Yellow

# Try to upgrade pip (non-blocking - continue even if it fails)
Write-Host "Upgrading pip (if needed)..." -ForegroundColor Gray
pip install --upgrade pip 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Warning: Could not upgrade pip (this is usually okay)" -ForegroundColor Yellow
}

# Install project dependencies (this is critical)
Write-Host "Installing project dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Failed to install dependencies from requirements.txt" -ForegroundColor Red
    exit 1
}
Write-Host "Dependencies installed successfully!" -ForegroundColor Green

# Start the service
Write-Host "Starting AI Forecasting Service on port 5000..." -ForegroundColor Green
Write-Host "Press Ctrl+C to stop the service" -ForegroundColor Yellow
uvicorn app.main:app --host 0.0.0.0 --port 5000 --reload
