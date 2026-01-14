# NIST CSF Tracker - System Architecture & Data Flow

## 🏗️ High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER BROWSER                             │
│                     http://localhost:5173                        │
└────────────────────────────┬────────────────────────────────────┘
                             │
                    React Frontend (Vite)
                             │
         ┌───────────────────┼───────────────────┐
         │                   │                   │
    Dashboard          Artifacts            Controls
         │                   │                   │
         └───────────────────┴───────────────────┘
                             │
                     TanStack Query
                      (Data Layer)
                             │
                        Axios HTTP
                             │
┌────────────────────────────┴────────────────────────────────────┐
│                    FastAPI Backend                               │
│                  http://localhost:8000                           │
│                                                                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │ Artifacts│  │ Controls │  │ Evidence │  │  Scores  │       │
│  │   API    │  │   API    │  │   API    │  │   API    │       │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘       │
│       │             │              │             │              │
│  ┌────┴────┐   ┌───┴──────┐  ┌───┴──────┐ ┌───┴──────┐       │
│  │Artifact │   │Candidate │  │ Scoring  │ │   Gap    │       │
│  │Service  │   │Service   │  │ Service  │ │ Service  │       │
│  └────┬────┘   └────┬─────┘  └────┬─────┘ └──────────┘       │
│       │             │              │                            │
│  ┌────┴────┐   ┌───┴──────┐       │                           │
│  │ Parser  │   │ Matching │       │                           │
│  │Service  │   │  Engine  │       │                           │
│  └────┬────┘   └────┬─────┘       │                           │
│       │             │              │                            │
└───────┼─────────────┼──────────────┼────────────────────────────┘
        │             │              │
        │             └──────┬───────┘
        │                    │
┌───────┴────────────────────┴────────────────────────────────────┐
│                      SQLModel ORM                                │
└───────────────────────────┬──────────────────────────────────────┘
                            │
┌───────────────────────────┴──────────────────────────────────────┐
│                    SQLite Database                                │
│                  data/nist_csf_tracker.db                        │
│                                                                  │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐          │
│  │Artifacts │ │  Chunks  │ │ Controls │ │ Evidence │          │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘          │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐          │
│  │  Scores  │ │   Gaps   │ │ Actions  │ │  Risks   │          │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘          │
│  ┌──────────┐                                                   │
│  │Score     │                                                   │
│  │Events    │                                                   │
│  └──────────┘                                                   │
└──────────────────────────────────────────────────────────────────┘
        │
        └──────────────────────────────────────────────┐
                                                        │
┌───────────────────────────────────────────────────────┴──────────┐
│                    File System Storage                            │
│                    data/artifacts/                                │
│                                                                   │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │ DOCX Files  │  │  PDF Files  │  │  TXT Files  │             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
│  ┌─────────────┐  ┌─────────────┐                               │
│  │ URL Snapshots│  │ XLSX Files │                               │
│  └─────────────┘  └─────────────┘                               │
└───────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Data Flow: Artifact Ingestion

```
┌──────────────┐
│     User     │
│ Uploads File │
└──────┬───────┘
       │
       ▼
┌──────────────────────┐
│  Frontend: Upload    │
│  Form with File      │
└──────┬───────────────┘
       │ POST /api/artifacts/upload
       │ (multipart/form-data)
       ▼
┌──────────────────────┐
│  Backend: Artifacts  │
│  API Endpoint        │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│  ArtifactService     │
│  .save_file()        │
│  - Hash content      │
│  - Store to disk     │
│  - Create DB record  │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│  ParserService       │
│  .parse_and_chunk()  │
│  - Route by type     │
│  - Extract text      │
│  - Create chunks     │
│  - Add locators      │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│  Database            │
│  - Insert Artifact   │
│  - Insert Chunks     │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│  Frontend: Success   │
│  Refresh Artifact    │
│  List                │
└──────────────────────┘
```

---

## 🎯 Data Flow: Evidence Candidate Detection

```
┌──────────────┐
│     User     │
│ Views Control│
└──────┬───────┘
       │
       ▼
┌──────────────────────┐
│  Frontend: Control   │
│  Detail Page         │
└──────┬───────────────┘
       │ GET /api/controls/{id}/candidates
       │
       ▼
┌──────────────────────┐
│  Backend: Controls   │
│  API Endpoint        │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│  CandidateService    │
│  .find_candidates()  │
└──────┬───────────────┘
       │
       ▼ For each chunk
┌──────────────────────┐
│  Scoring Engine      │
│  ._score_chunk()     │
│                      │
│  1. Control ID match │
│  2. Name keywords    │
│  3. Custom keywords  │
│  4. Function terms   │
│  5. Category patterns│
│  6. Locator bonus    │
└──────┬───────────────┘
       │
       ▼ Sort by score
┌──────────────────────┐
│  Top N Candidates    │
│  - Chunk text        │
│  - Locator info      │
│  - Match reasons     │
│  - Score             │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│  Frontend: Display   │
│  Ranked List         │
└──────────────────────┘
```

---

## ✅ Data Flow: Evidence Validation

```
┌──────────────┐
│     User     │
│ Clicks Review│
└──────┬───────┘
       │
       ▼
┌──────────────────────┐
│  Frontend: Modal     │
│  - Show full text    │
│  - Show locator      │
│  - Evidence type     │
│  - Notes field       │
└──────┬───────────────┘
       │
       │ User clicks "Accept"
       ▼
       │ POST /api/evidence/
       │ (create evidence)
┌──────┴───────────────┐
│  Backend: Evidence   │
│  API - Create        │
│  - Save to DB        │
│  - Status: pending   │
└──────┬───────────────┘
       │
       │ PATCH /api/evidence/{id}/validate
       │ (validate evidence)
       ▼
┌──────────────────────┐
│  Backend: Evidence   │
│  API - Validate      │
│  - Update status     │
│  - Add notes         │
│  - Set timestamp     │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│  ScoringService      │
│  .calculate_control_ │
│  score()             │
│                      │
│  1. Get evidence     │
│  2. Count types      │
│  3. Determine score  │
│  4. Log change       │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│  Database            │
│  - Update Evidence   │
│  - Update Score      │
│  - Insert ScoreEvent │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│  Frontend: Update    │
│  - Refresh score     │
│  - Update candidate  │
│    list              │
│  - Show success      │
└──────────────────────┘
```

---

## 📊 Data Flow: Dashboard Rollups

```
┌──────────────┐
│     User     │
│ Views        │
│ Dashboard    │
└──────┬───────┘
       │
       ▼
┌──────────────────────┐
│  Frontend: Dashboard │
│  Component           │
└──────┬───────────────┘
       │ GET /api/scores/dashboard
       │
       ▼
┌──────────────────────┐
│  Backend: Scores     │
│  API - Dashboard     │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│  ScoringService      │
│                      │
│  .get_overall_score()│
│  .get_function_      │
│   rollups()          │
│  .get_category_      │
│   rollups()          │
└──────┬───────────────┘
       │
       ▼ Query database
┌──────────────────────┐
│  Database Queries    │
│  - All controls      │
│  - All scores        │
│  - Group by function │
│  - Group by category │
│  - Calculate avgs    │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│  Computed Results    │
│  - Overall %         │
│  - Per function      │
│  - Per category      │
│  - Pending count     │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│  Frontend: Display   │
│  - Stats cards       │
│  - Function table    │
│  - Progress bars     │
└──────────────────────┘
```

---

## 🗃️ Database Schema Relationships

```
┌─────────────┐
│  Artifact   │
│─────────────│
│ id (PK)     │
│ title       │
│ type        │
│ source_path │
│ hash        │
└──────┬──────┘
       │ 1
       │
       │ N
       ▼
┌─────────────┐        ┌─────────────┐
│Artifact     │        │  Control    │
│Chunk        │        │─────────────│
│─────────────│        │ id (PK)     │
│ id (PK)     │        │ csf_id      │
│ artifact_id │        │ function    │
│ chunk_text  │        │ category    │
│ locator_json│        │ name        │
└──────┬──────┘        └──────┬──────┘
       │                      │ 1
       │ 1                    │
       │                      │ N
       │                      ▼
       │              ┌─────────────┐
       │              │  Evidence   │
       │              │─────────────│
       │              │ id (PK)     │
       ├──────────────┤ control_id  │
       │ (via FK)     │ artifact_id │
       └──────────────┤ chunk_id    │
                      │ status      │
                      │ evidence_   │
                      │  type       │
                      └──────┬──────┘
                             │
                             │ Used by
                             ▼
                      ┌─────────────┐
                      │   Score     │
                      │─────────────│
                      │ id (PK)     │
                      │ control_id  │─────┐
                      │ score_value │     │
                      │ score_label │     │ 1
                      └─────────────┘     │
                                          │
                                          │ N
                                          ▼
                                   ┌─────────────┐
                                   │ ScoreEvent  │
                                   │─────────────│
                                   │ id (PK)     │
                                   │ control_id  │
                                   │ old_score   │
                                   │ new_score   │
                                   │ timestamp   │
                                   └─────────────┘

┌─────────────┐        ┌─────────────┐        ┌─────────────┐
│    Gap      │        │   Action    │        │    Risk     │
│─────────────│        │─────────────│        │ Acceptance  │
│ id (PK)     │        │ id (PK)     │        │─────────────│
│ control_id  │────┐   │ gap_id      │        │ id (PK)     │
│ gap_type    │    │   │ control_id  │        │ control_id  │
│ severity    │    └───│ title       │        │ risk_       │
│ status      │        │ status      │        │  statement  │
└─────────────┘        └─────────────┘        │ status      │
                                               └─────────────┘
```

---

## 🔐 Security Layers

```
┌───────────────────────────────────────────────────────────┐
│                   Current Security (Local)                 │
├───────────────────────────────────────────────────────────┤
│  1. CORS: Restricted to localhost                         │
│  2. File validation: Extension checking                   │
│  3. Hash verification: SHA256 for deduplication           │
│  4. SQL injection: Prevented by SQLModel ORM              │
│  5. XSS: Prevented by React auto-escaping                 │
└───────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────┐
│              Future Security (Multi-User)                  │
├───────────────────────────────────────────────────────────┤
│  1. Authentication: OAuth2 + JWT tokens                   │
│  2. Authorization: Role-based access control              │
│  3. Encryption: TLS/HTTPS for all traffic                 │
│  4. Data encryption: At-rest encryption for sensitive data│
│  5. Audit logging: All actions tracked with user ID       │
│  6. Rate limiting: Prevent abuse                          │
│  7. Input sanitization: Strict validation                 │
│  8. Session management: Secure cookie handling            │
└───────────────────────────────────────────────────────────┘
```

---

## 📦 Deployment Architecture Options

### Current: Local Development
```
┌─────────────────────┐
│   Windows Machine   │
│                     │
│  ┌───────────────┐  │
│  │   Backend     │  │
│  │   :8000       │  │
│  └───────────────┘  │
│         │           │
│  ┌──────▼────────┐  │
│  │   SQLite DB   │  │
│  └───────────────┘  │
│         │           │
│  ┌──────▼────────┐  │
│  │  Artifacts    │  │
│  │  Folder       │  │
│  └───────────────┘  │
│                     │
│  ┌───────────────┐  │
│  │   Frontend    │  │
│  │   :5173       │  │
│  └───────────────┘  │
└─────────────────────┘
```

### Future: Docker Deployment
```
┌─────────────────────────────────────┐
│         Docker Host                 │
│                                     │
│  ┌──────────────────────────────┐  │
│  │   docker-compose.yml         │  │
│  └──────────────────────────────┘  │
│         │                           │
│  ┌──────┴────────┐                  │
│  │               │                  │
│  ▼               ▼                  │
│ ┌────────┐  ┌────────┐             │
│ │Backend │  │Frontend│             │
│ │Service │  │Service │             │
│ └───┬────┘  └────────┘             │
│     │                               │
│     ▼                               │
│ ┌────────────┐  ┌────────────┐     │
│ │  SQLite    │  │ Artifacts  │     │
│ │  Volume    │  │  Volume    │     │
│ └────────────┘  └────────────┘     │
└─────────────────────────────────────┘
```

### Future: Cloud Deployment
```
┌─────────────────────────────────────────────────┐
│              Cloud Provider (AWS/Azure)         │
│                                                 │
│  ┌──────────────┐                               │
│  │   CDN        │  Static Assets                │
│  │  (Frontend)  │                               │
│  └──────┬───────┘                               │
│         │                                       │
│         ▼                                       │
│  ┌──────────────┐                               │
│  │  Load        │                               │
│  │  Balancer    │                               │
│  └──────┬───────┘                               │
│         │                                       │
│  ┌──────┴───────┐                               │
│  │              │                               │
│  ▼              ▼                               │
│ ┌────┐        ┌────┐                            │
│ │API │        │API │  Backend Instances         │
│ │ 1  │        │ 2  │                            │
│ └─┬──┘        └─┬──┘                            │
│   │             │                               │
│   └──────┬──────┘                               │
│          │                                      │
│          ▼                                      │
│   ┌─────────────┐         ┌──────────────┐     │
│   │ PostgreSQL  │         │  S3 Bucket   │     │
│   │  Database   │         │  (Artifacts) │     │
│   └─────────────┘         └──────────────┘     │
└─────────────────────────────────────────────────┘
```

---

*Architecture documentation as of MVP completion (EPIC 0-4)*
