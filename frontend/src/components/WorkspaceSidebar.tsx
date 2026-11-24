'use client';

import React, { useState } from 'react';
import {
  Folder,
  LogOut,
  MessageSquare,
  Plus,
  Trash2,
} from 'lucide-react';
import { Conversation, Workspace } from '@/types';

interface WorkspaceSidebarProps {
  userEmail: string;
  workspaces: Workspace[];
  activeWorkspaceId: string | null;
  conversations: Conversation[];
  activeConversationId: string | null;
  onSelectWorkspace: (id: string) => void;
  onCreateWorkspace: (name: string) => Promise<void>;
  onDeleteWorkspace: (id: string) => Promise<void>;
  onSelectConversation: (id: string) => void;
  onCreateConversation: () => Promise<void>;
  onDeleteConversation: (id: string) => Promise<void>;
  onSignOut: () => void;
}

export function WorkspaceSidebar({
  userEmail,
  workspaces,
  activeWorkspaceId,
  conversations,
  activeConversationId,
  onSelectWorkspace,
  onCreateWorkspace,
  onDeleteWorkspace,
  onSelectConversation,
  onCreateConversation,
  onDeleteConversation,
  onSignOut,
}: WorkspaceSidebarProps) {
  const [newWsName, setNewWsName] = useState('');
  const [creatingWs, setCreatingWs] = useState(false);

  const handleCreateWs = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newWsName.trim() || creatingWs) return;
    setCreatingWs(true);
    try {
      await onCreateWorkspace(newWsName.trim());
      setNewWsName('');
    } finally {
      setCreatingWs(false);
    }
  };

  return (
    <aside className="w-full md:w-72 bg-white border-r border-slate-200 flex flex-col h-full shrink-0">
      <div className="p-4 border-b border-slate-200 flex items-center justify-between">
        <div>
          <h1 className="font-semibold text-slate-900">DocuMind AI</h1>
          <p className="text-xs text-slate-500 truncate max-w-[160px]" title={userEmail}>
            {userEmail}
          </p>
        </div>
        <button
          type="button"
          onClick={onSignOut}
          title="Sign out"
          aria-label="Sign out"
          className="p-2 rounded-lg text-slate-500 hover:text-slate-900 hover:bg-slate-100 transition"
        >
          <LogOut className="h-4 w-4" />
        </button>
      </div>

      {/* Workspaces section */}
      <div className="p-4 border-b border-slate-200">
        <h2 className="text-xs font-semibold uppercase tracking-wider text-slate-500 mb-3">
          Workspaces
        </h2>
        <form onSubmit={handleCreateWs} className="flex gap-2 mb-3">
          <input
            type="text"
            aria-label="New workspace name"
            value={newWsName}
            onChange={(e) => setNewWsName(e.target.value)}
            placeholder="New workspace..."
            className="flex-1 min-w-0 rounded-lg border border-slate-300 px-2.5 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-slate-900"
          />
          <button
            type="submit"
            disabled={!newWsName.trim() || creatingWs}
            aria-label="Create workspace"
            className="px-2.5 py-1.5 rounded-lg bg-slate-900 text-white hover:bg-slate-800 disabled:opacity-40 transition"
          >
            <Plus className="h-4 w-4" />
          </button>
        </form>

        <div className="space-y-1 max-h-48 overflow-y-auto">
          {workspaces.length === 0 ? (
            <p className="text-xs text-slate-400 py-2">No workspaces yet.</p>
          ) : (
            workspaces.map((ws) => {
              const isActive = ws.id === activeWorkspaceId;
              return (
                <div
                  key={ws.id}
                  className={`group flex items-center justify-between rounded-lg px-2.5 py-2 text-sm cursor-pointer transition ${
                    isActive
                      ? 'bg-slate-900 text-white'
                      : 'text-slate-700 hover:bg-slate-100'
                  }`}
                  onClick={() => onSelectWorkspace(ws.id)}
                >
                  <div className="flex items-center gap-2 min-w-0">
                    <Folder className="h-4 w-4 shrink-0" />
                    <span className="truncate">{ws.name}</span>
                  </div>
                  <button
                    type="button"
                    aria-label={`Delete workspace ${ws.name}`}
                    onClick={(e) => {
                      e.stopPropagation();
                      if (
                        window.confirm(
                          `Delete workspace "${ws.name}" and all its documents and chats?`
                        )
                      ) {
                        onDeleteWorkspace(ws.id);
                      }
                    }}
                    className={`p-1 rounded opacity-0 group-hover:opacity-100 transition ${
                      isActive
                        ? 'hover:bg-slate-700 text-slate-300'
                        : 'hover:bg-slate-200 text-slate-500'
                    }`}
                  >
                    <Trash2 className="h-3.5 w-3.5" />
                  </button>
                </div>
              );
            })
          )}
        </div>
      </div>

      {/* Conversation history section */}
      <div className="p-4 flex-1 flex flex-col min-h-0">
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-xs font-semibold uppercase tracking-wider text-slate-500">
            Conversations
          </h2>
          {activeWorkspaceId && (
            <button
              type="button"
              onClick={onCreateConversation}
              aria-label="New conversation"
              className="inline-flex items-center gap-1 text-xs font-medium text-slate-700 hover:text-slate-900"
            >
              <Plus className="h-3.5 w-3.5" />
              New Chat
            </button>
          )}
        </div>

        <div className="space-y-1 overflow-y-auto flex-1">
          {!activeWorkspaceId ? (
            <p className="text-xs text-slate-400">Select a workspace first.</p>
          ) : conversations.length === 0 ? (
            <p className="text-xs text-slate-400">No conversations yet.</p>
          ) : (
            conversations.map((conv) => {
              const isActive = conv.id === activeConversationId;
              return (
                <div
                  key={conv.id}
                  className={`group flex items-center justify-between rounded-lg px-2.5 py-2 text-sm cursor-pointer transition ${
                    isActive
                      ? 'bg-slate-100 text-slate-900 font-medium'
                      : 'text-slate-600 hover:bg-slate-50'
                  }`}
                  onClick={() => onSelectConversation(conv.id)}
                >
                  <div className="flex items-center gap-2 min-w-0">
                    <MessageSquare className="h-3.5 w-3.5 shrink-0 text-slate-400" />
                    <span className="truncate">{conv.title || 'New Conversation'}</span>
                  </div>
                  <button
                    type="button"
                    aria-label={`Delete conversation ${conv.title || 'New Conversation'}`}
                    onClick={(e) => {
                      e.stopPropagation();
                      if (window.confirm('Delete this conversation and its messages?')) {
                        onDeleteConversation(conv.id);
                      }
                    }}
                    className="p-1 rounded opacity-0 group-hover:opacity-100 hover:bg-slate-200 text-slate-500 transition"
                  >
                    <Trash2 className="h-3.5 w-3.5" />
                  </button>
                </div>
              );
            })
          )}
        </div>
      </div>
    </aside>
  );
}
