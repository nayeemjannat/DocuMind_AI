'use client';

import React, { useRef, useState } from 'react';
import {
  AlertCircle,
  CheckCircle2,
  Clock,
  FileText,
  Loader2,
  RefreshCw,
  Trash2,
  Upload,
} from 'lucide-react';
import { DocumentItem } from '@/types';

interface DocumentPanelProps {
  documents: DocumentItem[];
  uploading: boolean;
  onUpload: (file: File) => Promise<void>;
  onDelete: (documentId: string) => Promise<void>;
  onRefresh: () => Promise<void>;
}

const STATUS_BADGE: Record<
  DocumentItem['status'],
  { label: string; className: string; icon: React.ReactNode }
> = {
  uploaded: {
    label: 'Uploaded',
    className: 'bg-slate-100 text-slate-700',
    icon: <Clock className="h-3 w-3" />,
  },
  queued: {
    label: 'Queued',
    className: 'bg-amber-50 text-amber-700 border border-amber-200',
    icon: <Clock className="h-3 w-3" />,
  },
  processing: {
    label: 'Processing',
    className: 'bg-blue-50 text-blue-700 border border-blue-200',
    icon: <Loader2 className="h-3 w-3 animate-spin" />,
  },
  ready: {
    label: 'Ready',
    className: 'bg-emerald-50 text-emerald-700 border border-emerald-200',
    icon: <CheckCircle2 className="h-3 w-3" />,
  },
  failed: {
    label: 'Failed',
    className: 'bg-red-50 text-red-700 border border-red-200',
    icon: <AlertCircle className="h-3 w-3" />,
  },
  deleting: {
    label: 'Deleting',
    className: 'bg-slate-100 text-slate-500',
    icon: <Loader2 className="h-3 w-3 animate-spin" />,
  },
  deleted: {
    label: 'Deleted',
    className: 'bg-slate-100 text-slate-400',
    icon: <Trash2 className="h-3 w-3" />,
  },
};

function formatBytes(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
}

export function DocumentPanel({
  documents,
  uploading,
  onUpload,
  onDelete,
  onRefresh,
}: DocumentPanelProps) {
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const [localError, setLocalError] = useState<string | null>(null);
  const [refreshing, setRefreshing] = useState(false);

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    setLocalError(null);
    const file = e.target.files?.[0];
    if (!file) return;

    const maxBytes = 5 * 1024 * 1024;
    const ext = file.name.split('.').pop()?.toLowerCase() || '';
    if (!['pdf', 'docx', 'txt'].includes(ext)) {
      setLocalError('Unsupported format. Please upload PDF, DOCX, or TXT files only.');
      e.target.value = '';
      return;
    }
    if (file.size > maxBytes) {
      setLocalError('File exceeds the 5 MB limit.');
      e.target.value = '';
      return;
    }

    try {
      await onUpload(file);
    } finally {
      e.target.value = '';
    }
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    try {
      await onRefresh();
    } finally {
      setRefreshing(false);
    }
  };

  return (
    <section className="bg-white border-b lg:border-b-0 lg:border-r border-slate-200 w-full lg:w-80 flex flex-col shrink-0">
      <div className="p-4 border-b border-slate-200 flex items-center justify-between">
        <div>
          <h2 className="text-sm font-semibold text-slate-900">Documents</h2>
          <p className="text-xs text-slate-500">PDF, DOCX, TXT · Max 5 MB · Max 5/workspace</p>
        </div>
        <button
          type="button"
          onClick={handleRefresh}
          aria-label="Refresh documents"
          className="p-1.5 rounded-lg text-slate-500 hover:text-slate-900 hover:bg-slate-100 transition"
        >
          <RefreshCw className={`h-4 w-4 ${refreshing ? 'animate-spin' : ''}`} />
        </button>
      </div>

      <div className="p-4 border-b border-slate-100">
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf,.docx,.txt"
          aria-label="Upload document"
          className="hidden"
          onChange={handleFileChange}
        />
        <button
          type="button"
          disabled={uploading}
          onClick={() => fileInputRef.current?.click()}
          className="w-full flex items-center justify-center gap-2 rounded-xl border-2 border-dashed border-slate-300 py-3 px-4 text-sm font-medium text-slate-700 hover:border-slate-500 hover:bg-slate-50 disabled:opacity-50 transition"
        >
          {uploading ? (
            <>
              <Loader2 className="h-4 w-4 animate-spin" />
              Uploading...
            </>
          ) : (
            <>
              <Upload className="h-4 w-4" />
              Upload Document
            </>
          )}
        </button>

        {localError && (
          <p role="alert" className="mt-2 text-xs text-red-600">
            {localError}
          </p>
        )}
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-2.5">
        {documents.length === 0 ? (
          <div className="text-center py-8 text-xs text-slate-400">
            No documents uploaded yet. Upload a file to start asking questions.
          </div>
        ) : (
          documents.map((doc) => {
            const badge = STATUS_BADGE[doc.status] || STATUS_BADGE.uploaded;
            return (
              <div
                key={doc.id}
                className="rounded-xl border border-slate-200 p-3 hover:border-slate-300 transition"
              >
                <div className="flex items-start justify-between gap-2">
                  <div className="flex items-start gap-2 min-w-0">
                    <FileText className="h-4 w-4 text-slate-400 mt-0.5 shrink-0" />
                    <div className="min-w-0">
                      <p
                        className="text-sm font-medium text-slate-900 truncate"
                        title={doc.original_filename}
                      >
                        {doc.original_filename}
                      </p>
                      <p className="text-xs text-slate-500 mt-0.5">
                        {formatBytes(doc.size_bytes)}
                        {doc.page_count ? ` · ${doc.page_count} pages` : ''}
                      </p>
                    </div>
                  </div>
                  <button
                    type="button"
                    aria-label={`Delete document ${doc.original_filename}`}
                    onClick={() => {
                      if (
                        window.confirm(
                          `Delete "${doc.original_filename}" and all its indexed passages?`
                        )
                      ) {
                        onDelete(doc.id);
                      }
                    }}
                    className="p-1 rounded text-slate-400 hover:text-red-600 hover:bg-red-50 transition"
                  >
                    <Trash2 className="h-3.5 w-3.5" />
                  </button>
                </div>

                <div className="mt-2.5 flex items-center justify-between">
                  <span
                    className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium ${badge.className}`}
                  >
                    {badge.icon}
                    {badge.label}
                  </span>
                </div>

                {doc.status === 'failed' && doc.error_message && (
                  <p className="mt-2 text-xs text-red-600 bg-red-50 rounded p-1.5">
                    {doc.error_message}
                  </p>
                )}
              </div>
            );
          })
        )}
      </div>
    </section>
  );
}
