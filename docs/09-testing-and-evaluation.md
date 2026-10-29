# 09 — Testing and Evaluation Plan

Do not claim a check passed unless it was actually executed. Record commands, environment, results, and known limitations.

## Test layers

### Unit tests
- Filename and file-type validation.
- File-size and page-limit policies.
- Parser behavior for PDF/DOCX/TXT fixtures.
- Text normalization and chunking boundaries.
- State transitions and retry rules.
- Citation validation against retrieved chunk IDs.
- Quota calculations.
- Error mapping and response validation.

### Integration tests
- Database relationships and constraints.
- Ownership checks across every private resource.
- Private storage upload/download/delete.
- Persistent job claim, lease expiry, retry, and recovery.
- Chunk persistence and vector retrieval filters.
- LLM adapter errors and timeout behavior.
- Message and citation persistence.

### End-to-end tests
- Sign up/sign in.
- Create workspace.
- Upload a supported document.
- See queued/processing/ready state.
- Ask an answerable question and inspect citations.
- Ask an unanswerable question and receive an insufficient-evidence response.
- View conversation history.
- Delete a document and verify its chunks are no longer searchable.

### Security tests
- Cross-user workspace/document/conversation access.
- Forged nested resource IDs.
- Disallowed MIME/extension and oversized uploads.
- Malformed, corrupt, empty, and encrypted documents.
- Prompt injection embedded in source documents.
- Quota and rate-limit bypass attempts.
- No secrets or private content in public responses/logs.

## RAG evaluation dataset

Create at least 30 cases using synthetic or public-domain documents:
- Direct factual lookup.
- Questions requiring multiple passages.
- Paraphrased questions.
- Questions whose answer is not present.
- Ambiguous questions.
- Conflicting source passages.
- Citation page/section validation.
- Prompt-injection attempts.
- Similar-sounding but wrong facts.
- Cross-workspace isolation checks.

For each case, store expected answer facts, expected supporting source/chunk, whether the correct behavior is to abstain, and the scoring result.

## Metrics

- Grounded-answer success rate.
- Citation precision: cited chunks actually support the associated claims.
- Abstention quality: unsupported questions are not answered as facts.
- Retrieval recall on answerable cases.
- Cross-user isolation test pass rate.
- Ingestion success/failure rate and duration.
- Retry recovery rate.
- API error rate and latency where observable.

## Initial acceptance goals

- 100% pass on required authorization-isolation tests.
- 100% citation references resolve to real retrieved chunks.
- At least 80% grounded-answer success on the defined evaluation set.
- At least 90% citation precision.
- All critical user journey E2E tests pass.
- No unresolved critical security defects.

These are target thresholds. Report measured outcomes honestly and document dataset size and limitations.
