import {
  AnswerResponse,
  Conversation,
  DocumentItem,
  DocumentUploadResponse,
  Message,
  Workspace,
} from '@/types';

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, '') || 'http://localhost:8000/api/v1';

export class ApiError extends Error {
  status: number;
  code?: string;

  constructor(message: string, status: number, code?: string) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.code = code;
  }
}

async function request<T>(
  path: string,
  token: string,
  options: RequestInit = {}
): Promise<T> {
  const headers = new Headers(options.headers || {});
  headers.set('Authorization', `Bearer ${token}`);

  if (!(options.body instanceof FormData) && !headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json');
  }

  const res = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers,
  });

  if (res.status === 204) {
    return undefined as T;
  }

  let payload: unknown = null;
  const contentType = res.headers.get('content-type') || '';
  if (contentType.includes('application/json')) {
    payload = await res.json().catch(() => null);
  }

  if (!res.ok) {
    const detail =
      payload && typeof payload === 'object' && 'detail' in payload
        ? (payload as { detail: unknown }).detail
        : null;

    let message = 'Something went wrong. Please try again.';
    let code: string | undefined;

    if (typeof detail === 'string') {
      message = detail;
    } else if (detail && typeof detail === 'object') {
      const obj = detail as { message?: string; code?: string };
      if (obj.message) message = obj.message;
      if (obj.code) code = obj.code;
    } else if (res.status === 401) {
      message = 'Your session has expired. Please sign in again.';
    } else if (res.status === 429) {
      message = 'Daily quota or rate limit reached. Please try again later.';
      code = 'RATE_LIMITED';
    }

    throw new ApiError(message, res.status, code);
  }

  return payload as T;
}

export const api = {
  listWorkspaces(token: string) {
    return request<Workspace[]>('/workspaces', token);
  },

  createWorkspace(token: string, name: string) {
    return request<Workspace>('/workspaces', token, {
      method: 'POST',
      body: JSON.stringify({ name }),
    });
  },

  deleteWorkspace(token: string, workspaceId: string) {
    return request<void>(`/workspaces/${workspaceId}`, token, {
      method: 'DELETE',
    });
  },

  listDocuments(token: string, workspaceId: string) {
    return request<DocumentItem[]>(`/workspaces/${workspaceId}/documents`, token);
  },

  uploadDocument(token: string, workspaceId: string, file: File) {
    const formData = new FormData();
    formData.append('file', file);
    return request<DocumentUploadResponse>(
      `/workspaces/${workspaceId}/documents`,
      token,
      {
        method: 'POST',
        body: formData,
      }
    );
  },

  deleteDocument(token: string, documentId: string) {
    return request<void>(`/documents/${documentId}`, token, {
      method: 'DELETE',
    });
  },

  listConversations(token: string, workspaceId: string) {
    return request<Conversation[]>(`/workspaces/${workspaceId}/conversations`, token);
  },

  createConversation(token: string, workspaceId: string, title?: string) {
    return request<Conversation>(`/workspaces/${workspaceId}/conversations`, token, {
      method: 'POST',
      body: JSON.stringify({ title }),
    });
  },

  deleteConversation(token: string, conversationId: string) {
    return request<void>(`/conversations/${conversationId}`, token, {
      method: 'DELETE',
    });
  },

  listMessages(token: string, conversationId: string) {
    return request<Message[]>(`/conversations/${conversationId}/messages`, token);
  },

  askInConversation(
    token: string,
    conversationId: string,
    question: string,
    documentId?: string
  ) {
    return request<AnswerResponse>(`/conversations/${conversationId}/messages`, token, {
      method: 'POST',
      body: JSON.stringify({
        question,
        document_id: documentId || null,
      }),
    });
  },
};
