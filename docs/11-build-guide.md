# 11 — Step-by-Step Build Guide

## Working rule

Complete one phase at a time. Do not ask an AI coding agent to build the whole application in one prompt. Each phase must have a visible result, relevant checks, a progress update, and a Git commit where appropriate.

## Phase tracker

- [x] **P00 — Scope freeze:** confirm MVP, limits, out-of-scope items, stack, and unresolved decisions.
- [x] **P01 — Repository structure:** create frontend/backend/docs structure and project conventions; no feature implementation yet.
- [ ] **P02 — Development environment:** pin supported runtime versions, dependency management, formatting/linting, test runners, and basic CI.
- [ ] **P03 — Database and storage:** define migrations, core tables, indexes, RLS/storage policies, and test ownership isolation.
- [ ] **P04 — Authentication:** integrate managed auth and server-side token verification; test invalid/expired sessions.
- [ ] **P05 — Workspace CRUD:** create/list/view/update/delete owned workspaces; test cross-user denial.
- [ ] **P06 — Upload and validation:** private file upload, format/size/quotas, document metadata, clear errors.
- [ ] **P07 — Durable ingestion jobs:** database-backed queue, claim/lease, retries, stale-job recovery, idempotency.
- [ ] **P08 — Parsing and chunking:** PDF/DOCX/TXT extraction, normalization, chunk IDs, parser tests.
- [ ] **P09 — Embeddings and vector search:** resource gate, model decision, indexing, authorized retrieval filters.
- [ ] **P10 — RAG answer generation:** relevance gate, LLM adapter, evidence-only prompt, citation validation, abstention.
- [ ] **P11 — History and deletion:** persist conversations/messages/citations; remove source and derived chunks safely.
- [ ] **P12 — Frontend workflow:** polished auth/workspace/upload/chat/citation/history/error states.
- [ ] **P13 — Security and quotas:** authorization matrix, rate limits, prompt-injection tests, secret/log review.
- [ ] **P14 — Evaluation and QA:** unit/integration/E2E, 30-case RAG evaluation, record measured metrics.
- [ ] **P15 — Free-tier deployment:** verify current limits, deploy, run smoke tests, document caveats.
- [ ] **P16 — Final acceptance:** demo walkthrough, README/setup, screenshots if desired, known limitations, final progress update.

## Phase exit rule

A phase is complete only when:
1. Its deliverable exists.
2. Relevant tests/checks were actually run.
3. Results and limitations are recorded.
4. The project remains runnable or the known blocker is documented.
5. `12-build-progress.md` is updated.
6. A meaningful Git commit is made when appropriate.

## P00 checklist

- [x] Confirm target: portfolio demo for approximately 2–4 users.
- [x] Confirm zero-budget constraint and no paid fallback.
- [x] Confirm supported file types and initial limits.
- [x] Confirm out-of-scope items.
- [x] Choose initial deployment candidates, with current free-tier checks deferred to P15.
- [x] Record unresolved decisions in `13-decisions.md`.
- [x] Mark P00 complete only after these items are explicitly reviewed.

## Recommended coding-session loop

1. Read `12-build-progress.md`.
2. Choose the single next unchecked task.
3. Inspect relevant files before editing.
4. Write a short implementation plan.
5. Make the smallest coherent change.
6. Run the relevant tests/checks.
7. Fix failures caused by the change.
8. Update progress and decision logs.
9. Commit the work.
10. Report exact status and next task.

## Resource gate for embeddings

Do not assume the baseline local embedding model fits a free host. Test it early enough to avoid reworking the architecture late. If it fails, compare a lighter ONNX/FastEmbed-compatible model, document dimensions and limitations, and rebuild the index consistently. Never mix incompatible vector dimensions/models.

## Final acceptance

See `16-acceptance-criteria.md`. P16 is not complete merely because the app starts; it requires the end-to-end journey, security isolation, citation integrity, and honest documentation of measured results.
