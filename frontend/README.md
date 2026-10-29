# DocuMind AI — Frontend

This is the Next.js (TypeScript + Tailwind CSS) client application for DocuMind AI.

## Project Structure

- **`src/app/`**: Next.js App Router pages and layout.
- **`src/components/`**: Reusable UI components (modals, file upload, chat window, citation cards, status badges).
- **`src/lib/`**: API client helpers, Supabase client configuration, utility functions.
- **`src/types/`**: TypeScript interfaces and types for API responses, workspaces, documents, and chat messages.

## Environment Variables

Copy `.env.example` to `.env.local` and set:
- `NEXT_PUBLIC_API_URL`: Backend API URL (default: `http://localhost:8000/api/v1`)
- `NEXT_PUBLIC_SUPABASE_URL`: Supabase project URL
- `NEXT_PUBLIC_SUPABASE_ANON_KEY`: Supabase anon/public key

Notice: Never place secret keys (such as `SUPABASE_SERVICE_ROLE_KEY`) in frontend environment files.
