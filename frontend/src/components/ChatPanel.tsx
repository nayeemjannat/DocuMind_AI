'use client';

import React, { useState } from 'react';
import {
  AlertTriangle,
  BookOpen,
  ChevronDown,
  ChevronUp,
  FileText,
  Loader2,
  Send,
} from 'lucide-react';
import { Citation, DocumentItem, Message } from '@/types';

interface ChatPanelProps {
  messages: Message[];
  documents: DocumentItem[];
  asking: boolean;
  onAsk: (question: string) => Promise<void>;
}

function CitationCard({ citation, index }: { citation: Citation; index: number }) {
  const [expanded, setExpanded] = useState(false);

  return (
    <div className="rounded-lg border border-slate-200 bg-slate-50 text-xs">
      <button
        type="button"
        onClick={() => setExpanded((prev) => !prev)}
        className="w-full flex items-center justify-between gap-2 px-3 py-2 text-left hover:bg-slate-100 rounded-lg transition"
      >
        <div className="flex items-center gap-2 min-w-0">
          <span className="inline-flex items-center justify-center h-5 w-5 rounded bg-slate-900 text-white text-[11px] font-medium shrink-0">
            {index + 1}
          </span>
          <FileText className="h-3.5 w-3.5 text-slate-500 shrink-0" />
          <span className="font-medium text-slate-800 truncate">{citation.document_name}</span>
          {citation.page_number != null && (
            <span className="text-slate-500 shrink-0">Page {citation.page_number}</span>
          )}
        </div>
        {expanded ? (
          <ChevronUp className="h-3.5 w-3.5 text-slate-500 shrink-0" />
        ) : (
          <ChevronDown className="h-3.5 w-3.5 text-slate-500 shrink-0" />
        )}
      </button>

      {expanded && (
        <div className="px-3 pb-3 pt-1 border-t border-slate-200 text-slate-600 leading-relaxed whitespace-pre-wrap">
          {citation.excerpt}
        </div>
      )}
    </div>
  );
}

export function ChatPanel({ messages, documents, asking, onAsk }: ChatPanelProps) {
  const [question, setQuestion] = useState('');
  const readyCount = documents.filter((d) => d.status === 'ready').length;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const trimmed = question.trim();
    if (trimmed.length < 2 || asking) return;
    setQuestion('');
    await onAsk(trimmed);
  };

  return (
    <section className="flex-1 flex flex-col bg-slate-50 min-w-0">
      <div className="px-6 py-3.5 bg-white border-b border-slate-200 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <BookOpen className="h-4 w-4 text-slate-600" />
          <h2 className="text-sm font-semibold text-slate-900">Document Q&amp;A</h2>
        </div>
        <span className="text-xs text-slate-500">
          {readyCount} {readyCount === 1 ? 'document' : 'documents'} ready
        </span>
      </div>

      <div className="flex-1 overflow-y-auto p-6 space-y-6">
        {messages.length === 0 ? (
          <div className="max-w-lg mx-auto text-center py-16">
            <div className="h-12 w-12 rounded-2xl bg-white border border-slate-200 flex items-center justify-center mx-auto mb-4">
              <BookOpen className="h-6 w-6 text-slate-500" />
            </div>
            <h3 className="text-base font-medium text-slate-900 mb-1">
              Ask a question about your documents
            </h3>
            <p className="text-sm text-slate-500">
              Answers are generated strictly from your uploaded files with clickable source citations.
              If the evidence isn&apos;t present, DocuMind will tell you clearly.
            </p>
          </div>
        ) : (
          messages.map((msg) => {
            const isUser = msg.role === 'user';
            const isInsufficient =
              !isUser && (!msg.citations || msg.citations.length === 0);

            return (
              <div
                key={msg.id}
                className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-2xl rounded-2xl px-4 py-3 ${
                    isUser
                      ? 'bg-slate-900 text-white'
                      : 'bg-white border border-slate-200 text-slate-800 shadow-sm'
                  }`}
                >
                  {isInsufficient && (
                    <div className="flex items-center gap-1.5 text-xs font-medium text-amber-700 mb-2">
                      <AlertTriangle className="h-3.5 w-3.5" />
                      Insufficient evidence in uploaded documents
                    </div>
                  )}

                  <p className="text-sm leading-relaxed whitespace-pre-wrap">{msg.content}</p>

                  {!isUser && msg.citations && msg.citations.length > 0 && (
                    <div className="mt-4 pt-3 border-t border-slate-100 space-y-2">
                      <p className="text-xs font-medium text-slate-500">
                        Sources ({msg.citations.length})
                      </p>
                      <div className="space-y-1.5">
                        {msg.citations.map((cit, idx) => (
                          <CitationCard key={`${cit.chunk_id}-${idx}`} citation={cit} index={idx} />
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            );
          })
        )}

        {asking && (
          <div className="flex justify-start">
            <div className="bg-white border border-slate-200 rounded-2xl px-4 py-3 flex items-center gap-2 text-sm text-slate-500 shadow-sm">
              <Loader2 className="h-4 w-4 animate-spin" />
              Searching documents and verifying citations...
            </div>
          </div>
        )}
      </div>

      <form onSubmit={handleSubmit} className="p-4 bg-white border-t border-slate-200">
        <div className="max-w-3xl mx-auto flex gap-2">
          <input
            type="text"
            aria-label="Ask a question"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            disabled={asking}
            placeholder={
              readyCount > 0
                ? 'Ask a question about your documents...'
                : 'Upload and wait for a document to be ready, or ask a question...'
            }
            className="flex-1 rounded-xl border border-slate-300 px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-slate-900 disabled:bg-slate-50"
          />
          <button
            type="submit"
            disabled={asking || question.trim().length < 2}
            aria-label="Send question"
            className="inline-flex items-center gap-2 rounded-xl bg-slate-900 px-4 py-2.5 text-sm font-medium text-white hover:bg-slate-800 disabled:opacity-40 transition"
          >
            <Send className="h-4 w-4" />
            Ask
          </button>
        </div>
      </form>
    </section>
  );
}
