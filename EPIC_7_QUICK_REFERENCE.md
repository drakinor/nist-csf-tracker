# EPIC 7: Risk Acceptance - Quick Reference

## 🎯 Overview
Risk acceptance workflow with expiry enforcement, review cadence, and score isolation guarantees.

## 📋 Requirements Checklist
- ✅ Expiry enforcement (required dates, automatic expiry)
- ✅ Review cadence (tracking, overdue detection)
- ✅ Score isolation guarantee (explicit guarantees, verification)

---

## 🔧 Key API Endpoints

### Accept Risk (with required expiry)
```http
POST /risks/{risk_id}/accept
Content-Type: application/json

{
  "treatment": "accept",
  "justification": "Risk is acceptable because...",
  "expiry_date": "2024-12-31T23:59:59"  # REQUIRED, must be future
}
```

**Returns:** Risk object with acceptance details + score isolation guarantee

**Validations:**
- ✅ `expiry_date` is required
- ✅ `expiry_date` must be in the future
- ❌ Past dates rejected with 400 error
- ❌ Missing expiry rejected with 422 error

---

### List Expired Acceptances
```http
GET /risks/expired/acceptances
```

**Returns:**
```json
{
  "expired_count": 5,
  "expired_risks": [
    {
      "id": 3,
      "control_id": "ID.AM-1",
      "status": "accepted",
      "expiry_date": "2024-01-01T00:00:00",
      "days_expired": 14
    }
  ]
}
```

---

### Enforce Expiry (Reopen Expired Risks)
```http
POST /risks/enforce/expiry
```

**What it does:**
- Finds all risks with `status="accepted"` and `expiry_date < now()`
- Changes status from "accepted" to "open"
- Does NOT affect control scores

**Returns:**
```json
{
  "message": "Reopened 3 expired risk acceptances",
  "risks_reopened": 3,
  "guarantee": "Control scores unaffected by expiry enforcement"
}
```

---

### Mark Risk as Reviewed
```http
POST /risks/{risk_id}/review
Content-Type: application/json

{
  "review_notes": "Reviewed risk - still acceptable",
  "review_cadence_days": 90  # Next review in 90 days
}
```

**Returns:**
```json
{
  "id": 3,
  "last_reviewed": "2024-01-15T10:00:00",
  "next_review_due": "2024-04-15T10:00:00",
  "review_notes": "Reviewed risk - still acceptable"
}
```

**Sets:**
- `last_reviewed` = current timestamp
- `next_review_due` = last_reviewed + cadence_days

---

### Check Review Cadence (Find Overdue)
```http
GET /risks/check/review-cadence
```

**Returns:**
```json
{
  "total_accepted_risks": 10,
  "with_review_schedule": 8,
  "overdue_count": 2,
  "overdue_risks": [
    {
      "risk_id": 5,
      "control_id": "ID.AM-1",
      "next_review_due": "2024-01-01T00:00:00",
      "days_overdue": 14,
      "risk_description": "Incomplete asset inventory"
    }
  ]
}
```

---

### Verify Score Isolation
```http
GET /risks/verify/score-isolation
```

**Returns:**
```json
{
  "total_risks": 15,
  "total_scores": 50,
  "accepted_risks_count": 5,
  "sample_accepted_risks": [
    {
      "risk_id": 3,
      "risk_status": "accepted",
      "control_id": "ID.AM-1",
      "control_score": 0.66,
      "score_method": "Deterministic: 2 validated + 1 partial",
      "score_rationale": "Score based on validated evidence only"
    }
  ],
  "guarantee_verified": true,
  "explanation": "Risk acceptance and treatment decisions exist independently in the risk register. Control scores are calculated exclusively from validated evidence.",
  "proof": "Scores are calculated by ScoringService._determine_score() which only examines Evidence table, never Risk table"
}
```

---

## 🔒 Score Isolation Guarantee

### What It Means
**Risk operations NEVER affect control scores.**

### How It Works
1. **Scores** are calculated by `ScoringService._determine_score()`
2. **Scoring logic** only examines the `Evidence` table
3. **Risk register** operates on the `Risk` table
4. **No code path** exists where risk operations modify scores

### Proof Points
- ✅ Accepting a risk does not change the control's score
- ✅ Reviewing a risk does not change the control's score
- ✅ Enforcing expiry does not change any control scores
- ✅ Risk generation does not change any control scores

### Verification
```bash
# Get control score
GET /controls/ID.AM-1
# Note the score: 0.66

# Accept a risk for this control
POST /risks/3/accept
{
  "treatment": "accept",
  "justification": "Acceptable risk",
  "expiry_date": "2024-12-31T23:59:59"
}

# Check control score again
GET /controls/ID.AM-1
# Score is still: 0.66 ✅
```

---

## 📊 Typical Workflows

### Workflow 1: Accept Risk with Expiry
```
1. Identify open risk → GET /risks
2. Accept risk → POST /risks/{id}/accept
   - Provide expiry_date (required)
   - Provide justification
3. Verify score unchanged → GET /controls/{control_id}
```

### Workflow 2: Review Accepted Risk
```
1. Get accepted risks → GET /risks?status=accepted
2. Review risk → POST /risks/{id}/review
   - Add review_notes
   - Set review_cadence_days (e.g., 90)
3. Verify next_review_due is set
```

### Workflow 3: Enforce Expiry (Scheduled Job)
```
1. Check expired acceptances → GET /risks/expired/acceptances
2. Review expired list
3. Enforce expiry → POST /risks/enforce/expiry
4. Verify risks reopened
```

### Workflow 4: Monitor Overdue Reviews
```
1. Check review cadence → GET /risks/check/review-cadence
2. Review overdue list
3. For each overdue risk:
   - Review the risk
   - Mark as reviewed → POST /risks/{id}/review
```

---

## 🧪 Testing

### Test File
`backend/test_epic7_manual.py`

### Run Tests
```powershell
# Terminal 1: Start backend
cd c:\nist-csf-tracker\backend
..\\.venv\Scripts\python.exe -m uvicorn app.main:app --reload

# Terminal 2: Run tests
cd c:\nist-csf-tracker\backend
..\\.venv\Scripts\python.exe test_epic7_manual.py
```

### Test Coverage
- ✅ Expiry date required
- ✅ Past dates rejected
- ✅ Future dates accepted
- ✅ Expired risks listed
- ✅ Expiry enforcement works
- ✅ Review tracking works
- ✅ Overdue detection works
- ✅ Score isolation verified
- ✅ End-to-end isolation test

---

## 🚨 Common Issues

### Issue: "expiry_date is required"
**Solution:** Always provide `expiry_date` when accepting risks.
```json
{
  "treatment": "accept",
  "justification": "...",
  "expiry_date": "2024-12-31T23:59:59"  ← Add this
}
```

### Issue: "Expiry date must be in the future"
**Solution:** Use a date/time after now.
```python
from datetime import datetime, timedelta
expiry = (datetime.now() + timedelta(days=90)).isoformat()
```

### Issue: No risks to accept
**Solution:** Generate risks from gaps first.
```http
POST /risks/generate/from-gaps
```

### Issue: Tests failing with connection refused
**Solution:** Ensure backend server is running.
```powershell
cd c:\nist-csf-tracker\backend
..\\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

---

## 📈 Score Isolation Explained

### Why It Matters
Risk acceptance is a **business decision**, not a technical control implementation. Scores reflect **actual technical controls**, not risk appetite.

### Example
```
Control: ID.AM-1 (Asset inventory)
Score: 0.33 (1 validated evidence)

User accepts the risk of incomplete inventory:
POST /risks/3/accept

Control score remains: 0.33 ✅

Why? Because:
- The control is still only 33% implemented
- Risk acceptance doesn't change implementation
- Score reflects reality, not acceptance
```

### Benefits
1. **Honest scoring** - Scores reflect true control state
2. **Separation of concerns** - Risk decisions don't corrupt technical assessments
3. **Audit trail** - Risk register separate from control implementation
4. **Compliance** - Can show both control state AND risk treatment

---

## 🎓 Key Concepts

### Expiry Date
- **Required** for all risk acceptances
- **Must be future date** (validated)
- **Auto-enforcement** available via endpoint
- **Business rule:** No indefinite risk acceptance

### Review Cadence
- **Customizable** per risk (e.g., 90, 180 days)
- **Tracks** last_reviewed and next_review_due
- **Detects** overdue reviews automatically
- **Business rule:** Accepted risks must be reviewed regularly

### Score Isolation
- **Architectural** guarantee (not just documented)
- **Proven** by code structure and verification endpoint
- **Tested** in end-to-end tests
- **Business rule:** Scores reflect reality, not risk appetite

---

## 📖 Related Documentation
- Full details: `EPIC_7_COMPLETION_UPDATED.md`
- Test suite: `backend/test_epic7_manual.py`
- Risk API: `backend/app/api/risks.py`
- Scoring service: `backend/app/services/scoring_service.py`
