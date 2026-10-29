# 17 — Risk Register

| Risk | Impact | Mitigation / response | Status |
|---|---|---|---|
| Local embedding model exceeds host RAM/CPU | Deployment or ingestion fails | Measure early; test a lighter compatible model; re-index consistently if model changes | Open |
| Free host sleeps or restarts | Slow requests or interrupted jobs | Persist jobs in DB; lease/recovery logic; explain cold-start caveat | Open |
| Free LLM quota changes | Questions stop working | Provider adapter, clear quota errors, no paid fallback; re-check terms before launch | Open |
| Cross-user data leak | Critical privacy failure | Ownership checks on every nested resource and vector query; adversarial tests | Open |
| Hallucinated citations | Trust failure | Validate every citation against retrieved chunk IDs; evaluate citation precision | Open |
| Prompt injection in uploaded documents | Unsafe or ungrounded output | Treat passages as untrusted data; system rules and adversarial evaluation | Open |
| Duplicate chunks after retry | Retrieval quality/cost degradation | Idempotent writes, chunk identity constraints, retry tests | Open |
| Deletion leaves orphaned vectors | Deleted content remains retrievable | Retryable deletion, consistency checks, deletion tests | Open |
| Parser returns empty/incorrect text | Poor answers | Extraction-quality checks, clear failure states, representative fixtures | Open |
| Provider sends sensitive content outside app | Privacy concern | Send minimum excerpts; review provider data-handling terms; use synthetic demo docs | Open |
| Scope expands too early | Delayed completion | One phase/task at a time; log changes; keep non-goals explicit | Open |
| AI coding tool overwrites working code | Regression/context loss | Inspect first, small diffs, tests, commits, progress handoff | Open |

Review this table after major milestones and whenever a new technical choice changes the risk profile.
