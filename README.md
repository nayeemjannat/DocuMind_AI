# DocuMind AI

DocuMind AI is an intelligent, evidence-grounded document question-answering web application built with Retrieval-Augmented Generation (RAG). It enables users to upload private documents (PDF, DOCX, TXT), ask questions about their content, and receive verified answers supported by exact source citations.

---

## Key Features

- **Document Ingestion:** Supports PDF, DOCX, and plain text files with text extraction and metadata tracking.
- **RAG & Vector Search:** Chunks documents, generates embeddings using `sentence-transformers/all-MiniLM-L6-v2`, and performs cosine similarity retrieval using PostgreSQL `pgvector`.
- **Grounded Answers with Citations:** Retrieves relevant passages and generates answers with clear citations mapping back to source documents and page numbers.
- **Strict Tenant & Workspace Isolation:** Every workspace, document, chunk, and conversation is strictly isolated to its owner using server-side authorization and Row Level Security (RLS).
- **Durable Ingestion Pipeline:** Database-backed queue with leasing and retries for robust background processing.

---

## Tech Stack

- **Frontend:** Next.js (React, TypeScript, Tailwind CSS)
- **Backend:** Python, FastAPI, SQLAlchemy, Uvicorn
- **Database & Storage:** Supabase PostgreSQL with `pgvector` extension and private object storage
- **Embeddings:** `sentence-transformers/all-MiniLM-L6-v2` (384 dimensions)
- **LLM:** Google Gemini API (Free tier)
- **Authentication:** Supabase Managed Auth (JWT verification with RS256/HS256)
- **Testing:** Pytest, HTTPX

---

## Project Structure

```text
DocuMind_AI/
├── backend/                # FastAPI backend & ingestion worker
│   ├── app/
│   │   ├── api/v1/         # REST API routes (health, auth, workspaces)
│   │   ├── core/           # Security & runtime configuration
│   │   ├── db/             # Database connection & session
│   │   ├── models/         # SQLAlchemy models (workspace, document, chunk, chat)
│   │   ├── schemas/        # Pydantic schemas
│   │   └── services/       # Ingestion, embeddings, and RAG services
│   ├── tests/              # Automated unit and integration tests
│   └── requirements.txt    # Python dependencies
├── frontend/               # Next.js web application
│   └── src/                # UI components and App Router pages
├── supabase/               # Database migrations and RLS policies
└── docs/                   # Architecture, API contracts, and engineering specs
```

---

## Getting Started

### Prerequisites

- Python 3.12+
- Node.js 20+
- Supabase account (or local PostgreSQL instance with `pgvector`)

### Backend Setup

1. Navigate to the backend directory and activate the virtual environment:
   ```bash
   cd backend
   python -m venv .venv
   # Windows:
   .venv\Scripts\activate
   # macOS/Linux:
   source .venv/bin/activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create `.env` based on `.env.example`:
   ```bash
   cp .env.example .env
   ```

4. Run tests:
   ```bash
   pytest -v
   ```

5. Start the API server:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   npm install
   ```

2. Configure environment:
   ```bash
   cp .env.example .env.local
   ```

3. Start development server:
   ```bash
   npm run dev
   ```

---

## API Endpoints Overview

- `GET  /api/v1/health/live` — Liveness probe
- `GET  /api/v1/health/ready` — Readiness probe
- `GET  /api/v1/auth/me` — Authenticated user profile
- `POST /api/v1/workspaces` — Create workspace
- `GET  /api/v1/workspaces` — List user's workspaces
- `GET  /api/v1/workspaces/{id}` — Get workspace details
- `PATCH /api/v1/workspaces/{id}` — Update workspace
- `DELETE /api/v1/workspaces/{id}` — Delete workspace

---

## License

MIT License.
