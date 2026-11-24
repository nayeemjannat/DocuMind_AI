'use client';

import React, { useCallback, useEffect, useState } from 'react';
import { AuthView } from '@/components/AuthView';
import { ChatPanel } from '@/components/ChatPanel';
import { DocumentPanel } from '@/components/DocumentPanel';
import { WorkspaceSidebar } from '@/components/WorkspaceSidebar';
import { api, ApiError } from '@/lib/api';
import { getSupabaseClient } from '@/lib/supabase';
import { Conversation, DocumentItem, Message, Workspace } from '@/types';

export default function HomePage() {
  const [token, setToken] = useState<string | null>(null);
  const [userEmail, setUserEmail] = useState<string>('User');
  const [workspaces, setWorkspaces] = useState<Workspace[]>([]);
  const [activeWorkspaceId, setActiveWorkspaceId] = useState<string | null>(null);
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [activeConversationId, setActiveConversationId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);

  const [uploading, setUploading] = useState(false);
  const [asking, setAsking] = useState(false);
  const [errorBanner, setErrorBanner] = useState<string | null>(null);

  const handleError = useCallback((err: unknown) => {
    if (err instanceof ApiError && err.status === 401) {
      setToken(null);
    }
    const msg = err instanceof Error ? err.message : 'An unexpected error occurred.';
    setErrorBanner(msg);
  }, []);

  // Restore Supabase session on mount if configured
  useEffect(() => {
    const supabase = getSupabaseClient();
    if (!supabase) return;
    supabase.auth.getSession().then(({ data }) => {
      if (data.session?.access_token) {
        setToken(data.session.access_token);
        setUserEmail(data.session.user?.email || 'User');
      }
    });
  }, []);

  const loadWorkspaces = useCallback(async () => {
    if (!token) return;
    try {
      const list = await api.listWorkspaces(token);
      setWorkspaces(list);
      if (list.length > 0 && !activeWorkspaceId) {
        setActiveWorkspaceId(list[0].id);
      } else if (list.length === 0) {
        setActiveWorkspaceId(null);
      }
    } catch (err) {
      handleError(err);
    }
  }, [token, activeWorkspaceId, handleError]);

  useEffect(() => {
    loadWorkspaces();
  }, [loadWorkspaces]);

  const loadWorkspaceData = useCallback(async () => {
    if (!token || !activeWorkspaceId) {
      setDocuments([]);
      setConversations([]);
      setActiveConversationId(null);
      setMessages([]);
      return;
    }
    try {
      const [docs, convs] = await Promise.all([
        api.listDocuments(token, activeWorkspaceId),
        api.listConversations(token, activeWorkspaceId),
      ]);
      setDocuments(docs);
      setConversations(convs);
      if (convs.length > 0) {
        setActiveConversationId((prev) =>
          prev && convs.some((c) => c.id === prev) ? prev : convs[0].id
        );
      } else {
        setActiveConversationId(null);
        setMessages([]);
      }
    } catch (err) {
      handleError(err);
    }
  }, [token, activeWorkspaceId, handleError]);

  useEffect(() => {
    loadWorkspaceData();
  }, [loadWorkspaceData]);

  // Poll document status while any document is queued or processing
  useEffect(() => {
    if (!token || !activeWorkspaceId) return;
    const hasPending = documents.some(
      (d) => d.status === 'queued' || d.status === 'processing' || d.status === 'uploaded'
    );
    if (!hasPending) return;

    const timer = setInterval(async () => {
      try {
        const docs = await api.listDocuments(token, activeWorkspaceId);
        setDocuments(docs);
      } catch {
        // Ignore transient polling errors
      }
    }, 3000);

    return () => clearInterval(timer);
  }, [token, activeWorkspaceId, documents]);

  const loadMessages = useCallback(async () => {
    if (!token || !activeConversationId) {
      setMessages([]);
      return;
    }
    try {
      const list = await api.listMessages(token, activeConversationId);
      setMessages(list);
    } catch (err) {
      handleError(err);
    }
  }, [token, activeConversationId, handleError]);

  useEffect(() => {
    loadMessages();
  }, [loadMessages]);

  if (!token) {
    return (
      <AuthView
        onAuthenticated={(newToken, email) => {
          setToken(newToken);
          setUserEmail(email);
          setErrorBanner(null);
        }}
      />
    );
  }

  const handleSignOut = async () => {
    const supabase = getSupabaseClient();
    if (supabase) {
      await supabase.auth.signOut();
    }
    setToken(null);
    setWorkspaces([]);
    setActiveWorkspaceId(null);
    setDocuments([]);
    setConversations([]);
    setActiveConversationId(null);
    setMessages([]);
  };

  const handleCreateWorkspace = async (name: string) => {
    setErrorBanner(null);
    try {
      const ws = await api.createWorkspace(token, name);
      setWorkspaces((prev) => [ws, ...prev]);
      setActiveWorkspaceId(ws.id);
    } catch (err) {
      handleError(err);
    }
  };

  const handleDeleteWorkspace = async (id: string) => {
    setErrorBanner(null);
    try {
      await api.deleteWorkspace(token, id);
      setWorkspaces((prev) => prev.filter((w) => w.id !== id));
      if (activeWorkspaceId === id) {
        setActiveWorkspaceId(null);
      }
    } catch (err) {
      handleError(err);
    }
  };

  const handleUploadDocument = async (file: File) => {
    if (!activeWorkspaceId) return;
    setErrorBanner(null);
    setUploading(true);
    try {
      const res = await api.uploadDocument(token, activeWorkspaceId, file);
      setDocuments((prev) => [res.document, ...prev]);
    } catch (err) {
      handleError(err);
    } finally {
      setUploading(false);
    }
  };

  const handleDeleteDocument = async (documentId: string) => {
    setErrorBanner(null);
    try {
      await api.deleteDocument(token, documentId);
      setDocuments((prev) => prev.filter((d) => d.id !== documentId));
    } catch (err) {
      handleError(err);
    }
  };

  const handleCreateConversation = async () => {
    if (!activeWorkspaceId) return;
    setErrorBanner(null);
    try {
      const conv = await api.createConversation(token, activeWorkspaceId);
      setConversations((prev) => [conv, ...prev]);
      setActiveConversationId(conv.id);
      setMessages([]);
    } catch (err) {
      handleError(err);
    }
  };

  const handleDeleteConversation = async (conversationId: string) => {
    setErrorBanner(null);
    try {
      await api.deleteConversation(token, conversationId);
      setConversations((prev) => prev.filter((c) => c.id !== conversationId));
      if (activeConversationId === conversationId) {
        setActiveConversationId(null);
        setMessages([]);
      }
    } catch (err) {
      handleError(err);
    }
  };

  const handleAskQuestion = async (question: string) => {
    if (!activeWorkspaceId) return;
    setErrorBanner(null);
    setAsking(true);

    try {
      let convId = activeConversationId;
      if (!convId) {
        const created = await api.createConversation(token, activeWorkspaceId);
        setConversations((prev) => [created, ...prev]);
        setActiveConversationId(created.id);
        convId = created.id;
      }

      await api.askInConversation(token, convId, question);
      const [updatedMessages, updatedConvs] = await Promise.all([
        api.listMessages(token, convId),
        api.listConversations(token, activeWorkspaceId),
      ]);
      setMessages(updatedMessages);
      setConversations(updatedConvs);
    } catch (err) {
      handleError(err);
    } finally {
      setAsking(false);
    }
  };

  return (
    <div className="h-screen flex flex-col md:flex-row bg-slate-50 overflow-hidden">
      <WorkspaceSidebar
        userEmail={userEmail}
        workspaces={workspaces}
        activeWorkspaceId={activeWorkspaceId}
        conversations={conversations}
        activeConversationId={activeConversationId}
        onSelectWorkspace={(id) => {
          setActiveWorkspaceId(id);
          setErrorBanner(null);
        }}
        onCreateWorkspace={handleCreateWorkspace}
        onDeleteWorkspace={handleDeleteWorkspace}
        onSelectConversation={(id) => {
          setActiveConversationId(id);
          setErrorBanner(null);
        }}
        onCreateConversation={handleCreateConversation}
        onDeleteConversation={handleDeleteConversation}
        onSignOut={handleSignOut}
      />

      <main className="flex-1 flex flex-col min-w-0 min-h-0">
        {errorBanner && (
          <div
            role="alert"
            className="bg-red-50 border-b border-red-200 px-4 py-2.5 flex items-center justify-between text-sm text-red-700"
          >
            <span>{errorBanner}</span>
            <button
              type="button"
              onClick={() => setErrorBanner(null)}
              className="text-xs font-medium underline ml-4"
            >
              Dismiss
            </button>
          </div>
        )}

        {!activeWorkspaceId ? (
          <div className="flex-1 flex items-center justify-center p-8 text-center">
            <div className="max-w-sm">
              <h2 className="text-lg font-semibold text-slate-900 mb-2">
                Create or select a workspace
              </h2>
              <p className="text-sm text-slate-500">
                Use the sidebar to create a workspace, upload PDF/DOCX/TXT documents, and start asking grounded questions.
              </p>
            </div>
          </div>
        ) : (
          <div className="flex-1 flex flex-col lg:flex-row min-h-0">
            <DocumentPanel
              documents={documents}
              uploading={uploading}
              onUpload={handleUploadDocument}
              onDelete={handleDeleteDocument}
              onRefresh={loadWorkspaceData}
            />
            <ChatPanel
              messages={messages}
              documents={documents}
              asking={asking}
              onAsk={handleAskQuestion}
            />
          </div>
        )}
      </main>
    </div>
  );
}
