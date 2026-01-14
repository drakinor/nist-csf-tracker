# NIST CSF Tracker - Quick Reference

## 🚀 Quick Start Commands

### First Time Setup
```powershell
.\scripts\setup.ps1
```

### Start Development Environment
```powershell
.\scripts\dev.ps1
```

### Access Application
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

---

## 🔧 Manual Commands

### Backend

**Activate virtual environment:**
```powershell
cd backend
.\venv\Scripts\Activate.ps1
```

**Install dependencies:**
```powershell
pip install -r requirements.txt
```

**Initialize database:**
```powershell
python -m app.init_db
```

**Seed controls:**
```powershell
python -m app.seed_controls
```

**Start server:**
```powershell
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Start with debug logging:**
```powershell
uvicorn app.main:app --reload --log-level debug
```

### Frontend

**Install dependencies:**
```powershell
cd frontend
npm install
```

**Start dev server:**
```powershell
npm run dev
```

**Build for production:**
```powershell
npm run build
```

**Preview production build:**
```powershell
npm run preview
```

---

## 🗄️ Database Commands

**Open database:**
```powershell
cd data
sqlite3 nist_csf_tracker.db
```

**Common SQL queries:**
```sql
-- List all tables
.tables

-- View controls
SELECT csf_id, name, function FROM controls;

-- View artifacts
SELECT id, title, type, collected_at FROM artifacts;

-- View accepted evidence
SELECT e.id, c.csf_id, e.evidence_type, e.status 
FROM evidence e 
JOIN controls c ON e.control_id = c.id 
WHERE e.status = 'accepted';

-- View scores
SELECT c.csf_id, s.score_value, s.score_label 
FROM scores s 
JOIN controls c ON s.control_id = c.id;

-- View score events (audit trail)
SELECT c.csf_id, se.old_score, se.new_score, se.timestamp 
FROM score_events se 
JOIN controls c ON se.control_id = c.id 
ORDER BY se.timestamp DESC;

-- Count chunks per artifact
SELECT a.title, COUNT(ac.id) as chunk_count 
FROM artifacts a 
LEFT JOIN artifact_chunks ac ON a.id = ac.artifact_id 
GROUP BY a.id;

-- Exit
.quit
```

---

## 📦 Dependency Management

### Backend

**Add new package:**
```powershell
cd backend
.\venv\Scripts\Activate.ps1
pip install package-name
pip freeze > requirements.txt
```

**Update all packages:**
```powershell
pip install --upgrade -r requirements.txt
```

### Frontend

**Add new package:**
```powershell
cd frontend
npm install package-name
```

**Update all packages:**
```powershell
npm update
```

---

## 🧹 Cleanup Commands

**Reset database (WARNING: deletes all data):**
```powershell
Remove-Item data\nist_csf_tracker.db
cd backend
.\venv\Scripts\Activate.ps1
python -m app.init_db
python -m app.seed_controls
```

**Clear artifacts (WARNING: deletes all uploaded files):**
```powershell
Remove-Item data\artifacts\* -Exclude .gitkeep
```

**Reset backend environment:**
```powershell
Remove-Item -Recurse -Force backend\venv
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

**Reset frontend:**
```powershell
Remove-Item -Recurse -Force frontend\node_modules
cd frontend
npm install
```

---

## 🐛 Troubleshooting Commands

**Check Python version:**
```powershell
python --version
```

**Check Node version:**
```powershell
node --version
npm --version
```

**Kill processes on ports:**
```powershell
# Kill process on port 8000 (backend)
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Kill process on port 5173 (frontend)
netstat -ano | findstr :5173
taskkill /PID <PID> /F
```

**Check if services are running:**
```powershell
# Backend
Invoke-WebRequest http://localhost:8000/health

# Frontend
Invoke-WebRequest http://localhost:5173
```

**View backend logs:**
```powershell
cd backend
.\venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --access-log --log-level info
```

---

## 📊 Testing Commands

**Test artifact upload:**
```powershell
# Using curl (if installed)
curl -X POST http://localhost:8000/api/artifacts/upload `
  -F "file=@path\to\document.pdf" `
  -F "tags=test,policy"
```

**Test API endpoints:**
```powershell
# List controls
Invoke-RestMethod -Uri http://localhost:8000/api/controls/

# Get control
Invoke-RestMethod -Uri http://localhost:8000/api/controls/1

# Get candidates
Invoke-RestMethod -Uri http://localhost:8000/api/controls/1/candidates

# Dashboard
Invoke-RestMethod -Uri http://localhost:8000/api/scores/dashboard
```

---

## 🔍 Inspection Commands

**View database schema:**
```powershell
cd data
sqlite3 nist_csf_tracker.db ".schema controls"
```

**Export data:**
```powershell
# Export controls to CSV
sqlite3 data\nist_csf_tracker.db -csv -header "SELECT * FROM controls" > controls.csv

# Export evidence to CSV
sqlite3 data\nist_csf_tracker.db -csv -header "SELECT * FROM evidence" > evidence.csv
```

**Check artifact files:**
```powershell
Get-ChildItem data\artifacts | Format-Table Name, Length, LastWriteTime
```

**View environment variables:**
```powershell
Get-Content backend\.env
```

---

## 📝 Development Workflow

### Adding a New Feature

1. **Create feature branch** (if using git)
2. **Backend changes:**
   ```powershell
   cd backend
   .\venv\Scripts\Activate.ps1
   # Edit files
   # Test with: uvicorn app.main:app --reload
   ```

3. **Frontend changes:**
   ```powershell
   cd frontend
   # Edit files
   # Test with: npm run dev
   ```

4. **Test integration:**
   - Upload test artifact
   - Verify candidate generation
   - Test validation workflow
   - Check dashboard updates

5. **Update documentation**

### Running After System Restart

```powershell
# Navigate to project
cd C:\nist-csf-tracker

# Start services
.\scripts\dev.ps1
```

---

## 🎯 Common Tasks

### Add New NIST CSF Controls

1. Edit `backend\app\seed_controls.py`
2. Add control dictionaries to `CSF_CONTROLS` list
3. Run:
   ```powershell
   cd backend
   .\venv\Scripts\Activate.ps1
   python -m app.seed_controls
   ```

### Recalculate All Scores

```powershell
# Via API
Invoke-RestMethod -Method POST http://localhost:8000/api/scores/recalculate-all
```

### Generate Gaps

```powershell
# Via API
Invoke-RestMethod -Method POST http://localhost:8000/api/gaps/generate
```

### Backup Database

```powershell
Copy-Item data\nist_csf_tracker.db "data\nist_csf_tracker_backup_$(Get-Date -Format 'yyyyMMdd_HHmmss').db"
```

### Restore Database

```powershell
Copy-Item data\nist_csf_tracker_backup_YYYYMMDD_HHMMSS.db data\nist_csf_tracker.db
```

---

## 🚨 Emergency Commands

**Complete reset (nuclear option):**
```powershell
# Backup first!
Remove-Item data\nist_csf_tracker.db
Remove-Item data\artifacts\* -Exclude .gitkeep
Remove-Item -Recurse -Force backend\venv
Remove-Item -Recurse -Force frontend\node_modules

# Rebuild
.\scripts\setup.ps1
```

**Force stop all services:**
```powershell
Get-Process | Where-Object {$_.ProcessName -like "*python*" -or $_.ProcessName -like "*node*"} | Stop-Process -Force
```

---

## 📚 Additional Resources

- API Documentation: http://localhost:8000/docs
- Redoc API Docs: http://localhost:8000/redoc
- Implementation Guide: `IMPLEMENTATION.md`
- Main README: `README.md`

---

## 💡 Pro Tips

1. **Use two terminals** when developing - one for backend, one for frontend
2. **Keep the browser console open** (F12) to see API errors
3. **Use the API docs** at `/docs` to test endpoints directly
4. **Check the database** with sqlite3 when debugging data issues
5. **Enable debug logging** when troubleshooting backend issues
6. **Clear browser cache** if frontend changes don't appear
7. **Use React Query DevTools** by installing `@tanstack/react-query-devtools`

---

*Last updated: Implementation complete (EPIC 0-4)*
