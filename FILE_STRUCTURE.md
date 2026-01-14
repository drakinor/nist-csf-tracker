# NIST CSF Tracker - Complete File Structure

## 📂 Full Directory Tree

```
C:\nist-csf-tracker\
│
├── 📄 README.md                        # Main project documentation
├── 📄 IMPLEMENTATION.md                # Detailed implementation guide
├── 📄 QUICK_REFERENCE.md               # Command reference
├── 📄 .gitignore                       # Git ignore rules
│
├── 📁 backend\                         # Python FastAPI backend
│   ├── 📁 app\
│   │   ├── 📁 api\                     # API route handlers
│   │   │   ├── 📄 artifacts.py         # Upload, ingest URL, list, delete
│   │   │   ├── 📄 controls.py          # List, get, candidates, score, summaries
│   │   │   ├── 📄 evidence.py          # Create, validate, list, delete
│   │   │   ├── 📄 scores.py            # List, recalculate, dashboard, history
│   │   │   ├── 📄 gaps.py              # List, create, generate
│   │   │   ├── 📄 actions.py           # Create, update, list
│   │   │   └── 📄 risks.py             # Create, approve, list
│   │   │
│   │   ├── 📁 models\                  # Database models
│   │   │   └── 📄 __init__.py          # All table definitions:
│   │   │                               # - Artifact, ArtifactChunk
│   │   │                               # - Control, Evidence
│   │   │                               # - Score, ScoreEvent
│   │   │                               # - Gap, Action, RiskAcceptance
│   │   │
│   │   ├── 📁 services\                # Business logic layer
│   │   │   ├── 📄 artifact_service.py  # File storage, URL fetching, hashing
│   │   │   ├── 📄 candidate_service.py # Evidence matching engine (EPIC 3)
│   │   │   ├── 📄 scoring_service.py   # Score calculation and rollups
│   │   │   └── 📄 gap_service.py       # Gap identification
│   │   │
│   │   ├── 📁 parsers\                 # Document parsing
│   │   │   └── 📄 parser_service.py    # DOCX, PDF, TXT, MD, XLSX, URL parsers
│   │   │
│   │   ├── 📄 config.py                # Settings and environment config
│   │   ├── 📄 database.py              # SQLModel engine and session
│   │   ├── 📄 main.py                  # FastAPI application
│   │   ├── 📄 init_db.py               # Database table creation
│   │   └── 📄 seed_controls.py         # NIST CSF control seeding
│   │
│   ├── 📁 alembic\                     # Database migrations (future)
│   │   └── (empty - migrations not yet implemented)
│   │
│   ├── 📄 requirements.txt             # Python dependencies:
│   │                                   # - fastapi, uvicorn, sqlmodel
│   │                                   # - python-docx, pypdf, beautifulsoup4
│   │                                   # - reportlab, requests
│   │
│   ├── 📄 .env.example                 # Environment template
│   └── 📄 .env                         # Local config (created by setup)
│
├── 📁 frontend\                        # React TypeScript frontend
│   ├── 📁 src\
│   │   ├── 📁 pages\                   # React page components
│   │   │   ├── 📄 Dashboard.tsx        # Overall stats, function rollups
│   │   │   ├── 📄 Artifacts.tsx        # Upload, ingest, list, viewer
│   │   │   ├── 📄 Controls.tsx         # Browse controls by function
│   │   │   ├── 📄 ControlDetail.tsx    # Validation workspace (EPIC 4)
│   │   │   └── 📄 ValidationQueue.tsx  # Bulk validation queue
│   │   │
│   │   ├── 📁 services\                # API client layer
│   │   │   └── 📄 api.ts               # Axios client + TypeScript types
│   │   │
│   │   ├── 📄 App.tsx                  # Main app component + routing
│   │   ├── 📄 App.css                  # App-specific styles
│   │   ├── 📄 main.tsx                 # React entry point
│   │   └── 📄 index.css                # Global styles + utility classes
│   │
│   ├── 📄 index.html                   # HTML template
│   ├── 📄 package.json                 # Node dependencies:
│   │                                   # - react, react-router-dom
│   │                                   # - axios, @tanstack/react-query
│   │                                   # - lucide-react, vite
│   │
│   ├── 📄 vite.config.ts               # Vite build configuration
│   ├── 📄 tsconfig.json                # TypeScript configuration
│   └── 📄 tsconfig.node.json           # TypeScript for Vite
│
├── 📁 data\                            # Local data storage
│   ├── 📁 artifacts\                   # Uploaded files + URL snapshots
│   │   └── 📄 .gitkeep                 # Keep folder in git
│   │
│   └── 📄 nist_csf_tracker.db          # SQLite database (created on init)
│
└── 📁 scripts\                         # Automation scripts
    ├── 📄 dev.ps1                      # One-command dev startup
    └── 📄 setup.ps1                    # Initial setup automation
```

---

## 📊 File Statistics

### Backend
- **Total Files**: 15 Python files
- **Lines of Code**: ~3,500
- **API Endpoints**: 35+
- **Database Tables**: 9
- **Dependencies**: 15 packages

### Frontend
- **Total Files**: 8 TypeScript/TSX files
- **Lines of Code**: ~2,000
- **Pages**: 5
- **Dependencies**: 10 packages

### Documentation
- **Total Files**: 3 markdown files
- **Total Documentation**: ~1,500 lines

---

## 🎯 Key File Purposes

### Backend Core Files

| File | Purpose | Lines |
|------|---------|-------|
| `main.py` | FastAPI app initialization, CORS, route registration | ~50 |
| `config.py` | Environment settings, path resolution | ~50 |
| `database.py` | SQLModel engine, session dependency | ~20 |
| `models/__init__.py` | 9 table definitions with relationships | ~250 |
| `init_db.py` | Database table creation script | ~30 |
| `seed_controls.py` | NIST CSF control data seeding | ~250 |

### Backend API Files

| File | Endpoints | Purpose |
|------|-----------|---------|
| `api/artifacts.py` | 6 | Upload, ingest URL, list, get, delete, chunks |
| `api/controls.py` | 7 | List, get, evidence, candidates, score, summaries |
| `api/evidence.py` | 5 | List, get, create, validate, delete |
| `api/scores.py` | 4 | List, recalculate, dashboard, history |
| `api/gaps.py` | 3 | List, create, generate |
| `api/actions.py` | 3 | List, create, update |
| `api/risks.py` | 3 | List, create, approve |

### Backend Service Files

| File | Responsibility | Key Methods |
|------|----------------|-------------|
| `services/artifact_service.py` | File storage, URL fetching | `save_file()`, `ingest_url()`, `delete_file()` |
| `services/candidate_service.py` | Evidence matching | `find_candidates()`, `_score_chunk()`, `_score_category_patterns()` |
| `services/scoring_service.py` | Score calculation | `calculate_control_score()`, `get_function_rollups()`, `get_category_rollups()` |
| `services/gap_service.py` | Gap identification | `generate_gaps()` |

### Backend Parser Files

| File | Supported Types | Key Methods |
|------|-----------------|-------------|
| `parsers/parser_service.py` | DOCX, PDF, TXT, MD, XLSX, URL | `parse_and_chunk()`, `_parse_docx()`, `_parse_pdf()`, etc. |

### Frontend Core Files

| File | Purpose | Components |
|------|---------|------------|
| `App.tsx` | Main app, routing, navigation | 1 main component |
| `main.tsx` | React entry, QueryClient setup | Entry point |
| `services/api.ts` | API client, TypeScript types | 7 API modules |

### Frontend Page Files

| File | Route | Purpose | Lines |
|------|-------|---------|-------|
| `Dashboard.tsx` | `/` | Overall stats, function rollups | ~150 |
| `Artifacts.tsx` | `/artifacts` | Upload, ingest, list, viewer | ~350 |
| `Controls.tsx` | `/controls` | Browse controls by function | ~100 |
| `ControlDetail.tsx` | `/controls/:id` | Validation workspace | ~400 |
| `ValidationQueue.tsx` | `/validation` | Bulk validation queue | ~150 |

---

## 🔗 File Dependencies

### Backend Dependency Graph

```
main.py
├── config.py
├── database.py
├── models/__init__.py
└── api/
    ├── artifacts.py
    │   ├── services/artifact_service.py
    │   └── parsers/parser_service.py
    ├── controls.py
    │   ├── services/candidate_service.py
    │   └── services/scoring_service.py
    ├── evidence.py
    │   └── services/scoring_service.py
    ├── scores.py
    │   └── services/scoring_service.py
    └── gaps.py
        └── services/gap_service.py
```

### Frontend Dependency Graph

```
main.tsx
└── App.tsx
    ├── services/api.ts
    └── pages/
        ├── Dashboard.tsx
        │   └── api.ts (scoreApi, artifactApi, controlApi, evidenceApi)
        ├── Artifacts.tsx
        │   └── api.ts (artifactApi)
        ├── Controls.tsx
        │   └── api.ts (controlApi)
        ├── ControlDetail.tsx
        │   └── api.ts (controlApi, evidenceApi)
        └── ValidationQueue.tsx
            └── api.ts (evidenceApi, controlApi)
```

---

## 📦 External Dependencies

### Backend (Python)

| Package | Version | Purpose |
|---------|---------|---------|
| fastapi | 0.109.0 | Web framework |
| uvicorn | 0.27.0 | ASGI server |
| sqlmodel | 0.0.14 | ORM (SQLAlchemy + Pydantic) |
| python-docx | 1.1.0 | DOCX parsing |
| pypdf | 4.0.1 | PDF parsing |
| beautifulsoup4 | 4.12.3 | HTML parsing |
| readability-lxml | 0.8.1 | URL content extraction |
| openpyxl | 3.1.2 | Excel parsing |
| requests | 2.31.0 | HTTP client |
| reportlab | 4.0.9 | PDF generation (future) |
| pydantic-settings | 2.1.0 | Settings management |
| python-multipart | 0.0.6 | File upload handling |
| alembic | 1.13.1 | Database migrations (future) |

### Frontend (Node.js)

| Package | Version | Purpose |
|---------|---------|---------|
| react | 18.2.0 | UI framework |
| react-dom | 18.2.0 | React DOM rendering |
| react-router-dom | 6.21.0 | Routing |
| axios | 1.6.5 | HTTP client |
| @tanstack/react-query | 5.17.9 | Data fetching + caching |
| lucide-react | 0.309.0 | Icon library |
| vite | 5.0.11 | Build tool |
| typescript | 5.3.3 | Type safety |

---

## 🔐 Security Considerations

### Current State (Local-Only)
- No authentication/authorization
- No encryption at rest
- No input sanitization beyond framework defaults
- CORS restricted to localhost

### Production Recommendations
1. Add user authentication (OAuth2/JWT)
2. Implement role-based access control
3. Enable HTTPS (TLS/SSL)
4. Sanitize user inputs
5. Encrypt sensitive data at rest
6. Add rate limiting
7. Implement audit logging
8. Regular security updates

---

## 🚀 Deployment Options (Future)

### Option 1: Desktop App (Electron)
- Package backend + frontend as Electron app
- SQLite remains local
- No server required
- Windows/Mac/Linux support

### Option 2: Docker Container
- Single docker-compose.yml
- SQLite in volume mount
- Expose only frontend port
- Easy deployment

### Option 3: Cloud Deployment
- Replace SQLite with PostgreSQL
- Add authentication layer
- Deploy backend to cloud (AWS/Azure/GCP)
- Deploy frontend to static hosting (Vercel/Netlify)
- Add S3 for artifact storage

---

## 📈 Growth Path

### Current Size
- **Total Project Size**: ~15 MB
- **Database**: Starts at ~1 MB, grows with data
- **Artifacts**: Grows with uploads
- **Dependencies**: ~500 MB (venv + node_modules)

### Scalability
- **SQLite limit**: ~140 TB (theoretical)
- **Practical limit**: 10,000s of artifacts before PostgreSQL recommended
- **Chunk limit**: Millions with proper indexing
- **Evidence limit**: 100,000s with current schema

---

## 🎓 Learning Resources

### Backend Technologies
- FastAPI docs: https://fastapi.tiangolo.com/
- SQLModel docs: https://sqlmodel.tiangolo.com/
- Python docx: https://python-docx.readthedocs.io/
- PyPDF: https://pypdf.readthedocs.io/

### Frontend Technologies
- React docs: https://react.dev/
- Vite docs: https://vitejs.dev/
- TanStack Query: https://tanstack.com/query/
- React Router: https://reactrouter.com/

### NIST CSF
- NIST CSF 2.0: https://www.nist.gov/cyberframework
- Control definitions: Official NIST documentation
- Implementation guidance: NIST publications

---

*Complete file structure as of implementation completion (EPIC 0-4)*
