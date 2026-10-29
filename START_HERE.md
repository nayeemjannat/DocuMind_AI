# Start Here — DocuMind AI

## What this pack is

This is the project handoff bundle for DocuMind AI. It is designed so a new developer or AI coding assistant can understand the project without relying on previous chat history.

## Read in this order

1. `docs/00-project-overview.md` — what we are building and why.
2. `docs/01-product-requirements.md` — MVP scope and user stories.
3. `docs/02-architecture.md` — system boundaries and technical choices.
4. `docs/03-data-model.md` — proposed entities and relationships.
5. `docs/04-api-contract.md` — expected API behavior.
6. `docs/05-auth-security.md` — authorization and safety requirements.
7. `docs/06-document-ingestion.md` and `docs/07-rag-and-citations.md` — document processing and question answering.
8. `docs/11-build-guide.md` — phase-by-phase implementation sequence.
9. `docs/12-build-progress.md` — current status; update it before and after work.
10. `docs/14-ai-agent-work-protocol.md` — instructions for the coding agent.

## Current baseline

- Product: DocuMind AI, a document question-answering web app with grounded answers and citations.
- Target: a small, credible portfolio demo for approximately 2–4 users, not an enterprise service.
- Budget: BDT 0 for the initial MVP; choose free tiers only where their current limits fit.
- Planned stack: Next.js + TypeScript frontend, Python FastAPI API/worker, Supabase Postgres + pgvector + private object storage, managed authentication, local embeddings if resource limits allow, and a currently available free-tier LLM provider.
- MVP document types: PDF, DOCX, TXT.
- No source code is included in this bundle.

## First implementation task

Start with Phase P00 in `docs/11-build-guide.md`: freeze the MVP scope and confirm the stack. Do not begin by generating the entire app in one prompt.

## Copy/paste prompt for a new AI coding session

> You are the senior engineer helping implement DocuMind AI. First read `START_HERE.md` and all relevant documents in `docs/`. Do not assume previous chat history exists. The documentation is the project contract. Before editing anything, inspect the current repository and `docs/12-build-progress.md`. Work only on the single next incomplete task. Explain the plan briefly, make the smallest coherent change, run the relevant checks, and report exact files changed, commands/tests actually run, results, unresolved risks, and the next task. Never claim a test passed unless you ran it. Do not add paid services, new infrastructure, or scope without documenting a decision. Preserve security requirements, especially ownership checks and private document storage. Update `docs/12-build-progress.md` and `docs/13-decisions.md` when appropriate. If requirements conflict or a necessary fact is missing, stop and ask one focused question instead of guessing.
