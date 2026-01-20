# EPIC 5 Quick Reference Guide

## 🎯 Overview
EPIC 5 adds advanced scoring capabilities, manual overrides, historical trend tracking, and enhanced dashboard visualizations to the NIST CSF Tracker.

---

## 🚀 New Features

### 1. Manual Score Override
**When to use**: When automated scoring doesn't reflect reality (e.g., compensating controls, auditor decisions)

**How to use**:
1. Navigate to Control Detail page for any control
2. Click the **Edit** button (pencil icon) next to current score
3. Select new score value from dropdown (0.0, 0.33, 0.66, 1.0)
4. Enter detailed justification (required)
5. Click **Save Override**

**Important Notes**:
- Requires justification to maintain audit trail
- Overridden scores show "Manually overridden" indicator
- Creates audit event in score_events table
- Use sparingly - automatic scoring is preferred

---

### 2. Lowest Scoring Controls Widget
**Location**: Dashboard → "Priority Actions" section

**What it shows**:
- Top 10 controls with lowest scores
- Control ID, name, function, current score
- Method (auto vs manual)
- Direct links to control detail pages

**Why it matters**: Focus improvement efforts where they'll have the most impact

---

### 3. Historical Trend Chart
**Location**: Dashboard → "Compliance Trends" section

**What it shows**:
- Line chart of overall compliance percentage
- Last 30 days by default (API supports variable periods)
- Trend direction indicator (improving/declining/stable)
- Number of data points collected

**Requirements**: Must capture snapshots regularly to build trend data

---

### 4. Score Snapshots
**Purpose**: Create point-in-time records of compliance state for trend analysis

**Three ways to capture**:

#### A. Manual via UI
1. Go to Dashboard
2. Click **Capture Snapshot** button (camera icon)
3. Snapshot created immediately

#### B. Manual via CLI
```bash
cd backend
.\venv\Scripts\Activate.ps1
python capture_snapshot.py
```

#### C. Automated (Recommended)
**Windows Task Scheduler**:
1. Open Task Scheduler
2. Create Basic Task → "Daily Score Snapshot"
3. Trigger: Daily at midnight (or your preferred time)
4. Action: Start a program
   - Program: `C:\nist-csf-tracker\backend\venv\Scripts\python.exe`
   - Arguments: `capture_snapshot.py`
   - Start in: `C:\nist-csf-tracker\backend`

**Linux/Mac cron**:
```bash
# Add to crontab (crontab -e)
0 0 * * * cd /path/to/backend && source venv/bin/activate && python capture_snapshot.py
```

---

### 5. Weighted Scoring (Optional)
**Purpose**: More granular scoring based on evidence importance

**Evidence Type Weights**:
- Technical: 30% (most important - actual controls)
- Policy: 25% (establishes requirements)
- Procedure: 25% (defines processes)
- Operational: 20% (proves execution)
- Assessment: 15% (validation)

**Confidence Multipliers**:
- High: 1.0x (100%)
- Medium: 0.85x (85%)
- Low: 0.70x (70%)

**How to use**:
```bash
# API call to recalculate all scores with weighted method
curl -X POST http://localhost:8000/api/scores/recalculate-weighted
```

**Note**: Standard boolean scoring (policy + procedure + technical = 1.0) is the default and recommended approach

---

## 📊 Dashboard Enhancements

### Color Coding
- **Green** (≥80%): Excellent compliance
- **Blue** (≥60%): Good compliance
- **Orange** (≥40%): Needs improvement
- **Red** (<40%): Critical - immediate attention required

### Score Distribution
Shows count of controls at each level:
- **Full**: 1.0 score (fully implemented)
- **Mostly**: 0.66 score (largely implemented)
- **Partial**: 0.33 score (partially implemented)
- **None**: 0.0 score (not implemented)

### Function Rollups
Each NIST CSF function (Govern, Identify, Protect, Detect, Respond, Recover) shows:
- Average percentage score
- Number of scored controls vs total controls
- Visual progress bar with color coding

---

## 🔧 API Endpoints

### Get Dashboard Data
```bash
GET /api/scores/dashboard
```
Returns: Overall score, function rollups, category rollups, score distribution

### Get Lowest Scoring Controls
```bash
GET /api/scores/lowest?limit=10
```
Returns: Top N lowest scoring controls with details

### Get Trend Data
```bash
GET /api/scores/trends?days=30
```
Returns: Historical snapshots for specified period

### Create Snapshot
```bash
POST /api/scores/snapshot
```
Returns: Created snapshot with ID and timestamp

### Manual Override
```bash
POST /api/scores/{control_id}/override
Body: {
  "score_value": 0.66,
  "score_label": "mostly",
  "notes": "Control meets requirements per audit",
  "user": "admin"
}
```
Returns: Updated score with event ID

### Weighted Recalculation
```bash
POST /api/scores/recalculate-weighted
```
Returns: Number of controls updated

---

## 📈 Best Practices

### Snapshot Frequency
- **Development/Testing**: Weekly or as needed
- **Active Implementation**: Daily
- **Steady State**: Weekly
- **Audit Preparation**: Daily

### Manual Override Guidelines
1. **Document thoroughly**: Future you needs to understand why
2. **Review regularly**: Set calendar reminders to reassess
3. **Prefer evidence**: Add more evidence instead of overriding when possible
4. **Audit trail matters**: Someone will read your justification

### Trend Analysis
- **Need 5+ snapshots** for meaningful trends
- **Daily snapshots** recommended during active implementation
- **Look for patterns**, not just the latest number
- **Compare functions** to identify weak areas

---

## 🐛 Troubleshooting

### "No trend data available"
**Solution**: Capture at least 2 snapshots (different days) to see a trend

### "Manual override failed"
**Check**:
- Score value is exactly 0.0, 0.33, 0.66, or 1.0
- Notes field is not empty
- Backend server is running

### Snapshot script errors
**Common issues**:
- Virtual environment not activated
- Database path incorrect
- Missing dependencies

**Fix**:
```bash
cd backend
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python capture_snapshot.py
```

### Chart not showing data points
**Check**:
- At least 2 snapshots exist in database
- Snapshots are from different dates
- Browser console for JavaScript errors

---

## 📝 Configuration

### Change Trend Period in UI
Edit `Dashboard.tsx`:
```typescript
// Change from 30 to 90 days
scoreApi.getTrends(90)
```

### Snapshot Retention
Edit `capture_snapshot.py`:
```python
# Keep last 365 days (default)
cleanup_old_snapshots(365)

# Keep last 90 days
cleanup_old_snapshots(90)
```

### Evidence Weights
Edit `scoring_service.py` → `EVIDENCE_WEIGHTS`:
```python
EVIDENCE_WEIGHTS = {
    "policy": 0.30,      # Increase policy weight
    "procedure": 0.30,   # Increase procedure weight
    "technical": 0.25,   # Decrease technical weight
    "operational": 0.15, # Decrease operational weight
    "assessment": 0.10   # Decrease assessment weight
}
```

---

## 🎓 Example Workflows

### Scenario 1: Audit Preparation
1. **Week before audit**: Capture daily snapshots
2. **Review dashboard**: Identify lowest scoring controls
3. **Gather evidence**: Focus on priority areas
4. **Validate evidence**: Process pending validation queue
5. **Check trends**: Verify improvement trajectory
6. **Document overrides**: Justify any manual overrides with auditor input

### Scenario 2: Ongoing Compliance
1. **Monthly**: Review dashboard and trends
2. **Weekly**: Capture snapshot
3. **As needed**: Validate new evidence
4. **Quarterly**: Review and refresh manual overrides
5. **Annually**: Full assessment and evidence update

### Scenario 3: New Implementation
1. **Day 1**: Upload all existing artifacts
2. **Week 1**: Validate evidence candidates
3. **Week 2-4**: Daily snapshots to track progress
4. **Month 1**: Review trends, identify gaps
5. **Ongoing**: Weekly snapshots, monthly reviews

---

## 📚 Related Documentation
- **Full Implementation**: See [EPIC_5_COMPLETION.md](EPIC_5_COMPLETION.md)
- **API Documentation**: http://localhost:8000/docs
- **Overall Project**: See [IMPLEMENTATION.md](IMPLEMENTATION.md)

---

**Status**: ✅ EPIC 5 Complete - All Features Production Ready
