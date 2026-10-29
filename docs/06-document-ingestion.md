# 06 — Document Ingestion Pipeline

## Supported input

- PDF
- DOCX
- TXT

Initial limits: 5 MB per file, 30 pages per document where page count is available, 5 documents per account, 5 uploads/day/account, and one active job/account.

## Required state model

`uploaded -> queued -> processing -> ready | failed`

Deletion may use `deleting -> deleted`. Define exact state transitions in implementation and reject invalid transitions.

## Pipeline stages

1. **Validate request:** authenticate user, verify workspace ownership, enforce quotas, size/type checks.
2. **Store source:** write to private storage; use a generated object key rather than a trusted user path.
3. **Create records:** create document metadata and durable job state.
4. **Claim job:** worker atomically claims a queued/available job and records a lease.
5. **Fetch source:** use private server-side access.
6. **Parse:** extract text and page/section metadata where supported.
7. **Normalize:** standardize line endings and remove clearly irrelevant extraction artifacts without destroying meaning.
8. **Check quality:** fail safely if extracted text is empty or unusable; handle encrypted/corrupt files.
9. **Chunk:** split into bounded, overlapping passages with stable indices/IDs. Avoid splitting in the middle of sentences when feasible.
10. **Embed:** create vectors with the selected embedding model.
11. **Persist:** insert chunks and vectors idempotently.
12. **Finalize:** mark document/job ready only when all required stages succeed.
13. **Recover:** retry bounded transient failures; mark permanent failures safely.
14. **Observe:** record timing, counts, safe error categories, and job attempts without logging document bodies.

## Durability and idempotency

- The database, not process memory, is the source of truth for jobs.
- A process restart must not lose queued jobs.
- Jobs need claim/lease semantics so a crashed worker's job can be recovered.
- Retries must not create duplicate chunks.
- A repeated job should either produce the same result or cleanly replace a previous partial result.
- Use bounded retries and backoff; avoid infinite loops.
- If a document is deleted while a job is running, the worker must stop or safely discard its result.

## Resource limits

- Do not load every document or all embeddings into RAM.
- Process one job at a time initially.
- Measure model startup time, memory, CPU, and ingestion duration on the target free host.
- The initial candidate local embedding model is `sentence-transformers/all-MiniLM-L6-v2` (384 dimensions), but it is not approved until it passes the resource gate.
- If memory/CPU is too high, evaluate a lighter ONNX/FastEmbed-style option and document the chosen model and vector dimension. Re-index all documents if the embedding model changes.
- Do not mix vectors produced by incompatible embedding models in the same retrieval index.

## Deletion

Deletion must account for:
- Source object in private storage.
- Document metadata.
- All document chunks and vectors.
- Related ingestion jobs.
- Citation metadata/history references (decide whether to retain a tombstone or remove citation content).
- Any in-progress worker lease.

Deletion should be retryable and should not leave searchable orphan chunks.

## User-visible status

Show a clear status and safe error:
- Uploaded / queued.
- Processing.
- Ready to ask questions.
- Failed, with a helpful reason and retry option if retry is safe.

Never report “ready” before chunks and embeddings are committed and retrievable.
