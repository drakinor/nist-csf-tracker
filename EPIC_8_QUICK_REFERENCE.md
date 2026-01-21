# EPIC 8: PDF Reporting - Quick Reference

## 🎯 Overview
Professional PDF report generation for NIST CSF compliance tracking.

## 📋 Requirements Checklist
- ✅ ReportLab integration (4.0.9)
- ✅ Executive summary template
- ✅ Evidence index with artifact references
- ✅ Gap analysis section
- ✅ Action plan export
- ✅ Custom branding framework

---

## 🔧 API Endpoints

### List Available Reports
```http
GET /api/reports/available
```

Returns catalog of all available report types.

---

### Executive Summary
```http
GET /api/reports/executive-summary?organization=MyOrg
```

**What's Included:**
- Overall compliance percentage
- Function-level breakdown
- Critical/high priority gaps (top 10)
- Key statistics (implemented/partial/missing)
- Strategic recommendations

**Best For:** Board meetings, executive briefings, quarterly reviews

**Download As:** `NIST_CSF_Executive_Summary_YYYYMMDD.pdf`

---

### Compliance Report
```http
GET /api/reports/compliance?organization=MyOrg
```

**What's Included:**
- Control-by-control status (all controls)
- Evidence details with artifact names
- Page locators for evidence
- Scoring rationales and methods
- Grouped by NIST CSF functions

**Best For:** Audits, detailed compliance review, evidence documentation

**Download As:** `NIST_CSF_Compliance_Report_YYYYMMDD.pdf`

---

### Gap Analysis
```http
GET /api/reports/gap-analysis?organization=MyOrg
```

**What's Included:**
- Gap summary by severity and status
- Critical/high/medium/low priority gaps
- Gap descriptions and types
- Associated controls
- Remediation recommendations

**Best For:** Remediation planning, risk assessments, prioritization

**Download As:** `NIST_CSF_Gap_Analysis_YYYYMMDD.pdf`

---

### Action Plan
```http
GET /api/reports/action-plan?organization=MyOrg
```

**What's Included:**
- Action summary by priority
- Open and in-progress actions
- Assignments and due dates
- Acceptance criteria
- Related gap associations

**Best For:** Project management, team assignments, progress tracking

**Download As:** `NIST_CSF_Action_Plan_YYYYMMDD.pdf`

---

## 💻 Usage Examples

### Download with Browser
```
http://localhost:8000/api/reports/executive-summary?organization=Acme%20Corp
```
(Opens download dialog)

### Download with cURL
```bash
# Executive summary
curl -O "http://localhost:8000/api/reports/executive-summary?organization=Acme%20Corp"

# All reports
curl -O "http://localhost:8000/api/reports/executive-summary?organization=Acme%20Corp"
curl -O "http://localhost:8000/api/reports/compliance?organization=Acme%20Corp"
curl -O "http://localhost:8000/api/reports/gap-analysis?organization=Acme%20Corp"
curl -O "http://localhost:8000/api/reports/action-plan?organization=Acme%20Corp"
```

### Download with PowerShell
```powershell
Invoke-WebRequest -Uri "http://localhost:8000/api/reports/executive-summary?organization=Acme%20Corp" -OutFile "executive_summary.pdf"
```

### Download with Python
```python
import requests

response = requests.get(
    "http://localhost:8000/api/reports/executive-summary",
    params={"organization": "Acme Corp"}
)

with open("executive_summary.pdf", "wb") as f:
    f.write(response.content)
```

---

## 📊 Report Layouts

### Executive Summary Structure
```
┌─────────────────────────────────────┐
│ NIST Cybersecurity Framework        │
│ Executive Summary Report            │
│ [Organization] - [Date]             │
├─────────────────────────────────────┤
│ Overall Compliance Status           │
│ ┌─────────────────────────────────┐ │
│ │ Overall Compliance  │ 67.5%     │ │
│ │ Total Controls      │ 108       │ │
│ │ Fully Implemented   │ 25        │ │
│ │ Partially Impl.     │ 50        │ │
│ │ Not Implemented     │ 33        │ │
│ │ Open Gaps           │ 15        │ │
│ │ Active Risks        │ 8         │ │
│ └─────────────────────────────────┘ │
├─────────────────────────────────────┤
│ Compliance by Function              │
│ ┌─────────────────────────────────┐ │
│ │ Identify    │ 12 │ 0.75 │ 75%  │ │
│ │ Protect     │ 35 │ 0.68 │ 68%  │ │
│ │ Detect      │ 18 │ 0.55 │ 55%  │ │
│ │ Respond     │ 25 │ 0.62 │ 62%  │ │
│ │ Recover     │ 18 │ 0.70 │ 70%  │ │
│ └─────────────────────────────────┘ │
├─────────────────────────────────────┤
│ Critical & High Priority Gaps       │
│ • [CRITICAL] ID.AM-1: Asset inv...  │
│ • [HIGH] PR.AC-1: Access control... │
│ • ...                               │
├─────────────────────────────────────┤
│ Recommendations                     │
│ • Focus on implementing baseline... │
│ • Address 15 critical/high gaps...  │
│ • ...                               │
└─────────────────────────────────────┘
```

### Compliance Report Structure
```
┌─────────────────────────────────────┐
│ NIST CSF Compliance Report          │
│ [Organization] - [Date]             │
├─────────────────────────────────────┤
│ Function: Identify                  │
│                                     │
│ ID.AM-1: Asset Inventory            │
│ Description: Physical devices...    │
│ Score: 0.66 / 1.00 (66%)           │
│ Method: Deterministic: 2 validated  │
│ Rationale: Evidence includes...    │
│ Evidence (2 items):                 │
│ • [policy] Asset Management Policy  │
│ • [procedure] Inventory Process     │
│                                     │
│ ID.AM-2: Software Inventory         │
│ ...                                 │
└─────────────────────────────────────┘
```

### Gap Analysis Structure
```
┌─────────────────────────────────────┐
│ Gap Analysis Report                 │
│ [Organization] - [Date]             │
├─────────────────────────────────────┤
│ Gap Summary                         │
│ ┌─────────────────────────────────┐ │
│ │ Severity │ Open │ Progress │ ... │ │
│ │ Critical │ 5    │ 2        │ ... │ │
│ │ High     │ 10   │ 5        │ ... │ │
│ │ Medium   │ 15   │ 8        │ ... │ │
│ │ Low      │ 8    │ 3        │ ... │ │
│ └─────────────────────────────────┘ │
├─────────────────────────────────────┤
│ Critical Priority Gaps (5)          │
│                                     │
│ ID.AM-1 - Asset Inventory           │
│ Type: Missing Policy                │
│ Status: Open                        │
│ Description: No formal asset...     │
│ Recommendation: Implement...        │
│                                     │
│ ...                                 │
└─────────────────────────────────────┘
```

---

## 🎨 Styling Reference

### Color Palette
- **Primary Blue**: `#1e40af` - Headers, emphasis
- **Success Green**: `#10b981` - Score 1.0 (fully implemented)
- **Info Blue**: `#3b82f6` - Score 0.66 (mostly implemented)
- **Warning Amber**: `#f59e0b` - Score 0.33 (partially implemented)
- **Error Red**: `#dc2626` - Score 0.0 (not implemented)
- **Muted Gray**: `#6b7280` - Metadata, footers

### Typography
- **Titles**: Helvetica-Bold, 24pt
- **Section Headings**: Helvetica-Bold, 16pt
- **Subsection Headings**: Helvetica-Bold, 14pt
- **Body Text**: Helvetica, 10pt
- **Small Text**: Helvetica, 8pt

---

## 🧪 Testing

### Manual Test Suite
```powershell
cd c:\nist-csf-tracker\backend
C:/nist-csf-tracker/.venv/Scripts/python.exe test_epic8_manual.py
```

**Tests:**
1. List available reports
2. Generate executive summary PDF
3. Generate compliance report PDF
4. Generate gap analysis PDF
5. Generate action plan PDF

**Output:** PDF files in current directory

---

## 🚨 Common Issues

### Issue: "Internal Server Error" (500)
**Cause:** ReportLab not loaded or server needs restart  
**Solution:**
```powershell
# Stop backend (Ctrl+C in server window)
cd c:\nist-csf-tracker
.\start.ps1
```

### Issue: PDF downloads as HTML error page
**Cause:** API error or missing data  
**Solution:** Check http://localhost:8000/docs for API status

### Issue: Report has no data / looks empty
**Cause:** Database not seeded  
**Solution:**
```powershell
cd c:\nist-csf-tracker\backend
C:/nist-csf-tracker/.venv/Scripts/python.exe -m app.seed_controls
```

### Issue: File download fails
**Cause:** Browser PDF handler issue  
**Solution:** Use curl instead:
```bash
curl -O "http://localhost:8000/api/reports/executive-summary"
```

---

## 📦 Dependencies

### Required Python Packages
```
reportlab==4.0.9      # PDF generation
fastapi==0.109.0      # API framework
sqlmodel==0.0.14      # Database ORM
```

### Installation
```powershell
# Already in requirements.txt
cd c:\nist-csf-tracker\backend
C:/nist-csf-tracker/.venv/Scripts/pip.exe install -r requirements.txt
```

---

## 🔮 Future Enhancements

### Potential Features
- 📊 **Charts & Graphs** - Visual compliance trends
- 🎨 **Logo Upload** - Custom organization branding
- 📧 **Email Delivery** - Automated report distribution
- 📅 **Scheduled Reports** - Weekly/monthly automation
- 🔒 **PDF Encryption** - Password-protected reports
- 📝 **Custom Templates** - User-defined report layouts
- 📎 **Evidence Bundling** - ZIP with PDFs and artifacts
- 🌐 **Multi-language** - Internationalization support
- ✍️ **Digital Signatures** - Report authentication
- 📈 **Trend Analysis** - Historical compliance comparison

---

## 📖 Related Documentation
- Full details: `EPIC_8_COMPLETION.md`
- PDF service code: `backend/app/services/pdf_service.py`
- API endpoints: `backend/app/api/reports.py`
- Test suite: `backend/test_epic8_manual.py`

---

## ✅ Quick Start

1. **Ensure server is running:**
   ```powershell
   cd c:\nist-csf-tracker
   .\start.ps1
   ```

2. **Generate executive summary:**
   ```
   http://localhost:8000/api/reports/executive-summary?organization=MyOrg
   ```

3. **Download opens automatically** or use:
   ```bash
   curl -O "http://localhost:8000/api/reports/executive-summary"
   ```

4. **View all available reports:**
   ```
   http://localhost:8000/docs#/Reports
   ```

**That's it!** Professional PDF reports ready for executives, auditors, and stakeholders.
