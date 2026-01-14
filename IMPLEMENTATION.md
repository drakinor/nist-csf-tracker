# NIST CSF Tracker - Implementation Guide

## Project Overview

A local-first application for tracking NIST Cybersecurity Framework compliance with automated evidence detection and human validation.

**Status**: ✅ EPIC 0-4 Complete (MVP Ready)

---

## 🎯 What's Implemented

### ✅ EPIC 0: Repository & Local Dev UX
- Complete monorepo structure
- One-command startup script (`.\scripts\dev.ps1`)
- Setup automation (`.\scripts\setup.ps1`)
- Environment configuration

### ✅ EPIC 1: Data Model (Foundation)
- 9 database tables with full schema
- SQLite storage with SQLModel ORM
- Automatic database initialization
- 23 NIST CSF 2.0 controls seeded (expandable)
- Full audit trail for score changes

### ✅ EPIC 2: Artifact Ingestion + Chunking
- **Parsers implemented**:
  - DOCX (chunks by heading hierarchy)
  - PDF (chunks by pages and paragraphs)
  - TXT/MD (chunks by paragraphs with heading detection)
  - XLSX (chunks by rows)
  - URLs (fetch + boilerplate removal + local snapshot)
- **Features**:
  - File upload with hash-based deduplication
  - URL ingestion with readability extraction
  - Automatic chunking with precise locators
  - Artifact viewer with chunk inspection
  - Tag-based organization

### ✅ EPIC 3: Evidence Candidate Engine (Rules-Based)
- **Matching algorithms**:
  - Control ID detection
  - Keyword matching (custom + function-specific)
  - Category-specific regex patterns
  - Heading/section relevance scoring
  - Multi-factor scoring system (0-100 scale)
- **Features**:
  - Top-N candidate ranking
  - Match reason explanations
  - Duplicate detection (already reviewed evidence)
  - Support for 23+ controls across 5 functions

### ✅ EPIC 4: Validation Workspace (Human-in-the-Loop)
- **Control detail page**:
  - Control metadata and rubric display
  - Current score badge
  - Accepted evidence list with locators
  - Evidence candidate queue with scoring
- **Validation workflow**:
  - Full-text snippet viewer
  - Evidence type selector (policy/procedure/technical/operational)
  - Notes field for rationale
  - Accept/Reject actions with immediate score recalculation
  - Source locator display (page/heading/paragraph)
- **Validation queue**:
  - Centralized pending evidence review
  - Bulk validation support
  - Quick accept/reject with evidence typing

---

## 📁 Project Structure

```
nist-csf-tracker/
├── backend/
│   ├── app/
│   │   ├── api/                    # FastAPI routes
│   │   │   ├── artifacts.py        # Artifact CRUD + upload/ingest
│   │   │   ├── controls.py         # Control browsing + candidates
│   │   │   ├── evidence.py         # Evidence validation
│   │   │   ├── scores.py           # Scoring + dashboard
│   │   │   ├── gaps.py             # Gap management
│   │   │   ├── actions.py          # Action items
│   │   │   └── risks.py            # Risk acceptance
│   │   ├── models/                 # SQLModel data models
│   │   │   └── __init__.py         # All 9 table definitions
│   │   ├── services/               # Business logic
│   │   │   ├── artifact_service.py # File storage + URL ingestion
│   │   │   ├── candidate_service.py # Evidence matching engine
│   │   │   ├── scoring_service.py  # Score calculation + rollups
│   │   │   └── gap_service.py      # Gap generation
│   │   ├── parsers/                # Document parsers
│   │   │   └── parser_service.py   # DOCX/PDF/TXT/XLSX/URL parsers
│   │   ├── config.py               # Settings management
│   │   ├── database.py             # DB connection
│   │   ├── main.py                 # FastAPI app
│   │   ├── init_db.py              # Database initialization
│   │   └── seed_controls.py        # NIST CSF control seeding
│   ├── requirements.txt            # Python dependencies
│   └── .env.example                # Environment template
├── frontend/
│   ├── src/
│   │   ├── pages/                  # React pages
│   │   │   ├── Dashboard.tsx       # Overall stats + function rollups
│   │   │   ├── Artifacts.tsx       # Artifact management + upload
│   │   │   ├── Controls.tsx        # Control browsing
│   │   │   ├── ControlDetail.tsx   # Validation workspace
│   │   │   └── ValidationQueue.tsx # Bulk validation queue
│   │   ├── services/               # API client
│   │   │   └── api.ts              # Axios client + TypeScript types
│   │   ├── App.tsx                 # Main app + routing
│   │   ├── main.tsx                # React entry point
│   │   └── index.css               # Global styles
│   ├── package.json                # Node dependencies
│   ├── vite.config.ts              # Vite configuration
│   └── tsconfig.json               # TypeScript configuration
├── data/
│   ├── artifacts/                  # Uploaded files + URL snapshots
│   └── nist_csf_tracker.db         # SQLite database (created on init)
├── scripts/
│   ├── dev.ps1                     # One-command startup
│   └── setup.ps1                   # Initial setup automation
└── README.md                       # Project documentation
```

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.11+** (with pip)
- **Node.js 18+** (with npm)
- **PowerShell** (Windows)

### Option 1: Automated Setup (Recommended)

```powershell
# Clone or extract the project
cd nist-csf-tracker

# Run setup script (one-time)
.\scripts\setup.ps1

# Start the application
.\scripts\dev.ps1
```

The app will open at **http://localhost:5173**

### Option 2: Manual Setup

**Backend:**
```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env

# Initialize database
python -m app.init_db
python -m app.seed_controls

# Start server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend (new terminal):**
```powershell
cd frontend
npm install
npm run dev
```

Access at:
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

---

## 📊 Usage Workflow

### Step 1: Ingest Artifacts
1. Navigate to **Artifacts** page
2. Click **Upload File** or **Ingest URL**
3. Select document (DOCX, PDF, TXT, XLSX) or enter URL
4. Add tags (optional)
5. System automatically chunks and stores with locators

### Step 2: Review Evidence Candidates
1. Navigate to **Controls** page
2. Browse by function or category
3. Click on a control to see details
4. View **Evidence Candidates** section
5. Click **Review** on a candidate

### Step 3: Validate Evidence
1. Review full snippet text with source locator
2. Select evidence type (Policy/Procedure/Technical/Operational)
3. Add notes (optional)
4. Click **Accept Evidence** or **Reject**
5. Score updates automatically

### Step 4: Monitor Progress
1. Navigate to **Dashboard**
2. View overall compliance percentage
3. Review function-level rollups
4. Check pending validation count

### Step 5: Bulk Validation (Optional)
1. Navigate to **Validation Queue**
2. Review all pending evidence in one place
3. Quickly accept/reject with evidence typing

---

## 🎯 Acceptance Criteria Status

### EPIC 1: Data Model ✅
- [x] 9 tables defined with proper relationships
- [x] Audit trail for score changes
- [x] Migrations/initialization scripts
- [x] 23 NIST CSF controls seeded

### EPIC 2: Artifact Ingestion ✅
- [x] File upload endpoint (DOCX/PDF/TXT/XLSX)
- [x] URL ingest with boilerplate removal
- [x] DOCX parser with heading hierarchy
- [x] PDF parser with page/paragraph locators
- [x] TXT/MD parser with paragraph chunking
- [x] XLSX parser with row chunking
- [x] Artifact list UI with viewer

### EPIC 3: Evidence Candidate Engine ✅
- [x] Keyword matching (custom + function-specific)
- [x] Control ID detection
- [x] Category-specific regex patterns
- [x] Heading/section relevance scoring
- [x] Ranked candidate list with match reasons
- [x] API endpoint `/controls/{id}/candidates`
- [x] Candidate display in UI with scoring

### EPIC 4: Validation Workspace ✅
- [x] Control detail page with rubric
- [x] Evidence candidate list with "Review" action
- [x] Source viewer with full text + locator
- [x] Evidence type selector
- [x] Accept/Reject workflow
- [x] Automatic score recalculation
- [x] Validation queue page for bulk review
- [x] Audit trail recording

---

## 🔧 Technical Details

### Backend Architecture

**Framework**: FastAPI 0.109  
**Database**: SQLite with SQLModel ORM  
**Async**: Full async/await support  
**Validation**: Pydantic v2 models  

**Key Services**:
- `ArtifactService`: File storage, URL fetching, hash-based deduplication
- `ParserService`: Document-type routing and chunking logic
- `CandidateService`: Rules-based evidence matching with scoring
- `ScoringService`: Score calculation, rollups, and history

### Frontend Architecture

**Framework**: React 18 with TypeScript  
**Build Tool**: Vite 5  
**Routing**: React Router v6  
**Data Fetching**: TanStack Query (React Query)  
**HTTP Client**: Axios  
**Icons**: Lucide React  

**Key Components**:
- `Dashboard`: Overall stats and function rollups
- `Artifacts`: File upload, URL ingest, chunk viewer
- `Controls`: Browse controls by function/category
- `ControlDetail`: Validation workspace with candidates
- `ValidationQueue`: Bulk validation interface

### Evidence Matching Algorithm

**Scoring Factors** (0-100 scale):
1. **Control ID Match** (+50): Exact CSF ID found in text
2. **Name Keyword Overlap** (+5 per match): Control name terms
3. **Custom Keywords** (+10 per match): User-defined keywords
4. **Function Keywords** (+3 per match): Function-specific terms
5. **Category Patterns** (+8 per match): Regex patterns for categories
6. **Locator Bonus** (+5): Relevant section heading

**Score Interpretation**:
- **50+**: Very strong match (control ID found)
- **30-50**: Strong match (multiple factors)
- **15-30**: Moderate match (some factors)
- **<15**: Weak match (filtered out)

### Score Calculation

**Control Scores**:
- **None (0.0)**: No evidence
- **Partial (0.33)**: Single evidence type
- **Mostly (0.66)**: 2 evidence types or 2+ items
- **Full (1.0)**: 3+ evidence types

**Rollups**:
- **Function**: Average of all controls in function
- **Category**: Average of all controls in category
- **Overall**: Average of all scored controls

---

## 📈 Next Steps (Post-MVP)

### EPIC 5: Scoring + Rollups + Dashboard
- [ ] Advanced scoring rules (weighted by evidence type)
- [ ] Manual score override capability
- [ ] "Lowest scoring controls" widget
- [ ] Historical trend charts

### EPIC 6: Gap Analysis + Action Items
- [ ] Automated gap generation from missing controls
- [ ] Gap classification (missing/incomplete/policy-only)
- [ ] Action item creation and tracking
- [ ] Kanban board for actions
- [ ] Due date notifications

### EPIC 7: Risk Acceptance
- [ ] Risk acceptance form
- [ ] Likelihood/Impact matrix
- [ ] Approval workflow
- [ ] Expiry/review date tracking
- [ ] Risk register report

### EPIC 8: PDF Reporting
- [ ] ReportLab integration
- [ ] Executive summary template
- [ ] Evidence index with artifact references
- [ ] Action plan section
- [ ] Risk acceptance summary
- [ ] Custom branding/logo

### EPIC 9: Optional Local LLM Enhancement
- [ ] Ollama integration (feature flag)
- [ ] Chunk summarization
- [ ] Semantic similarity scoring
- [ ] Control-to-chunk recommendations
- [ ] Never auto-accept (suggestions only)

---

## 🧪 Testing the Application

### Test Workflow

1. **Upload a sample policy document** (DOCX or PDF)
   - Use a security policy, access control procedure, or incident response plan
   - The system will chunk it and create locators

2. **Navigate to Controls**
   - Browse controls by function
   - Click on "PR.AC-1" (Access Control) or "DE.CM-7" (Continuous Monitoring)

3. **Review Candidates**
   - See ranked evidence candidates
   - Check match reasons and scores
   - Click "Review" on top candidates

4. **Validate Evidence**
   - Review full text with locator
   - Select evidence type
   - Accept or reject
   - Watch score update in real-time

5. **Check Dashboard**
   - View overall compliance percentage
   - See function-level rollups
   - Monitor pending validation count

### Sample Test Data

Create a test document with these phrases:
- "Access control policy requires multi-factor authentication"
- "Incident response procedures include notification within 24 hours"
- "Continuous monitoring via SIEM tool with real-time alerts"
- "Asset inventory maintained in configuration management database"

These will match multiple controls and demonstrate the matching engine.

---

## 🔍 Debugging

### Backend Logs
```powershell
cd backend
.\venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --log-level debug
```

### Frontend Logs
Check browser console (F12) for:
- API errors
- React Query cache status
- Network requests

### Database Inspection
```powershell
cd data
sqlite3 nist_csf_tracker.db
.tables
SELECT * FROM controls LIMIT 5;
SELECT * FROM evidence WHERE status='accepted';
.quit
```

### Common Issues

**"ModuleNotFoundError"**: Activate virtual environment first  
**"Port already in use"**: Kill existing uvicorn/node processes  
**"CORS error"**: Check CORS_ORIGINS in backend/.env  
**"No controls found"**: Run `python -m app.seed_controls`  

---

## 📝 Configuration

### Backend (.env)
```env
DATABASE_URL=sqlite:///../../data/nist_csf_tracker.db
ARTIFACTS_PATH=../../data/artifacts
FEATURE_LLM=false
OLLAMA_URL=http://localhost:11434
CORS_ORIGINS=["http://localhost:5173","http://127.0.0.1:5173"]
```

### Key Settings
- `DATABASE_URL`: SQLite path (relative or absolute)
- `ARTIFACTS_PATH`: Uploaded file storage location
- `FEATURE_LLM`: Enable Ollama integration (future)
- `CORS_ORIGINS`: Allowed frontend origins

---

## 🎓 Key Learning Points

### Architecture Decisions

1. **SQLite over PostgreSQL**: Local-first requirement, no cloud dependency
2. **Rules-based matching first**: Deterministic, explainable, auditable
3. **Chunk-level locators**: Precise source tracing for validation
4. **Human validation required**: Never auto-accept evidence
5. **Score audit trail**: Every score change is logged with reason

### Evidence Validation Philosophy

- **Show the source**: Always display exact location (page/heading/paragraph)
- **Explain the match**: Surface all matching factors and keywords
- **Type the evidence**: Categorize as policy/procedure/technical/operational
- **Track the decision**: Capture notes and rationale
- **Recalculate immediately**: Scores update on validation

### Scalability Considerations

**Current Limits**:
- Single-user (no auth)
- Local storage only
- Synchronous processing
- In-memory candidate ranking

**Future Scaling**:
- Add user authentication
- Implement async background jobs
- Use PostgreSQL for multi-user
- Add Redis for caching
- Implement pagination for large datasets

---

## 🤝 Contributing

### Adding New Controls

Edit `backend/app/seed_controls.py`:
```python
{
    "csf_id": "PR.DS-3",
    "function": "Protect",
    "category": "PR.DS",
    "subcategory": "PR.DS-3",
    "name": "Asset Disposal",
    "text": "Assets are formally managed throughout removal...",
    "keywords": "disposal, decommission, sanitization, destruction"
}
```

Run: `python -m app.seed_controls`

### Adding New Parsers

Create parser in `backend/app/parsers/parser_service.py`:
```python
def _parse_custom(self, artifact: Artifact) -> List[Dict[str, Any]]:
    # Your parsing logic
    return chunks
```

Add to `parse_and_chunk()` routing logic.

### Customizing Scoring

Edit `backend/app/services/scoring_service.py`:
```python
def _determine_score(self, evidence_list: list) -> tuple[float, str]:
    # Your scoring logic
    return score_value, score_label
```

---

## 📞 Support

For questions or issues:
1. Check this guide first
2. Review API docs at http://localhost:8000/docs
3. Inspect database with sqlite3
4. Enable debug logging on backend

---

## 🎉 Success Metrics

**MVP Definition of Done** ✅:
- [x] Ingest DOCX or PDF artifact
- [x] System proposes evidence candidates for controls
- [x] Validate evidence by seeing exact source section
- [x] Scores update based on validated evidence
- [x] Scores roll up by category/function
- [x] Dashboard shows overall compliance posture

**Current Status**: **MVP COMPLETE** - Ready for production use!

---

## 📄 License

Proprietary - Internal use only
