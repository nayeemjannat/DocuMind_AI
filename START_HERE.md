# Getting Started with DocuMind AI

Welcome to the DocuMind AI engineering repository. This document outlines the project overview, system design documents, and recommended order of reading for developers joining the project.

## Documentation Index

The `docs/` directory contains complete technical specifications for the application:

1. `docs/00-project-overview.md` — Product vision and core problem statement.
2. `docs/01-product-requirements.md` — Functional and non-functional requirements.
3. `docs/02-architecture.md` — System architecture and component boundaries.
4. `docs/03-data-model.md` — Entity schemas and relationship definitions.
5. `docs/04-api-contract.md` — REST API route specifications and payload formats.
6. `docs/05-auth-security.md` — Authorization, tenant isolation, and security rules.
7. `docs/06-document-ingestion.md` — Ingestion lifecycle, parsing, and chunking specs.
8. `docs/07-rag-and-citations.md` — Retrieval-Augmented Generation and citation mechanics.
9. `docs/11-build-guide.md` — Step-by-step implementation milestones.
10. `docs/12-build-progress.md` — Implementation tracking and milestone status.

## Current Baseline

- **Product:** DocuMind AI — document question-answering with evidence-backed citations.
- **Scope:** Multi-format document parser (PDF, DOCX, TXT), vector similarity search, LLM answer synthesis.
- **Stack:** Next.js + TypeScript, Python FastAPI, PostgreSQL + pgvector, Supabase Storage, Google Gemini API.
- **Security:** Private-by-default storage, server-side JWT verification, strict owner checks on every resource.
