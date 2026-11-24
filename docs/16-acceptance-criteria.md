# 16 — Final Acceptance Criteria

The MVP is acceptable only when the required user journey works and the major privacy and grounding checks pass.

## Product journey
- [x] User can sign up/sign in.
- [x] User can create and view a workspace.
- [x] User can upload a valid PDF, DOCX, or TXT file within policy limits.
- [x] User sees accurate queued/processing/ready/failed status.
- [x] Ready document can be queried.
- [x] Answerable question receives an evidence-grounded answer.
- [x] Citations resolve to real retrieved chunks and correct documents.
- [x] Unanswerable question receives an insufficient-evidence response.
- [x] Conversation history persists.
- [x] Document deletion removes it from retrieval and follows the documented storage/database policy.

## Security and privacy
- [x] All required cross-user access tests pass.
- [x] All private endpoints verify identity and ownership.
- [x] Private storage is not publicly readable.
- [x] Vector search is scoped to authorized content before retrieval reaches the LLM.
- [x] Secrets are absent from source control and client bundles.
- [x] Prompt injection tests do not override system instructions.
- [x] Limits are enforced server-side.
- [x] Public errors do not expose stack traces or sensitive internals.

## Reliability and operations
- [x] Jobs survive API/worker restarts and recover stale leases.
- [x] Retries are bounded and idempotent.
- [x] Health endpoints behave as documented.
- [x] Free-tier resource limits have been tested and caveats documented.
- [x] LLM/provider failure is handled without paid fallback.
- [x] Logs avoid document contents and credentials.

## Quality and evidence
- [x] Unit/integration/E2E checks relevant to the MVP were run.
- [x] A 30-case RAG evaluation set exists.
- [x] Grounded-answer success and citation precision are measured and reported honestly.
- [x] No critical unresolved security issue remains.
- [x] README/setup guide allows another developer to run the app.
- [x] Progress and decision logs are current.
- [x] A short demo walkthrough is documented.

## Final handoff must include

- What works.
- How to run locally.
- How to deploy within current free-tier constraints.
- Which tests were run and their results.
- Measured RAG evaluation results.
- Known limitations and failure modes.
- Any provider/free-tier assumptions that may change.
