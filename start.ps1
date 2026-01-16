# NIST CSF Tracker Launcher
# PowerShell version for better Windows compatibility

Write-Host "`n╔══════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║   NIST CSF Tracker - Starting Services...  ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════╝`n" -ForegroundColor Cyan

# Start Backend Server
Write-Host "[1/2] Starting Backend Server (port 8000)..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd c:\nist-csf-tracker\backend; .\venv\Scripts\Activate.ps1; Write-Host 'Backend Starting...' -ForegroundColor Green; uvicorn app.main:app --reload --port 8000"

# Wait for backend to initialize
Start-Sleep -Seconds 3

# Start Frontend Server
Write-Host "[2/2] Starting Frontend Server (port 5173)..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd c:\nist-csf-tracker\frontend; Write-Host 'Frontend Starting...' -ForegroundColor Green; npm run dev"

# Wait a moment then check if servers are running
Start-Sleep -Seconds 5

Write-Host "`n╔══════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║        NIST CSF Tracker Started! ✓          ║" -ForegroundColor Green
Write-Host "╚══════════════════════════════════════════════╝" -ForegroundColor Green

Write-Host "`n📍 Service URLs:" -ForegroundColor Cyan
Write-Host "   Backend API:  " -NoNewline -ForegroundColor White
Write-Host "http://localhost:8000" -ForegroundColor Yellow
Write-Host "   Frontend UI:  " -NoNewline -ForegroundColor White
Write-Host "http://localhost:5173" -ForegroundColor Yellow
Write-Host "   API Docs:     " -NoNewline -ForegroundColor White
Write-Host "http://localhost:8000/docs" -ForegroundColor Yellow

Write-Host "`n💡 Two PowerShell windows opened:" -ForegroundColor Cyan
Write-Host "   • Backend server (FastAPI + Uvicorn)" -ForegroundColor White
Write-Host "   • Frontend server (Vite + React)" -ForegroundColor White

Write-Host "`n⚠️  To stop: Close both PowerShell windows or press Ctrl+C in each" -ForegroundColor Yellow
Write-Host ""

# Try to open browser after a delay
Start-Sleep -Seconds 3
try {
    $response = Invoke-WebRequest -Uri "http://localhost:5173" -UseBasicParsing -TimeoutSec 2 -ErrorAction Stop
    Write-Host "✓ Opening browser..." -ForegroundColor Green
    Start-Process "http://localhost:5173"
} catch {
    Write-Host "⚠️  Frontend still starting up. Open http://localhost:5173 manually in a moment." -ForegroundColor Yellow
}

Write-Host "`nPress any key to close this launcher..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
