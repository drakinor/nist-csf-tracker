# NIST CSF Tracker

A local-first application for tracking NIST Cybersecurity Framework compliance with evidence validation and automated gap analysis.

## Architecture

- **Backend**: Python + FastAPI + SQLite + SQLModel
- **Frontend**: React + Vite + TypeScript
- **Storage**: SQLite database + local artifact storage
- **Parsers**: python-docx, pypdf, BeautifulSoup4, readability-lxml
- **Reporting**: ReportLab for PDF generation

## Features

1. **Artifact Ingestion**: Import DOCX, PDF, TXT/MD, XLSX files and URLs with local snapshots
2. **Evidence Detection**: Rules-based engine proposes evidence snippets mapped to NIST CSF controls
3. **Human Validation**: Review exact source sections (page/heading/paragraph) before accepting evidence
4. **Scoring & Rollups**: Control-level scores roll up to categories and function domains
5. **Gap Analysis**: Identify missing/partial controls with severity classification
6. **Action Items**: Generate and track remediation tasks
7. **Risk Acceptance**: Document and track accepted risks with review dates
8. **PDF Reports**: Executive summary, evidence index, action plan, and risk register

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- PowerShell (Windows)

### Setup

1. **Install backend dependencies**:
```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. **Initialize database**:
```powershell
python -m app.init_db
```

3. **Install frontend dependencies**:
```powershell
cd ..\frontend
npm install
```

### Development

**Option 1: Manual start (two terminals)**

Terminal 1 (Backend):
```powershell
cd backend
.\venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Terminal 2 (Frontend):
```powershell
cd frontend
npm run dev
```

**Option 2: One-command start**
```powershell
.\scripts\dev.ps1
```

Access the application at http://localhost:5173

## Project Structure

```
nist-csf-tracker/
├── backend/
│   ├── app/
│   │   ├── api/              # API routes
│   │   ├── models/           # SQLModel data models
│   │   ├── services/         # Business logic
│   │   ├── parsers/          # Document parsers
│   │   ├── config.py         # Configuration
│   │   ├── database.py       # Database connection
│   │   └── main.py           # FastAPI app
│   ├── alembic/              # Database migrations
│   ├── requirements.txt
│   └── .env
├── frontend/
│   ├── src/
│   │   ├── components/       # React components
│   │   ├── pages/           # Page components
│   │   ├── services/        # API client
│   │   └── App.tsx
│   ├── package.json
│   └── vite.config.ts
├── data/
│   ├── artifacts/           # Uploaded files and URL snapshots
│   └── nist_csf_tracker.db  # SQLite database
├── scripts/
│   └── dev.ps1              # Development startup script
└── README.md
```

## Development Status

✅ **MVP COMPLETE** - Ready for production use!

### Completed EPICs

- ✅ **EPIC 0**: Repository structure and local dev UX
- ✅ **EPIC 1**: Data model and migrations (9 tables, full schema)
- ✅ **EPIC 2**: Artifact ingestion and chunking (DOCX/PDF/TXT/XLSX/URL parsers)
- ✅ **EPIC 3**: Evidence candidate engine (rules-based matching with scoring)
- ✅ **EPIC 4**: Validation workspace (human-in-the-loop evidence review)

### Coming Soon

- [ ] **EPIC 5**: Enhanced scoring + rollups + dashboard widgets
- [ ] **EPIC 6**: Gap analysis + action items with kanban board
- [ ] **EPIC 7**: Risk acceptance tracking with approval workflow
- [ ] **EPIC 8**: PDF reporting (ReportLab integration)
- [ ] **EPIC 9**: Optional local LLM enhancement (Ollama)

## Data Model

### Core Tables
- **artifacts**: Ingested documents and URLs
- **artifact_chunks**: Text chunks with locators (page/heading/paragraph)
- **controls**: NIST CSF control definitions
- **evidence**: Validated evidence snippets linked to controls
- **scores**: Control scores with calculation method and rationale
- **gaps**: Missing or partial control implementations
- **actions**: Remediation tasks linked to gaps
- **risk_acceptance**: Documented risk acceptance records
- **score_events**: Audit trail of score changes

## Configuration

Create a `.env` file in the `backend/` directory:

```env
DATABASE_URL=sqlite:///../../data/nist_csf_tracker.db
ARTIFACTS_PATH=../../data/artifacts
FEATURE_LLM=false
OLLAMA_URL=http://localhost:11434
```

## License

Proprietary - Internal use only
