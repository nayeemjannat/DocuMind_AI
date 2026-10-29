export type DocumentStatus =
  | 'uploaded'
  | 'queued'
  | 'processing'
  | 'ready'
  | 'failed'
  | 'deleting'
  | 'deleted';

export interface Workspace {
  id: string;
  name: string;
  owner_id: string;
  created_at: string;
  updated_at: string;
}

export interface Document {
  id: string;
  workspace_id: string;
  owner_id: string;
  original_filename: string;
  storage_path: string;
  mime_type: string;
  size_bytes: number;
  page_count?: number | null;
  status: DocumentStatus;
  error_message?: string | null;
  created_at: string;
  updated_at: string;
}

export interface Citation {
  chunk_id: string;
  document_id: string;
  document_name: string;
  page_number?: number | null;
  excerpt: string;
}

export interface Message {
  id: string;
  conversation_id: string;
  sender_role: 'user' | 'assistant';
  content: string;
  citations?: Citation[];
  created_at: string;
}
