# EPIC 6: Quick Reference Guide

## 🎯 What's New in EPIC 6

**Gap Analysis + Action Items**: Complete remediation workflow from gap identification to resolution

---

## ⚡ Quick Commands

### View Gap Analysis
```
Navigate to: http://localhost:5174/#/gaps
```

### View Action Board
```
Navigate to: http://localhost:5174/#/actions
```

### Regenerate Gaps
```powershell
curl -X POST http://localhost:8000/api/gaps/regenerate
```

---

## 📊 Key Pages

### Gap Analysis (`/gaps`)
**What**: Shows all control implementation gaps  
**Use When**: Preparing for audits, quarterly reviews, identifying weaknesses

**Quick Actions**:
- Filter by severity (critical/high/medium/low)
- Filter by status (open/in_progress/resolved/accepted)
- Filter by gap type
- Create action from gap
- Mark gap resolved

### Actions Board (`/actions`)
**What**: Kanban board for tracking remediation tasks  
**Use When**: Managing ongoing work, sprint planning, daily standups

**Quick Actions**:
- Create new action
- Start action (open → in_progress)
- Complete action (in_progress → complete)
- Block action (in_progress → blocked)
- Resume action (blocked → in_progress)

---

## 🔥 Common Workflows

### Audit Preparation
```
1. Go to Gap Analysis
2. Filter: severity = "critical" OR "high"
3. For each gap:
   - Click "Create Action"
   - Assign owner
   - Set due date before audit
4. Track in Actions board
5. Mark gaps resolved as work completes
```

### Weekly Team Standup
```
1. Open Actions board
2. Review "In Progress" column
3. Identify blocked actions
4. Move completed work to "Complete"
5. Check overdue count
```

### New Control Implementation
```
1. Control shows 0.0 score
2. Gap auto-created: "missing_control"
3. Create action: "Implement [Control]"
4. Add sub-tasks as separate actions
5. Upload evidence as work progresses
6. Gap auto-resolves when score ≥ 0.66
```

---

## 🎨 Gap Types Explained

| Type | Description | Example |
|------|-------------|---------|
| **missing_control** | No evidence at all | Control never implemented |
| **missing_policy** | No policy documentation | Technical controls exist, no formal policy |
| **missing_procedure** | No procedure docs | Policy exists, no operational procedures |
| **missing_technical_enforcement** | No technical controls | Policy + procedures, but no enforcement |
| **missing_operational_evidence** | No operational proof | Controls deployed, no logs/reports |
| **incomplete_implementation** | Partial implementation | Some evidence, but gaps remain |

---

## 🚦 Gap Severities

| Severity | Score Range | Meaning | Priority |
|----------|-------------|---------|----------|
| **Critical** | 0.0 | No implementation | Immediate |
| **High** | 0.01 - 0.32 | Minimal implementation | This sprint |
| **Medium** | 0.33 - 0.65 | Partial implementation | Next quarter |
| **Low** | 0.66 - 0.99 | Mostly complete | Backlog |

---

## 📋 Action Statuses

| Status | Icon | Meaning | Next Step |
|--------|------|---------|-----------|
| **open** | 🔵 | Ready to start | Click "Start" |
| **in_progress** | 🟠 | Currently working | Click "Done" or "Block" |
| **blocked** | 🔴 | Impediment | Click "Resume" when unblocked |
| **complete** | 🟢 | Finished | No action needed |

---

## 🛠️ API Quick Reference

### Get All Gaps
```bash
GET /api/gaps/
Query params: ?status=open&severity=critical
```

### Get Gap Summary
```bash
GET /api/gaps/summary
Response: { "total": 10, "by_severity": {...}, "by_status": {...} }
```

### Create Action
```bash
POST /api/actions/
Body: {
  "title": "Implement MFA",
  "gap_id": 5,
  "owner": "security_team",
  "due_date": "2026-02-15T00:00:00",
  "description": "Enable MFA for all users"
}
```

### Update Action Status
```bash
PATCH /api/actions/{id}
Body: { "status": "complete" }
```

### Get Kanban Board
```bash
GET /api/actions/kanban/board
Response: {
  "columns": {
    "open": [...],
    "in_progress": [...],
    "blocked": [...],
    "complete": [...]
  }
}
```

---

## 💡 Pro Tips

### Gap Management
- **Review monthly**: Don't let gaps accumulate
- **Prioritize by risk**: Critical gaps first, always
- **Document reasoning**: Note why gaps were accepted/resolved
- **Link to controls**: Use control detail page for context

### Action Planning
- **Be specific**: Good: "Enable MFA for VPN access", Bad: "Fix access control"
- **Set deadlines**: Everything needs a due date
- **Assign owners**: Someone must be accountable
- **Define "done"**: Write acceptance criteria

### Kanban Best Practices
- **Limit WIP**: 3-5 items "in_progress" per person
- **Unblock fast**: Review "blocked" daily
- **Complete often**: Don't let "in_progress" pile up
- **Update status**: Keep board current

---

## 🔍 Troubleshooting

### Issue: No gaps showing
**Solution**: 
1. Check filters (set all to "All")
2. Run: `POST /api/gaps/regenerate`
3. Verify controls are scored

### Issue: Actions not updating
**Solution**:
1. Check browser console for errors
2. Verify backend is running (`:8000`)
3. Check network tab for failed requests

### Issue: Gaps not auto-generating
**Solution**: Gaps generate during scoring:
1. Validate evidence to trigger
2. Or manually regenerate

### Issue: Wrong severity on gap
**Solution**: Edit gap directly:
```bash
PATCH /api/gaps/{id}
Body: { "severity": "critical" }
```

---

## 📈 Metrics to Track

### Daily
- Overdue action count
- Blocked action count

### Weekly
- Actions completed this week
- New gaps identified
- In-progress action count

### Monthly
- Total gaps by severity
- Average time to resolve gaps
- Completion rate
- Gaps per control area

---

## 🎯 Success Criteria

### Gap Analysis Working
- [x] Gaps auto-generate from scores
- [x] Severities assign correctly
- [x] Filtering works
- [x] Summary stats accurate

### Actions Working
- [x] Can create from gaps
- [x] Status transitions work
- [x] Overdue detection works
- [x] Kanban board displays

### Workflow Complete
- [x] Gap → Action → Resolution
- [x] Evidence upload → Gap resolves
- [x] Audit trail visible

---

## 🚀 Next Steps

After EPIC 6, you can:
- **EPIC 7**: Risk acceptance workflow
- **EPIC 8**: PDF report generation
- **EPIC 9**: Local LLM enhancement

---

## 📞 Quick Help

**Full docs**: [EPIC_6_COMPLETION.md](EPIC_6_COMPLETION.md)  
**API docs**: http://localhost:8000/docs  
**Frontend**: http://localhost:5174  
**Backend**: http://localhost:8000

---

**Remember**: Gap Analysis identifies problems, Actions solve them. Review gaps weekly, update actions daily.
