# 02 — System Architecture

## Intended stack

- **Frontend:** Next.js + TypeScript.
- **Backend API:** Python + FastAPI.
- **Database:** Supabase PostgreSQL, with pgvector if available in the selected plan.
- **File storage:** private Supabase Storage bucket or equivalent private object storage.
- **Authentication:** managed auth provider with server-side JWT/session verification.
- **Embeddings:** local sentence-transformer model initially, subject to memory/CPU validation; candidate baseline `sentence-transformers/all-MiniLM-L6-v2` (384 dimensions).
- **LLM:** one provider with an available free tier at implementation time. No paid fallback.
- **Worker:** a small Python worker that reads persistent jobs from the database.
- **Hosting:** choose free tiers that can actually run the app; validate current limits before deployment.

## Logical components

1. **Web UI** — authentication screens, workspaces, uploads, job status, chat, citations, history, and deletion.
2. **API** — identity verification, authorization, validation, business rules, upload orchestration, retrieval, LLM calls, and history.
3. **Ingestion worker** — claims durable jobs, parses documents, chunks text, embeds chunks, and updates job state.
4. **PostgreSQL + pgvector** — users/profile mapping, workspaces, documents, chunks/embeddings, conversations, messages, and jobs.
5. **Private object storage** — original uploaded files.
6. **External LLM provider** — answer generation only; send the minimum retrieved excerpts required.

## Request boundaries

- The browser must never receive a service-role key, database password, provider secret, or unrestricted storage credential.
- The frontend calls the API using the user's authenticated session/token.
- The API verifies identity and checks ownership before reading or changing a private resource.
- The worker uses a restricted server-side identity and processes only jobs it has claimed.
- The API and worker should share validation and domain logic where practical, without coupling core business rules to UI code.

## Data flow: upload and indexing

1. API authenticates the user and validates workspace ownership.
2. API validates file policy and writes the file to private storage.
3. API creates a document row and durable ingestion job.
4. Worker claims a queued job with a lease/claim timestamp.
5. Worker downloads the private file using server-side access.
6. Parser extracts text and page metadata where available.
7. Text is normalized and chunked with stable chunk identifiers.
8. Worker creates embeddings and inserts chunks with document/workspace/owner linkage.
9. Worker marks the document and job ready, or records a bounded failure.
10. A retry or restart must not duplicate chunks or corrupt job state.

## Data flow: question answering

1. API authenticates user and checks workspace/conversation ownership.
2. API embeds the question using the same model used for chunks.
3. Vector search filters by the authorized workspace/document scope before returning results.
4. Relevance gate determines whether sufficient evidence exists.
5. LLM receives a fixed instruction plus bounded retrieved excerpts and the question.
6. Response is validated; citations must map to retrieved chunk IDs.
7. API persists the user message, answer, and citation metadata.
8. UI displays answer and source references.

## Deployment shape

Prefer the smallest maintainable deployment: one frontend, one API, one worker, one managed database/storage system. If the chosen free platform cannot run the API and worker reliably in one service, split the worker only when needed and document the trade-off.

## Reliability assumptions

Free-tier services may sleep, restart, or have limited CPU/RAM. The design must not assume an in-memory queue is durable or that a process stays alive continuously. Persist job state and recover stale leases. A public demo may be temporarily unavailable under free-tier limits; document that honestly.

## Architecture rules

- No microservices unless a concrete constraint justifies them.
- No paid fallback.
- No secrets in frontend bundles or repository.
- No cross-user vector search followed by filtering only in application memory; authorization scope must be applied in the retrieval query.
- Avoid unnecessary abstraction, but isolate provider-specific adapters.
- Record significant changes in `13-decisions.md`.
