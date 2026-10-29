# 10 — Zero-Budget Deployment Plan

## Budget constraint

Initial build and public demo budget: BDT 0. The app must not silently switch to a paid service or paid fallback. Free-tier limits and terms change, so re-check official provider documentation immediately before deployment.

## Candidate service categories

- Frontend hosting: Vercel Hobby or another suitable free tier.
- API/worker hosting: a free Python-capable service such as Render Free, if its current limits fit.
- Database and private storage: Supabase Free or equivalent.
- LLM: a provider/model with a currently available free tier, chosen after checking current quota, terms, data handling, and availability.
- Embeddings: local model if it passes the host resource gate.

These are candidates, not guarantees of permanent free availability or always-on uptime.

## Deployment gates

### Gate A — local baseline
- Frontend and API run locally.
- Environment variables are documented.
- Tests pass locally.
- No secret is committed.

### Gate B — database and storage
- Migrations apply cleanly.
- Private bucket policies are tested.
- Ownership and deletion behavior are tested.

### Gate C — host resource test
- Measure API startup, worker startup, model loading time, memory, CPU, and one representative ingestion.
- Verify health checks and recovery after a restart.
- If the local embedding model exceeds limits, evaluate a lighter compatible option and re-index; record the decision.

### Gate D — public deployment
- Configure environment variables in hosting dashboards only.
- Run migrations using the documented safe procedure.
- Verify auth redirects and callback URLs.
- Verify private storage access.
- Test one upload, one answer with citations, one abstention, and one deletion.
- Check logs for secrets or document content.
- Confirm that quota and provider failures are handled gracefully.

## Free-tier reliability caveats

- Services may sleep or cold-start.
- CPU/RAM may be too limited for local embedding inference.
- Provider free quotas may be rate-limited or changed.
- A database-backed job queue must recover after process restarts.
- The public demo may have occasional downtime; do not promise production SLA.

## Environment variable policy

Create `.env.example` with names and descriptions only. Never include real values. Separate public frontend variables from server-only secrets. Anything prefixed as publicly exposed by the frontend framework must be safe for every visitor to read.

See `15-environment-config.md`.
