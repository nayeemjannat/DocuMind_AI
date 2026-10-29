# 13 — Decision Log

Use this file to record decisions that materially affect product scope, architecture, security, data, or deployment. Newest decisions should be added at the top.

## Decision record template

- **ID:**
- **Date:**
- **Status:** Proposed / Accepted / Superseded
- **Context:**
- **Decision:**
- **Alternatives considered:**
- **Consequences / trade-offs:**
- **Validation required:**

---

## Initial baseline decisions

### D-001 — Keep the MVP small
- **Status:** Accepted baseline
- **Decision:** Build a portfolio demo for approximately 2–4 users, not an enterprise platform.
- **Consequence:** Exclude billing, OCR, team sharing, and high-concurrency design.

### D-002 — Zero-budget initial deployment
- **Status:** Accepted baseline
- **Decision:** Initial budget is BDT 0; no paid fallback.
- **Consequence:** Current free-tier limitations must be verified; uptime and quotas cannot be promised.

### D-003 — One frontend, one API, one worker
- **Status:** Accepted baseline
- **Decision:** Prefer Next.js/TypeScript, FastAPI, and a small worker with managed PostgreSQL/storage.
- **Consequence:** Avoid unnecessary microservices.

### D-004 — Private-by-default documents
- **Status:** Accepted baseline
- **Decision:** Original files and extracted chunks are private to the owner.
- **Consequence:** Every nested resource access and vector query must enforce ownership.

### D-005 — Citations must be validated
- **Status:** Accepted baseline
- **Decision:** The application validates citation references against the actual retrieved chunk set.
- **Consequence:** Free-form model citations cannot be trusted without validation.

### D-006 — Embedding model is conditional
- **Status:** Proposed pending resource test
- **Decision:** Start by testing `sentence-transformers/all-MiniLM-L6-v2` (384 dimensions); switch only if resource constraints require it.
- **Validation required:** Measure memory/CPU/startup on the target host. If changed, document model and re-index consistently.

### D-007 — LLM provider is not yet locked
- **Status:** Proposed
- **Decision:** Choose a provider with a usable free tier at implementation time; no paid fallback.
- **Validation required:** Check current quotas, model access, terms, latency, and data handling before deployment.

### D-008 — Initial product limits
- **Status:** Accepted baseline
- **Decision:** 5 MB/file, 30 pages/document where count is available, 5 documents/account, 5 uploads/day, 20 questions/day, one active ingestion job/account.
- **Consequence:** Make limits configurable and return helpful limit errors.

### D-009 — Phase P00 MVP Scope Freeze Confirmed
- **Date:** 2026-10-30
- **Status:** Accepted
- **Decision:** Confirmed MVP scope, constraints, and baseline architecture:
  - **Target:** Portfolio demo for 2–4 users.
  - **Budget:** BDT 0 constraint; free tiers only with no paid fallbacks.
  - **Supported Formats & Limits:** PDF, DOCX, TXT; 5 MB/file, 30 pages/document, 5 documents/account, 5 uploads/day, 20 questions/day, 1 active ingestion job/account.
  - **Explicitly Out of Scope:** OCR for scanned images, billing/subscriptions, team collaboration/shared workspaces, complex role hierarchies, model fine-tuning, enterprise SLA.
  - **Baseline Stack:** Next.js + TypeScript (frontend), Python + FastAPI (API/worker), Supabase (PostgreSQL + pgvector + Auth + Storage), Google Gemini API (free tier LLM).
- **Consequences:** Implementation strictly follows this boundary; no premature microservices or unpaid external dependencies.

## Pending decisions

- Workspace deletion: hard delete, soft delete, or cascade policy.
- Conversation behavior after a source document is deleted.
- Exact citation presentation for each file format.
- Chosen embedding implementation after resource testing.
- Chosen LLM provider/model after current free-tier review.
- Final hosting topology based on resource tests.
- Whether public demo access requires invite/sign-in or uses a seeded synthetic demo account.
