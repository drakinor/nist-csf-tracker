# NIST CSF Tracker - Setup Script
# Run this once to set up the complete development environment

Write-Host "================================" -ForegroundColor Cyan
Write-Host "NIST CSF Tracker - Setup" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

$ErrorActionPreference = "Stop"

# Backend setup
Write-Host "1. Setting up Python backend..." -ForegroundColor Yellow
Set-Location backend

if (-not (Test-Path "venv")) {
    python -m venv venv
}

.\venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt

if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "   Created .env file - please review settings" -ForegroundColor Cyan
}

Write-Host "   ✓ Backend setup complete" -ForegroundColor Green
Set-Location ..
Write-Host ""

# Frontend setup
Write-Host "2. Setting up React frontend..." -ForegroundColor Yellow
Set-Location frontend
npm install
Write-Host "   ✓ Frontend setup complete" -ForegroundColor Green
Set-Location ..
Write-Host ""

# Database setup
Write-Host "3. Initializing database..." -ForegroundColor Yellow
Set-Location backend
.\venv\Scripts\Activate.ps1
python -m app.init_db
Write-Host "   ✓ Database tables created" -ForegroundColor Green
Write-Host ""

Write-Host "4. Seeding NIST CSF controls..." -ForegroundColor Yellow
python -m app.seed_controls
Write-Host "   ✓ Controls seeded" -ForegroundColor Green
Set-Location ..
Write-Host ""

Write-Host "================================" -ForegroundColor Green
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Green
Write-Host ""
Write-Host "To start the application, run:" -ForegroundColor Cyan
Write-Host "   .\scripts\dev.ps1" -ForegroundColor White
Write-Host ""
Write-Host "Or start manually:" -ForegroundColor Cyan
Write-Host "   Backend:  cd backend; .\venv\Scripts\Activate.ps1; uvicorn app.main:app --reload" -ForegroundColor White
Write-Host "   Frontend: cd frontend; npm run dev" -ForegroundColor White
Write-Host ""
