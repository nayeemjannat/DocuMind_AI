# 12 — Build Progress Tracker

**Last updated:** 2026-11-24  
**Current phase:** P09 — Embeddings and vector search  
**Overall status:** Phases P00 through P08 completed and verified  
**Current blocker:** None  
**Next single task:** Phase P09: implement embedding generation (sentence-transformers / local model), vector indexing, and authorized similarity retrieval.

## Phase status

Use only: `Not started`, `In progress`, `Blocked`, `Done`.

| Phase | Status | Evidence / commit | Notes |
|---|---|---|---|
| P00 Scope freeze | Done | Initial setup | MVP scope, constraints, and architecture baseline confirmed |
| P01 Repository structure | Done | Frontend/Backend scaffold | Project layout, conventions, and baseline configs established |
| P02 Development environment | Done | Python 3.12 venv, CI | Pytest runner, environment config, and GitHub Actions CI workflow |
| P03 Database and storage | Done | Schema & models | Initial migration, pgvector index, RLS policies, SQLAlchemy models |
| P04 Authentication | Done | Auth tests passing | Server-side JWT token verification and user context dependency |
| P05 Workspace CRUD | Done | Workspace tests passing | Workspace CRUD API endpoints with strict tenant isolation (17/17 tests passing) |
| P06 Upload and validation | Done | Document tests passing | Private file upload, format/size validation, and metadata storage (22/22 tests passing) |
| P07 Durable ingestion jobs | Done | Queue tests passing | DB-backed queue, lease claiming, retry logic, and stale lease recovery (26/26 tests passing) |
| P08 Parsing and chunking | Done | Ingestion tests passing | PDF/DOCX/TXT text extraction, intelligent text chunker, and database chunk persistence (31/31 tests passing) |
| P09 Embeddings and vector search | In progress | — | Resource gate |
| P10 RAG answer generation | Not started | — | Grounding and citations |
| P11 History and deletion | Not started | — | Cascade and cleanup |
| P12 Frontend workflow | Not started | — | Main UI journey |
| P13 Security and quotas | Not started | — | Adversarial checks |
| P14 Evaluation and QA | Not started | — | 30-case evaluation |
| P15 Deployment | Not started | — | Current free-tier verification |
| P16 Final acceptance | Not started | — | Demo and handoff |

## Session log

### Session 8 — Ingestion Queue and Document Parsing (2026-11-24)
- Added `backend/app/services/queue.py` with atomic job leasing, stale recovery, retry limits, and status queries.
- Added `backend/app/schemas/job.py` and `backend/app/api/v1/jobs.py` (`GET /api/v1/jobs/{id}`).
- Added `backend/app/services/parser.py` supporting PDF (`pypdf`), DOCX (`python-docx`), and TXT.
- Added `backend/app/services/chunker.py` with natural sentence/word boundary chunking and overlap.
- Added `backend/app/services/ingestion.py` executing full document processing and chunk persistence.
- Added test suites in `backend/tests/test_queue.py` and `backend/tests/test_ingestion.py`.
- All 31 automated tests passing.
- Next task: Vector embeddings generation and similarity search.

### Session 7 — Document Upload and Validation (2026-11-24)
- Added `backend/app/schemas/document.py` (`DocumentResponse`, `DocumentUploadResponse`).
- Added `backend/app/services/storage.py` private file storage handler.
- Added `backend/app/services/document.py` with validation (PDF, DOCX, TXT only, 5 MB limit, safe filename sanitization) and queuing.
- Added `backend/app/api/v1/documents.py` with REST endpoints:
  - `POST /api/v1/workspaces/{workspace_id}/documents`: upload document and enqueue job
  - `GET /api/v1/workspaces/{workspace_id}/documents`: list workspace documents
  - `GET /api/v1/documents/{document_id}`: get document metadata
  - `DELETE /api/v1/documents/{document_id}`: delete document and file
- Added `backend/tests/conftest.py` with shared test database fixture.
- Added `backend/tests/test_documents.py` verifying file type filtering, size caps, and cross-user isolation.
- All 22 tests passing.
- Next task: Ingestion job queue worker and lease recovery.

### Session 6 — Workspace CRUD and Multi-tenant Isolation (2026-11-02)
- Added `backend/app/schemas/workspace.py` (WorkspaceCreate, WorkspaceUpdate, WorkspaceResponse).
- Added `backend/app/services/workspace.py` with CRUD queries scoped to `owner_id`.
- Added `backend/app/api/v1/workspaces.py` with standard REST endpoints:
  - `POST /api/v1/workspaces`: create workspace
  - `GET /api/v1/workspaces`: list user workspaces
  - `GET /api/v1/workspaces/{id}`: get workspace details (404 on unowned)
  - `PATCH /api/v1/workspaces/{id}`: update workspace name
  - `DELETE /api/v1/workspaces/{id}`: cascade delete workspace
- Added comprehensive integration tests in `backend/tests/test_workspaces.py`.
- Verified cross-user isolation: User B cannot read, update, or delete User A's workspaces.
- All 17 automated tests passing.
- Next task: Document upload and format/size validation.
- Implemented `backend/app/core/security.py`:
  - `AuthenticatedUser` model.
  - `verify_token`: decodes Supabase JWT, validates expiration, subject UUID, and signature.
  - `get_current_user`: FastAPI dependency using `HTTPBearer`.
- Added `GET /api/v1/auth/me` route in `backend/app/api/v1/auth.py`.
- Implemented automated security test suite in `backend/tests/test_auth.py`:
  - Missing token -> 401 Unauthorized
  - Invalid token -> 401 Unauthorized
  - Untrusted secret token -> 401 Unauthorized
  - Expired token -> 401 Unauthorized
  - Valid token -> 200 OK with authenticated user context
- All 12 test cases in the test suite passed.
- Updated `11-build-guide.md` and `12-build-progress.md`.
- Next task: Phase P05 — Workspace CRUD and ownership isolation tests.

### Session 4 — P03 Database and Storage Schema Completed (2026-10-30)
- Created Supabase PostgreSQL migration (`supabase/migrations/20261030000000_initial_schema.sql`):
  - Extensions: `uuid-ossp`, `vector`.
  - Tables: `profiles`, `workspaces`, `documents`, `document_chunks` (vector 384), `ingestion_jobs`, `conversations`, `messages`.
  - HNSW vector index for cosine similarity.
  - Row Level Security (RLS) policies for user isolation across all tables.
  - Private storage bucket `documind-documents` and RLS policy for document files.
- Implemented SQLAlchemy declarative models in `backend/app/models/` (`base.py`, `workspace.py`, `document.py`, `chunk.py`, `job.py`, `chat.py`).
- Added database session generator in `backend/app/db/session.py`.
- Created and executed model unit tests in `backend/tests/test_models.py` (all 7 tests passed).
- Updated `11-build-guide.md` and `12-build-progress.md`.
- Next task: Phase P04 — Authentication and server-side token verification.

### Session 3 — P02 Development Environment Completed (2026-10-30)
- Configured Python 3.12 virtual environment at `backend/.venv`.
- Installed base dependencies (`fastapi`, `uvicorn`, `pydantic-settings`, `pytest`, `httpx`).
- Configured `backend/pytest.ini`.
- Executed `pytest` successfully (`test_liveness`, `test_readiness` — 2 passed).
- Added GitHub Actions workflow `.github/workflows/ci.yml` for automated test runs.
- Updated `11-build-guide.md` and `12-build-progress.md`.
- Next task: Phase P03 — Database schema and storage policies.

### Session 2 — P01 Repository Structure Completed (2026-10-30)
- Created `backend/` structure: `app/core/config.py`, `app/api/v1/health.py`, `app/main.py`, `tests/test_health.py`, `requirements.txt`, `.env.example`, `README.md`.
- Created `frontend/` structure: Next.js App Router scaffold (`src/app/page.tsx`, `layout.tsx`, `types/index.ts`, `package.json`, `tsconfig.json`, `.env.example`, `README.md`).
- Created root `.env.example` and `docs/19-project-conventions.md`.
- Updated `11-build-guide.md` and `12-build-progress.md`.
- Next task: Phase P02 — setup Python 3.12 venv, install backend dependencies, and run tests.

### Session 1 — P00 Scope freeze completed & Git initialized (2026-10-30)
- Initialized Git version control repository.
- Created root `.gitignore` covering Python, Node.js, Next.js, and secrets.
- Completed P00 scope freeze checklist: portfolio demo for ~2–4 users, BDT 0 constraint, PDF/DOCX/TXT support with 5 MB limits, Supabase + Next.js + FastAPI + Gemini stack.
- Recorded Decision D-009 in `13-decisions.md`.
- Updated `11-build-guide.md` and `12-build-progress.md`.
- Next task: Setup Phase P01 repository directory layout.

### Session 0 — Documentation pack prepared
- Created project documentation starter pack.
- No application code was written or tested.
- No deployment has been performed.
- No performance or RAG evaluation metrics have been measured.
- Next task: confirm P00 scope and update decisions.

## Update protocol

At the end of every coding session, update:
- Current phase and exact next task.
- Status of each touched phase.
- Files changed.
- Commands/tests actually run and outcomes.
- Known failures, risks, and blockers.
- Git commit hash if available.
- Next single action.

Never mark a phase `Done` based on generated code alone.
