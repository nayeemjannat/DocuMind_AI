'use client';

import React, { useState } from 'react';
import { BookOpen, KeyRound, Mail, ShieldCheck } from 'lucide-react';
import { getSupabaseClient, isSupabaseConfigured } from '@/lib/supabase';

interface AuthViewProps {
  onAuthenticated: (token: string, email: string) => void;
}

export function AuthView({ onAuthenticated }: AuthViewProps) {
  const [mode, setMode] = useState<'signin' | 'signup'>('signin');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [manualToken, setManualToken] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setNotice(null);

    const supabase = getSupabaseClient();
    if (!supabase) {
      if (!manualToken.trim()) {
        setError('Please enter a valid bearer token to continue.');
        return;
      }
      onAuthenticated(manualToken.trim(), email.trim() || 'local-user');
      return;
    }

    setLoading(true);
    try {
      if (mode === 'signup') {
        const { data, error: signUpError } = await supabase.auth.signUp({
          email: email.trim(),
          password,
        });
        if (signUpError) throw signUpError;
        if (data.session?.access_token) {
          onAuthenticated(data.session.access_token, data.user?.email || email);
        } else {
          setNotice('Account created. Check your email to confirm your address before signing in.');
          setMode('signin');
        }
      } else {
        const { data, error: signInError } = await supabase.auth.signInWithPassword({
          email: email.trim(),
          password,
        });
        if (signInError) throw signInError;
        if (data.session?.access_token) {
          onAuthenticated(data.session.access_token, data.user?.email || email);
        }
      }
    } catch (err) {
      const msg = err instanceof Error ? err.message : 'Authentication failed.';
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-slate-50 px-4 py-12">
      <div className="w-full max-w-md bg-white rounded-2xl shadow-sm border border-slate-200 p-8">
        <div className="flex items-center gap-3 mb-6">
          <div className="h-10 w-10 rounded-xl bg-slate-900 text-white flex items-center justify-center">
            <BookOpen className="h-5 w-5" />
          </div>
          <div>
            <h1 className="text-xl font-semibold text-slate-900">DocuMind AI</h1>
            <p className="text-xs text-slate-500">Evidence-grounded document Q&amp;A</p>
          </div>
        </div>

        <p className="text-sm text-slate-600 mb-6">
          Upload PDF, DOCX, or TXT files into private workspaces and get answers backed by verifiable citations.
        </p>

        {isSupabaseConfigured ? (
          <div className="flex rounded-lg bg-slate-100 p-1 mb-6" role="tablist">
            <button
              type="button"
              role="tab"
              aria-selected={mode === 'signin'}
              onClick={() => {
                setMode('signin');
                setError(null);
              }}
              className={`flex-1 py-1.5 text-sm font-medium rounded-md transition ${
                mode === 'signin'
                  ? 'bg-white text-slate-900 shadow-sm'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              Sign In
            </button>
            <button
              type="button"
              role="tab"
              aria-selected={mode === 'signup'}
              onClick={() => {
                setMode('signup');
                setError(null);
              }}
              className={`flex-1 py-1.5 text-sm font-medium rounded-md transition ${
                mode === 'signup'
                  ? 'bg-white text-slate-900 shadow-sm'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              Sign Up
            </button>
          </div>
        ) : (
          <div className="mb-5 rounded-lg bg-amber-50 border border-amber-200 p-3 text-xs text-amber-800">
            Supabase environment variables are not set. Paste a valid JWT access token below for local API testing.
          </div>
        )}

        {error && (
          <div
            role="alert"
            className="mb-4 rounded-lg bg-red-50 border border-red-200 px-3 py-2 text-sm text-red-700"
          >
            {error}
          </div>
        )}

        {notice && (
          <div
            role="status"
            className="mb-4 rounded-lg bg-emerald-50 border border-emerald-200 px-3 py-2 text-sm text-emerald-700"
          >
            {notice}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          {isSupabaseConfigured ? (
            <>
              <div>
                <label htmlFor="email" className="block text-sm font-medium text-slate-700 mb-1">
                  Email address
                </label>
                <div className="relative">
                  <Mail className="h-4 w-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
                  <input
                    id="email"
                    type="email"
                    required
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="you@example.com"
                    className="w-full rounded-lg border border-slate-300 pl-9 pr-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-slate-900"
                  />
                </div>
              </div>

              <div>
                <label htmlFor="password" className="block text-sm font-medium text-slate-700 mb-1">
                  Password
                </label>
                <div className="relative">
                  <KeyRound className="h-4 w-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
                  <input
                    id="password"
                    type="password"
                    required
                    minLength={6}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="••••••••"
                    className="w-full rounded-lg border border-slate-300 pl-9 pr-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-slate-900"
                  />
                </div>
              </div>
            </>
          ) : (
            <div>
              <label htmlFor="token" className="block text-sm font-medium text-slate-700 mb-1">
                API Bearer Token
              </label>
              <textarea
                id="token"
                required
                rows={3}
                value={manualToken}
                onChange={(e) => setManualToken(e.target.value)}
                placeholder="eyJhbGciOi..."
                className="w-full rounded-lg border border-slate-300 p-2.5 text-xs font-mono focus:outline-none focus:ring-2 focus:ring-slate-900"
              />
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full rounded-lg bg-slate-900 py-2.5 text-sm font-medium text-white hover:bg-slate-800 disabled:opacity-50 transition"
          >
            {loading
              ? 'Please wait...'
              : isSupabaseConfigured
              ? mode === 'signin'
                ? 'Sign In'
                : 'Create Account'
              : 'Continue with Token'}
          </button>
        </form>

        <div className="mt-6 pt-5 border-t border-slate-100 flex items-center gap-2 text-xs text-slate-500">
          <ShieldCheck className="h-4 w-4 text-slate-400 shrink-0" />
          <span>Documents are stored privately and isolated per account.</span>
        </div>
      </div>
    </div>
  );
}
