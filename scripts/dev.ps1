# NIST CSF Tracker - Development Startup Script
# This script starts both backend and frontend in development mode

Write-Host "================================" -ForegroundColor Cyan
Write-Host "NIST CSF Tracker - Starting..." -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

$ErrorActionPreference = "Stop"

# Check prerequisites
Write-Host "Checking prerequisites..." -ForegroundColor Yellow

# Check Python
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Python not found. Please install Python 3.11 or later." -ForegroundColor Red
    exit 1
}

# Check Node.js
try {
    $nodeVersion = node --version
    Write-Host "✓ Node.js found: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Node.js not found. Please install Node.js 18 or later." -ForegroundColor Red
    exit 1
}

Write-Host ""

# Setup backend if needed
if (-not (Test-Path "backend\venv")) {
    Write-Host "Setting up backend virtual environment..." -ForegroundColor Yellow
    Set-Location backend
    python -m venv venv
    .\venv\Scripts\Activate.ps1
    pip install -r requirements.txt
    Set-Location ..
    Write-Host "✓ Backend setup complete" -ForegroundColor Green
    Write-Host ""
}

# Copy .env if needed
if (-not (Test-Path "backend\.env")) {
    Write-Host "Creating backend .env file..." -ForegroundColor Yellow
    Copy-Item "backend\.env.example" "backend\.env"
    Write-Host "✓ Created backend\.env" -ForegroundColor Green
    Write-Host ""
}

# Initialize database if needed
if (-not (Test-Path "data\nist_csf_tracker.db")) {
    Write-Host "Initializing database..." -ForegroundColor Yellow
    Set-Location backend
    .\venv\Scripts\Activate.ps1
    python -m app.init_db
    python -m app.seed_controls
    Set-Location ..
    Write-Host "✓ Database initialized and seeded" -ForegroundColor Green
    Write-Host ""
}

# Setup frontend if needed
if (-not (Test-Path "frontend\node_modules")) {
    Write-Host "Installing frontend dependencies..." -ForegroundColor Yellow
    Set-Location frontend
    npm install
    Set-Location ..
    Write-Host "✓ Frontend setup complete" -ForegroundColor Green
    Write-Host ""
}

Write-Host "Starting services..." -ForegroundColor Yellow
Write-Host ""

# Start backend in background
Write-Host "Starting backend on http://localhost:8000 ..." -ForegroundColor Cyan
$backend = Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd backend; .\venv\Scripts\Activate.ps1; uvicorn app.main:app --reload --host 0.0.0.0 --port 8000" -PassThru

# Wait a moment for backend to start
Start-Sleep -Seconds 3

# Start frontend in background
Write-Host "Starting frontend on http://localhost:5173 ..." -ForegroundColor Cyan
$frontend = Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd frontend; npm run dev" -PassThru

Write-Host ""
Write-Host "================================" -ForegroundColor Green
Write-Host "Services are starting!" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Green
Write-Host ""
Write-Host "Backend:  http://localhost:8000" -ForegroundColor Cyan
Write-Host "Frontend: http://localhost:5173" -ForegroundColor Cyan
Write-Host "API Docs: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C in the spawned terminals to stop services" -ForegroundColor Yellow
Write-Host ""

# Keep script alive
Write-Host "Press any key to open browser..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

Start-Process "http://localhost:5173"
