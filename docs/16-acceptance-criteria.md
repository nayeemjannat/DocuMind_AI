# 16 — Final Acceptance Criteria

The MVP is acceptable only when the required user journey works and the major privacy and grounding checks pass.

## Product journey
- [ ] User can sign up/sign in.
- [ ] User can create and view a workspace.
- [ ] User can upload a valid PDF, DOCX, or TXT file within policy limits.
- [ ] User sees accurate queued/processing/ready/failed status.
- [ ] Ready document can be queried.
- [ ] Answerable question receives an evidence-grounded answer.
- [ ] Citations resolve to real retrieved chunks and correct documents.
- [ ] Unanswerable question receives an insufficient-evidence response.
- [ ] Conversation history persists.
- [ ] Document deletion removes it from retrieval and follows the documented storage/database policy.

## Security and privacy
- [ ] All required cross-user access tests pass.
- [ ] All private endpoints verify identity and ownership.
- [ ] Private storage is not publicly readable.
- [ ] Vector search is scoped to authorized content before retrieval reaches the LLM.
- [ ] Secrets are absent from source control and client bundles.
- [ ] Prompt injection tests do not override system instructions.
- [ ] Limits are enforced server-side.
- [ ] Public errors do not expose stack traces or sensitive internals.

## Reliability and operations
- [ ] Jobs survive API/worker restarts and recover stale leases.
- [ ] Retries are bounded and idempotent.
- [ ] Health endpoints behave as documented.
- [ ] Free-tier resource limits have been tested and caveats documented.
- [ ] LLM/provider failure is handled without paid fallback.
- [ ] Logs avoid document contents and credentials.

## Quality and evidence
- [ ] Unit/integration/E2E checks relevant to the MVP were run.
- [ ] A 30-case RAG evaluation set exists.
- [ ] Grounded-answer success and citation precision are measured and reported honestly.
- [ ] No critical unresolved security issue remains.
- [ ] README/setup guide allows another developer to run the app.
- [ ] Progress and decision logs are current.
- [ ] A short demo walkthrough is documented.

## Final handoff must include

- What works.
- How to run locally.
- How to deploy within current free-tier constraints.
- Which tests were run and their results.
- Measured RAG evaluation results.
- Known limitations and failure modes.
- Any provider/free-tier assumptions that may change.
