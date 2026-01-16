# How to Launch NIST CSF Tracker

## Quick Start

### Option 1: PowerShell Script (Recommended)
```powershell
.\start.ps1
```
- Opens two PowerShell windows (backend + frontend)
- Automatically opens browser when ready
- Color-coded status messages

### Option 2: Batch File
```cmd
start.bat
```
- Opens two command prompt windows
- Simple and compatible with all Windows versions

## What Gets Started

1. **Backend Server** (Port 8000)
   - FastAPI application
   - Uvicorn with auto-reload
   - SQLite database
   - API at http://localhost:8000
   - API docs at http://localhost:8000/docs

2. **Frontend Server** (Port 5173)
   - React + Vite dev server
   - Hot module replacement
   - UI at http://localhost:5173

## Manual Launch (if scripts don't work)

### Backend
```powershell
cd c:\nist-csf-tracker\backend
.\venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --port 8000
```

### Frontend (in separate terminal)
```powershell
cd c:\nist-csf-tracker\frontend
npm run dev
```

## Stopping the Servers

- Close both PowerShell/CMD windows, OR
- Press `Ctrl+C` in each window

## Troubleshooting

### Port Already in Use
If you get "port already in use" errors:

**Check what's using the ports:**
```powershell
# Check port 8000 (backend)
netstat -ano | findstr :8000

# Check port 5173 (frontend)
netstat -ano | findstr :5173
```

**Kill the processes:**
```powershell
# Kill by PID (get PID from netstat output)
taskkill /PID <PID> /F

# Or kill all node/python processes
Get-Process | Where-Object {$_.ProcessName -like "*node*"} | Stop-Process -Force
Get-Process | Where-Object {$_.ProcessName -like "*python*"} | Stop-Process -Force
```

### Backend Won't Start
- Make sure virtual environment exists: `c:\nist-csf-tracker\backend\venv`
- Reinstall dependencies: `cd backend; .\venv\Scripts\Activate.ps1; pip install -r requirements.txt`
- Check Python version: `python --version` (should be 3.10+)

### Frontend Won't Start
- Make sure node_modules exists: `cd frontend; npm install`
- Check Node version: `node --version` (should be 16+)
- Clear npm cache: `npm cache clean --force`

### Database Issues
- Database file: `c:\nist-csf-tracker\data\nist_csf_tracker.db`
- Reinitialize: `cd backend; .\venv\Scripts\python.exe -m app.init_db`
- Reseed controls: `cd backend; .\venv\Scripts\python.exe -m app.seed_controls_full`

## First Time Setup

If this is your first time running the application:

1. **Install Backend Dependencies:**
   ```powershell
   cd c:\nist-csf-tracker\backend
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

2. **Install Frontend Dependencies:**
   ```powershell
   cd c:\nist-csf-tracker\frontend
   npm install
   ```

3. **Initialize Database:**
   ```powershell
   cd c:\nist-csf-tracker\backend
   .\venv\Scripts\python.exe -m app.init_db
   .\venv\Scripts\python.exe -m app.seed_controls_full
   ```

4. **Run the launcher:**
   ```powershell
   cd c:\nist-csf-tracker
   .\start.ps1
   ```

## URLs After Launch

- **Frontend UI:** http://localhost:5173
- **Backend API:** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs (Swagger UI)
- **Health Check:** http://localhost:8000/health

## Development Notes

- Backend uses auto-reload (changes trigger restart)
- Frontend uses HMR (hot module replacement)
- Database is SQLite (file-based, no server needed)
- All data stored in `c:\nist-csf-tracker\data\`
