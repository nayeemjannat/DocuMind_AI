# DocuMind AI — Documentation Starter Pack

**Purpose:** A code-free, organized project knowledge base that a developer or AI coding agent can read before implementing DocuMind AI.

This package contains product requirements, architecture decisions, data-model guidance, API contracts, security rules, RAG/ingestion specifications, test plans, deployment notes, a phased build guide, and progress templates.

## Important

- This is **documentation only**. It intentionally contains no application source code.
- Treat `docs/00-project-overview.md`, `docs/01-product-requirements.md`, and `docs/02-architecture.md` as core project context.
- Treat `docs/12-build-progress.md` as the current source of truth for implementation status.
- Record new decisions in `docs/13-decisions.md`; do not silently change an accepted requirement.
- Verify free-tier limits and provider capabilities at deployment time. They can change.
- Never put real credentials, API keys, service-role keys, tokens, or private user documents in this repository.

## Recommended repository layout

When you create the actual code repository, place these documents under its `docs/` directory. Keep this pack's root `README.md` as a reference or merge its contents into the code repository's root README.

## First steps

1. Read `START_HERE.md`.
2. Read `docs/00-project-overview.md`, `docs/01-product-requirements.md`, and `docs/02-architecture.md`.
3. Follow `docs/11-build-guide.md` one phase at a time.
4. Update `docs/12-build-progress.md` after each work session.
5. Use `docs/14-ai-agent-work-protocol.md` whenever handing work to an AI coding tool.
