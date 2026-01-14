# NIST CSF Tracker - Troubleshooting Guide

## 🚨 Common Issues & Solutions

### Installation & Setup Issues

#### Issue: "Python not found"
**Symptom**: Script fails with "python: command not found"

**Solution**:
```powershell
# Verify Python installation
python --version

# If not installed, download from python.org
# Make sure to check "Add Python to PATH" during installation
```

#### Issue: "Node not found"
**Symptom**: Script fails with "node: command not found"

**Solution**:
```powershell
# Verify Node installation
node --version

# If not installed, download from nodejs.org
# LTS version recommended
```

#### Issue: "venv creation fails"
**Symptom**: `python -m venv venv` fails

**Solution**:
```powershell
# Install venv package
python -m pip install --user virtualenv

# Or use virtualenv directly
pip install virtualenv
virtualenv venv
```

#### Issue: "pip install fails with SSL error"
**Symptom**: SSL certificate verification failed

**Solution**:
```powershell
# Upgrade pip first
python -m pip install --upgrade pip

# If still failing, try:
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt
```

---

### Startup Issues

#### Issue: "Port 8000 already in use"
**Symptom**: Backend fails to start, says port is busy

**Solution**:
```powershell
# Find process using port 8000
netstat -ano | findstr :8000

# Kill the process (replace PID with actual number)
taskkill /PID <PID> /F

# Or use a different port
uvicorn app.main:app --reload --port 8001
```

#### Issue: "Port 5173 already in use"
**Symptom**: Frontend fails to start

**Solution**:
```powershell
# Find and kill process
netstat -ano | findstr :5173
taskkill /PID <PID> /F

# Or change port in frontend/vite.config.ts:
# server: { port: 5174 }
```

#### Issue: "Module not found" errors
**Symptom**: Backend crashes with "No module named 'fastapi'" or similar

**Solution**:
```powershell
# Ensure virtual environment is activated
cd backend
.\venv\Scripts\Activate.ps1

# Verify activation (prompt should show (venv))
# Reinstall dependencies
pip install -r requirements.txt
```

#### Issue: "Database file not found"
**Symptom**: Backend crashes with database errors

**Solution**:
```powershell
# Initialize database
cd backend
.\venv\Scripts\Activate.ps1
python -m app.init_db
python -m app.seed_controls
```

---

### Frontend Issues

#### Issue: "CORS error in browser"
**Symptom**: Browser console shows CORS policy error

**Solution**:
1. Check backend `.env` file:
```env
CORS_ORIGINS=["http://localhost:5173","http://127.0.0.1:5173"]
```

2. Make sure backend is running

3. Clear browser cache and reload

4. Try accessing via http://localhost:5173 (not 127.0.0.1)

#### Issue: "White screen / blank page"
**Symptom**: Frontend loads but shows nothing

**Solution**:
```powershell
# Check browser console (F12) for errors
# Common fixes:

# 1. Clear cache
# 2. Restart frontend dev server
cd frontend
npm run dev

# 3. Reinstall dependencies
Remove-Item -Recurse -Force node_modules
npm install
```

#### Issue: "404 errors for API calls"
**Symptom**: API requests fail with 404

**Solution**:
1. Verify backend is running on port 8000
2. Check Vite proxy configuration in `vite.config.ts`
3. Test API directly: http://localhost:8000/docs
4. Ensure API paths match frontend calls

---

### Upload & Parsing Issues

#### Issue: "File upload fails"
**Symptom**: Upload returns error or times out

**Solution**:
```powershell
# Check file size (current limit ~100MB)
# Check file type (must be .docx, .pdf, .txt, .md, .xlsx)

# Verify artifacts directory exists and is writable
Test-Path data\artifacts
# Should return True

# Check disk space
Get-PSDrive C | Select-Object Used,Free
```

#### Issue: "Parsing error for DOCX"
**Symptom**: Upload succeeds but parsing fails

**Solution**:
```powershell
# Ensure file is valid DOCX (not DOC renamed to DOCX)
# Try opening file in Word first
# Check backend logs for specific error

# Test parser directly:
cd backend
.\venv\Scripts\Activate.ps1
python
>>> from app.parsers.parser_service import ParserService
>>> parser = ParserService()
>>> # Test your file
```

#### Issue: "PDF parsing returns empty text"
**Symptom**: PDF uploads but no chunks created

**Solution**:
- PDF might be image-based (scanned document)
- Current parser doesn't support OCR
- Try using a text-based PDF instead
- Or extract text externally first

#### Issue: "URL ingest fails"
**Symptom**: URL fetch returns error

**Solution**:
```powershell
# Check URL is accessible
Invoke-WebRequest -Uri "https://example.com"

# Ensure no firewall blocking
# Some sites block automated requests
# Try with a different URL

# Check backend logs for specific error
# (might be SSL, timeout, or content-type issue)
```

---

### Candidate Detection Issues

#### Issue: "No candidates found for control"
**Symptom**: Control shows 0 candidates

**Possible causes**:
1. No artifacts uploaded yet
2. Artifacts don't contain relevant keywords
3. Chunks are too short (< 50 characters filtered out)

**Solution**:
```powershell
# Verify chunks exist
sqlite3 data\nist_csf_tracker.db
SELECT COUNT(*) FROM artifact_chunks;

# Check control keywords
SELECT csf_id, keywords FROM controls WHERE id = 1;

# Manually test scoring
cd backend
.\venv\Scripts\Activate.ps1
python
>>> from app.services.candidate_service import CandidateService
>>> # Test scoring logic
```

#### Issue: "All candidates have low scores"
**Symptom**: Candidate scores all under 10

**Solution**:
- Normal if content doesn't match closely
- Try uploading more relevant documents
- Review control keywords and add custom ones:
```sql
UPDATE controls 
SET keywords = 'access control,authentication,authorization,IAM' 
WHERE csf_id = 'PR.AC-1';
```

---

### Scoring Issues

#### Issue: "Score doesn't update after validation"
**Symptom**: Evidence accepted but score stays the same

**Solution**:
```powershell
# Check if evidence was actually saved
sqlite3 data\nist_csf_tracker.db
SELECT * FROM evidence WHERE control_id = 1 AND status = 'accepted';

# Manually recalculate scores
Invoke-RestMethod -Method POST http://localhost:8000/api/scores/recalculate-all

# Check score_events table for history
SELECT * FROM score_events WHERE control_id = 1 ORDER BY timestamp DESC;
```

#### Issue: "Score seems wrong"
**Symptom**: Control has evidence but shows "none"

**Solution**:
1. Verify evidence status is "accepted" (not "pending" or "rejected")
2. Check scoring logic in `backend/app/services/scoring_service.py`
3. Manually trigger recalculation
4. Check for database consistency

---

### Database Issues

#### Issue: "Database locked"
**Symptom**: Operations fail with "database is locked"

**Solution**:
```powershell
# Close any open database connections
# Stop backend server
# Check for zombie processes
Get-Process | Where-Object {$_.ProcessName -like "*python*"}

# Restart backend
cd backend
.\venv\Scripts\Activate.ps1
uvicorn app.main:app --reload
```

#### Issue: "Foreign key constraint fails"
**Symptom**: Cannot delete artifact or control

**Solution**:
```powershell
# SQLite doesn't enforce foreign keys by default (good for our use case)
# If enforced, delete dependent records first:

# For artifact deletion:
sqlite3 data\nist_csf_tracker.db
DELETE FROM evidence WHERE artifact_id = 1;
DELETE FROM artifact_chunks WHERE artifact_id = 1;
DELETE FROM artifacts WHERE id = 1;
```

#### Issue: "Database corrupted"
**Symptom**: Random errors, data inconsistencies

**Solution**:
```powershell
# Check database integrity
sqlite3 data\nist_csf_tracker.db "PRAGMA integrity_check;"

# If corrupted, restore from backup or rebuild:
Remove-Item data\nist_csf_tracker.db
cd backend
.\venv\Scripts\Activate.ps1
python -m app.init_db
python -m app.seed_controls
# Re-upload artifacts
```

---

### Performance Issues

#### Issue: "Slow artifact upload"
**Symptom**: Upload takes > 30 seconds

**Possible causes**:
1. Large file size (> 50MB)
2. Complex document structure (many pages/sections)
3. Antivirus scanning file
4. Low disk space

**Solution**:
```powershell
# Check file size
Get-Item path\to\file.pdf | Select-Object Name, Length

# Temporarily disable antivirus for artifacts folder
# (or add exception for data\artifacts)

# Check disk space
Get-PSDrive C | Select-Object Used, Free
```

#### Issue: "Candidate generation slow"
**Symptom**: Takes > 5 seconds to load candidates

**Possible causes**:
1. Large number of chunks (1000s)
2. Complex scoring logic running on all chunks

**Solution**:
```powershell
# Check chunk count
sqlite3 data\nist_csf_tracker.db
SELECT COUNT(*) FROM artifact_chunks;

# If > 5000 chunks, consider:
# 1. Adding database indexes
# 2. Implementing chunk filtering before scoring
# 3. Caching candidate results
```

---

### Browser-Specific Issues

#### Issue: "Works in Chrome but not Edge/Firefox"
**Symptom**: Different behavior across browsers

**Solution**:
1. Clear browser cache
2. Check browser console for errors
3. Disable browser extensions
4. Try incognito/private mode
5. Update browser to latest version

#### Issue: "Changes not appearing"
**Symptom**: Code changes don't show up

**Solution**:
```powershell
# For frontend:
# 1. Hard refresh (Ctrl+Shift+R)
# 2. Clear cache
# 3. Restart dev server

# For backend:
# 1. Check uvicorn is in --reload mode
# 2. Restart server manually
# 3. Check for syntax errors in logs
```

---

### Data Integrity Issues

#### Issue: "Evidence shows for wrong control"
**Symptom**: Evidence mapped to incorrect control

**Solution**:
```powershell
# Check evidence table
sqlite3 data\nist_csf_tracker.db
SELECT e.id, c.csf_id, e.snippet_text 
FROM evidence e 
JOIN controls c ON e.control_id = c.id 
WHERE e.id = 1;

# If wrong, update:
UPDATE evidence SET control_id = 2 WHERE id = 1;
```

#### Issue: "Duplicate chunks"
**Symptom**: Same text appears multiple times

**Solution**:
```powershell
# Check for duplicates
sqlite3 data\nist_csf_tracker.db
SELECT chunk_text, COUNT(*) 
FROM artifact_chunks 
GROUP BY chunk_text 
HAVING COUNT(*) > 1;

# This is usually OK (same text in different documents)
# If truly duplicates from same artifact, delete:
DELETE FROM artifact_chunks WHERE id = X;
```

---

## 🔍 Debugging Tools

### Backend Debugging

**Enable debug logging:**
```powershell
cd backend
.\venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --log-level debug
```

**Test API endpoints:**
```powershell
# Health check
Invoke-RestMethod http://localhost:8000/health

# List controls
Invoke-RestMethod http://localhost:8000/api/controls/

# Get candidates
Invoke-RestMethod http://localhost:8000/api/controls/1/candidates
```

**Interactive Python debugging:**
```powershell
cd backend
.\venv\Scripts\Activate.ps1
python
>>> from app.models import Control, Artifact
>>> from app.database import engine
>>> from sqlmodel import Session, select
>>> 
>>> with Session(engine) as session:
...     controls = session.exec(select(Control)).all()
...     print(f"Found {len(controls)} controls")
```

### Frontend Debugging

**React DevTools:**
1. Install React DevTools browser extension
2. Open developer tools (F12)
3. Navigate to "Components" or "Profiler" tab

**TanStack Query DevTools:**
```powershell
cd frontend
npm install @tanstack/react-query-devtools

# Add to main.tsx:
# import { ReactQueryDevtools } from '@tanstack/react-query-devtools'
# <ReactQueryDevtools initialIsOpen={false} />
```

**Network debugging:**
1. Open browser DevTools (F12)
2. Go to "Network" tab
3. Filter by "Fetch/XHR"
4. Inspect API calls, status codes, payloads

### Database Debugging

**SQLite browser:**
```powershell
# Install DB Browser for SQLite (GUI tool)
# Or use command line:
cd data
sqlite3 nist_csf_tracker.db

# Useful commands:
.tables                    # List all tables
.schema controls           # Show table structure
.mode column              # Pretty print
.headers on               # Show column headers
SELECT * FROM controls LIMIT 5;
```

**Export data for analysis:**
```powershell
# Export to CSV
sqlite3 -csv data\nist_csf_tracker.db "SELECT * FROM evidence WHERE status='accepted'" > evidence.csv

# Export to JSON (with Python)
python
>>> import sqlite3, json
>>> conn = sqlite3.connect('data/nist_csf_tracker.db')
>>> cursor = conn.execute('SELECT * FROM controls')
>>> data = [dict(zip([c[0] for c in cursor.description], row)) for row in cursor]
>>> with open('controls.json', 'w') as f:
...     json.dump(data, f, indent=2)
```

---

## 🆘 Getting Help

### Self-Service Checklist
Before asking for help, try:
1. ✅ Read relevant documentation (README, IMPLEMENTATION, this guide)
2. ✅ Check browser console for errors (F12)
3. ✅ Review backend logs for error messages
4. ✅ Test API endpoints directly via /docs
5. ✅ Inspect database with sqlite3
6. ✅ Try the same operation in a fresh terminal
7. ✅ Restart both frontend and backend
8. ✅ Check if issue is reproducible

### Information to Provide
When reporting an issue, include:
- **What you tried**: Exact steps to reproduce
- **What happened**: Error messages, screenshots
- **What you expected**: Desired behavior
- **Your setup**: OS version, Python version, Node version
- **Logs**: Relevant backend logs and browser console output
- **Database state**: Relevant SQL queries and results

### Useful Diagnostic Commands
```powershell
# System info
python --version
node --version
npm --version

# Backend status
cd backend
.\venv\Scripts\Activate.ps1
pip list | findstr fastapi

# Frontend status
cd frontend
npm list --depth=0

# Database stats
sqlite3 data\nist_csf_tracker.db "SELECT 
  (SELECT COUNT(*) FROM artifacts) as artifacts,
  (SELECT COUNT(*) FROM artifact_chunks) as chunks,
  (SELECT COUNT(*) FROM controls) as controls,
  (SELECT COUNT(*) FROM evidence) as evidence,
  (SELECT COUNT(*) FROM scores) as scores;"

# Disk space
Get-PSDrive C | Select-Object Used, Free

# Process list
Get-Process | Where-Object {$_.ProcessName -like "*python*" -or $_.ProcessName -like "*node*"}
```

---

## 🔄 Reset & Recovery

### Complete Application Reset
**WARNING: This deletes all data!**

```powershell
# Backup first!
Copy-Item data\nist_csf_tracker.db data\backup_$(Get-Date -Format 'yyyyMMdd').db

# Stop all services
Get-Process | Where-Object {$_.ProcessName -like "*python*" -or $_.ProcessName -like "*node*"} | Stop-Process -Force

# Delete database and artifacts
Remove-Item data\nist_csf_tracker.db
Remove-Item data\artifacts\* -Exclude .gitkeep

# Rebuild
cd backend
.\venv\Scripts\Activate.ps1
python -m app.init_db
python -m app.seed_controls

# Restart
cd ..\..
.\scripts\dev.ps1
```

### Partial Resets

**Reset just evidence (keep artifacts):**
```powershell
sqlite3 data\nist_csf_tracker.db "DELETE FROM evidence; DELETE FROM scores; DELETE FROM score_events;"
```

**Reset just artifacts (keep controls):**
```powershell
sqlite3 data\nist_csf_tracker.db "DELETE FROM evidence; DELETE FROM artifact_chunks; DELETE FROM artifacts;"
Remove-Item data\artifacts\* -Exclude .gitkeep
```

**Reset just scores:**
```powershell
sqlite3 data\nist_csf_tracker.db "DELETE FROM scores; DELETE FROM score_events;"
# Then recalculate
Invoke-RestMethod -Method POST http://localhost:8000/api/scores/recalculate-all
```

---

## 💡 Prevention Tips

### Regular Maintenance
1. **Backup database weekly:**
   ```powershell
   Copy-Item data\nist_csf_tracker.db data\backups\backup_$(Get-Date -Format 'yyyyMMdd').db
   ```

2. **Monitor disk space:**
   ```powershell
   Get-PSDrive C | Select-Object Used, Free
   ```

3. **Review logs periodically:**
   - Check for repeated errors
   - Look for performance issues
   - Identify problematic artifacts

4. **Update dependencies monthly:**
   ```powershell
   cd backend
   pip install --upgrade -r requirements.txt
   
   cd ../frontend
   npm update
   ```

### Best Practices
1. **Upload clean documents**: Remove personal info, ensure good OCR quality
2. **Use descriptive tags**: Makes artifacts easier to find later
3. **Validate evidence promptly**: Don't let pending queue grow too large
4. **Add evidence notes**: Future you will thank you
5. **Review scores regularly**: Catch data quality issues early

---

*Troubleshooting guide as of MVP completion*
