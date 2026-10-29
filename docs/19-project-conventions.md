# 19 — Project Conventions

## Directory Structure

```text
DocuMind_AI/
├── .gitignore
├── .env.example
├── README.md
├── START_HERE.md
├── docs/                   # Full architectural, requirements, and progress documentation
│   └── templates/
├── reference/              # Upstream blueprint and source references
├── backend/                # Python FastAPI API & Worker
│   ├── .env.example
│   ├── README.md
│   ├── requirements.txt
│   ├── app/
│   │   ├── api/v1/         # Versioned route handlers (health, workspaces, documents, chat)
│   │   ├── core/           # Configuration, security, constants
│   │   ├── db/             # Database connection and session
│   │   ├── models/         # Database models
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── services/       # Parser, chunker, embeddings, vector search, RAG
│   │   ├── worker/         # Background queue worker
│   │   └── main.py         # FastAPI application entrypoint
│   └── tests/              # Test suite (pytest)
└── frontend/               # Next.js App Router Frontend
    ├── .env.example
    ├── README.md
    ├── package.json
    ├── tsconfig.json
    └── src/
        ├── app/            # App Router pages and layouts
        ├── components/     # UI components
        ├── lib/            # Utilities and API clients
        └── types/          # TypeScript interfaces
```

## Naming Conventions

- **Python:** `snake_case` for modules, functions, variables, and database fields. `PascalCase` for classes, Pydantic schemas, and SQLAlchemy models. `UPPER_CASE` for global constants and environment variables.
- **TypeScript:** `camelCase` for variables, properties, and functions. `PascalCase` for React components, interfaces, and types. `kebab-case` for file and directory names where applicable.
- **API Endpoints:** Plural nouns in kebab-case or snake_case with `/api/v1/` prefix (e.g., `/api/v1/workspaces/{workspace_id}/documents`).
- **Database Tables:** Plural `snake_case` (e.g., `profiles`, `workspaces`, `documents`, `document_chunks`, `conversations`, `messages`, `ingestion_jobs`).

## Git & Commit Conventions

- Semantic commit messages: `feat:`, `fix:`, `docs:`, `test:`, `refactor:`, `chore:`.
- Update `docs/12-build-progress.md` before finalizing any phase commit.
- Never commit `.env` or secret keys.

## Security Conventions

- All resource endpoints must check ownership (`owner_id == authenticated_user_id`).
- No secrets in the frontend bundle or repo.
- Never use in-memory queue as the sole ingestion job state.
