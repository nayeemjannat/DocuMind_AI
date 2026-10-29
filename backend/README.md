# DocuMind AI — Backend (API & Worker)

This directory contains the Python FastAPI application and background ingestion worker for DocuMind AI.

## Architecture

- **`app/api/`**: REST API endpoints (v1 routes: auth verification, workspaces, documents, conversations, chat/RAG).
- **`app/core/`**: Configuration (`config.py`), security (`security.py`), and constants.
- **`app/db/`**: Supabase / PostgreSQL database connection and session management.
- **`app/models/`**: SQLAlchemy or SQLModel database models matching `docs/03-data-model.md`.
- **`app/schemas/`**: Pydantic schemas for request/response validation.
- **`app/services/`**: Domain services (document ingestion, text extraction, chunking, embeddings, vector search, LLM RAG).
- **`app/worker/`**: Background worker loop claiming and executing durable ingestion jobs.
- **`tests/`**: Unit and integration test suite.

## Getting Started

See `docs/15-environment-config.md` for required environment variables.
Copy `.env.example` to `.env` and configure accordingly.
