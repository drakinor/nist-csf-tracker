@echo off
echo Starting NIST CSF Tracker...
echo.

REM Start Backend Server
echo [1/2] Starting Backend Server (port 8000)...
start "NIST CSF Backend" cmd /k "cd /d c:\nist-csf-tracker\backend && venv\Scripts\activate && uvicorn app.main:app --reload --port 8000"

REM Wait a moment for backend to initialize
timeout /t 3 /nobreak >nul

REM Start Frontend Server
echo [2/2] Starting Frontend Server (port 5173)...
start "NIST CSF Frontend" cmd /k "cd /d c:\nist-csf-tracker\frontend && npm run dev"

echo.
echo ====================================
echo   NIST CSF Tracker Started!
echo ====================================
echo.
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:5173
echo API Docs: http://localhost:8000/docs
echo.
echo Two terminal windows have been opened.
echo Press any key to exit this launcher...
pause >nul
