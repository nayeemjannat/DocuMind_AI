# DocuMind AI — Deployment Guide

## Gate A — Local Baseline (Completed ✓)

This is the current deployment gate. The app runs entirely locally with an in-memory SQLite test database.

### Prerequisites

- Python 3.12+
- Node.js 18+
- pnpm or npm
- Git

### Backend setup

```bash
cd backend
python -m venv .venv

# Windows
.\.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
```

Create your `.env` file:

```bash
cp .env.example .env
# Edit .env and fill in your Supabase and Gemini credentials
```

Run the backend server:

```bash
uvicorn app.main:app --reload --port 8000
```

Run the full test suite (must all pass before any commit):

```bash
cd backend
python -m pytest -v
```

### Frontend setup

```bash
cd frontend
npm install          # or: pnpm install
cp .env.local.example .env.local
# Edit .env.local if your backend runs on a different port
npm run dev
```

The frontend runs at http://localhost:3000.

---

## Gate B — Database and Storage (Requires Supabase account)

### 1. Create a Supabase project

Go to https://supabase.com and create a free project. Note your project ref, region, and database password.

### 2. Apply the database migration

In the Supabase SQL editor, run the contents of:

```
supabase/migrations/20261030000000_initial_schema.sql
```

This creates all tables (`profiles`, `workspaces`, `documents`, `document_chunks`, `ingestion_jobs`, `conversations`, `messages`), the HNSW vector index, and RLS policies.

### 3. Create the storage bucket

In Supabase → Storage, create a **private** bucket named `documind-documents`.

Add a storage policy so users can only access their own files. Use the policy template from `supabase/migrations/`.

### 4. Configure environment variables

Fill in `backend/.env` with your Supabase project credentials:

```
SUPABASE_URL=https://your-project-ref.supabase.co
SUPABASE_ANON_KEY=...
SUPABASE_SERVICE_ROLE_KEY=...
SUPABASE_JWT_SECRET=...
DATABASE_URL=postgresql://...
```

---

## Gate C — Host Resource Test (Render Free Tier)

### Backend on Render

1. Create a free Web Service on https://render.com
2. Connect your GitHub repository
3. Set build command: `pip install -r backend/requirements.txt`
4. Set start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Set root directory: `backend`
6. Add all environment variables from `backend/.env.example` in the Render dashboard

**Free tier caveats:**
- Render Free spins down after 15 minutes of inactivity (cold-start ~30s)
- 512 MB RAM — the hash-based embedding model fits comfortably; `sentence-transformers` may require the Starter plan
- CPU is shared; ingestion jobs may be slow on burst

### Worker process

For the ingestion background worker, add a second Render service pointing to:

```bash
python -m app.worker
```

Or configure the worker to run inline with the web process for the free tier (single-process mode).

---

## Gate D — Public Deployment Checklist

Before going live:

- [ ] All environment variables set in hosting dashboards (never in `.env` committed to git)
- [ ] Database migration applied and verified
- [ ] Supabase Auth redirect URLs updated to production domain
- [ ] Supabase Auth email templates configured
- [ ] Storage bucket policies verified (private, owner-scoped)
- [ ] CORS origins updated to production frontend URL
- [ ] `ENVIRONMENT=production` and `DEBUG=False`
- [ ] Run smoke test: upload one PDF, ask one question, verify citation, ask unanswerable question
- [ ] Check logs: no secrets, no document content, no stack traces leaked
- [ ] Confirm quota limits appropriate for expected usage

---

## Frontend on Vercel

1. Import your GitHub repository at https://vercel.com
2. Set framework preset to **Next.js**
3. Set root directory to `frontend`
4. Add environment variables from `frontend/.env.local.example`:
   - `NEXT_PUBLIC_SUPABASE_URL`
   - `NEXT_PUBLIC_SUPABASE_ANON_KEY`
   - `NEXT_PUBLIC_API_BASE_URL` (your Render backend URL)

---

## Free-tier caveats summary

| Service | Limitation | Impact |
|---|---|---|
| Render Free | Sleeps after 15 min idle | ~30s cold-start on first request |
| Supabase Free | 500 MB database, 1 GB storage | Sufficient for portfolio demo |
| Gemini API Free | 15 requests/min, 1 million tokens/day | Sufficient for small usage; app falls back gracefully |
| Vercel Hobby | 100 GB bandwidth/month | More than sufficient |

The app is designed to degrade gracefully: if the Gemini API is unavailable or quota-exceeded, the built-in grounded synthesizer answers directly from document excerpts.

---

## Secrets policy

- `.env` and `.env.local` are in `.gitignore` and must never be committed
- Only `.env.example` and `.env.local.example` (with placeholder values) are version-controlled
- Server-only secrets (`SUPABASE_SERVICE_ROLE_KEY`, `SUPABASE_JWT_SECRET`, `GEMINI_API_KEY`, `DATABASE_URL`) must never be prefixed with `NEXT_PUBLIC_`
- Rotate any key that is accidentally committed immediately
