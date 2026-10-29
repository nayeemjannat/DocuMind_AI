# 12 — Build Progress Tracker

**Last updated:** 2026-10-30  
**Current phase:** P03 — Database and storage  
**Overall status:** P00, P01, P02 Complete (Environment configured, test suite active, CI established)  
**Current blocker:** None  
**Next single task:** Phase P03: define database schema (PostgreSQL + pgvector), migrations, storage buckets, and RLS policies.

## Phase status

Use only: `Not started`, `In progress`, `Blocked`, `Done`.

| Phase | Status | Evidence / commit | Notes |
|---|---|---|---|
| P00 Scope freeze | Done | Commit `53e0dbc`, D-009 | Scope, limits, out-of-scope, and zero-budget constraint confirmed |
| P01 Repository structure | Done | Commit `0af72f0` | Created `backend/` (FastAPI), `frontend/` (Next.js), `.env.example`, conventions |
| P02 Development environment | Done | Python 3.12 venv, tests passing | `pytest` runner active (2/2 passing), `.github/workflows/ci.yml` added |
| P03 Database and storage | In progress | — | Schema, policies, migrations |
| P04 Authentication | Not started | — | Server-side verification |
| P05 Workspace CRUD | Not started | — | Ownership tests |
| P06 Upload and validation | Not started | — | Private storage |
| P07 Durable ingestion jobs | Not started | — | DB-backed queue |
| P08 Parsing and chunking | Not started | — | PDF/DOCX/TXT |
| P09 Embeddings and vector search | Not started | — | Resource gate |
| P10 RAG answer generation | Not started | — | Grounding and citations |
| P11 History and deletion | Not started | — | Cascade and cleanup |
| P12 Frontend workflow | Not started | — | Main UI journey |
| P13 Security and quotas | Not started | — | Adversarial checks |
| P14 Evaluation and QA | Not started | — | 30-case evaluation |
| P15 Deployment | Not started | — | Current free-tier verification |
| P16 Final acceptance | Not started | — | Demo and handoff |

## Session log

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
