import React, { useState } from 'react';
import { apiClient } from '@/api';
import { PlayCircle, CheckCircle2, RotateCcw } from 'lucide-react';

interface BillingSummary {
  created: number;
  skipped: number;
  failed: Array<{ id: number; reason: string }>;
  timestamp: string;
}

export const BillingRunPage: React.FC = () => {
  const [isRunning, setIsRunning] = useState(false);
  const [summary, setSummary] = useState<BillingSummary | null>(null);
  const [runCount, setRunCount] = useState(0);

  const handleRunBilling = async () => {
    setIsRunning(true);
    try {
      if (apiClient.getIsMockMode()) {
        await new Promise((r) => setTimeout(r, 600));
        // Idempotency: first run creates invoices, subsequent run creates 0
        if (runCount === 0) {
          setSummary({
            created: 2,
            skipped: 0,
            failed: [],
            timestamp: new Date().toLocaleTimeString(),
          });
        } else {
          setSummary({
            created: 0,
            skipped: 2,
            failed: [],
            timestamp: new Date().toLocaleTimeString(),
          });
        }
        setRunCount((c) => c + 1);
      } else {
        const res = await apiClient.post<BillingSummary>('/billing/run/');
        setSummary(res);
        setRunCount((c) => c + 1);
      }
    } finally {
      setIsRunning(false);
    }
  };

  const handleReset = () => {
    setRunCount(0);
    setSummary(null);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Run Billing Engine</h1>
          <p className="text-xs text-slate-500 mt-1">
            Trigger automated subscription period evaluation and idempotent invoice generation.
          </p>
        </div>
      </div>

      <div className="bg-white rounded-xl border border-slate-200 p-8 shadow-xs max-w-xl mx-auto text-center space-y-6">
        <div className="mx-auto w-16 h-16 rounded-full bg-indigo-50 text-indigo-600 flex items-center justify-center">
          <PlayCircle className="w-10 h-10" />
        </div>

        <div className="space-y-1">
          <h2 className="text-lg font-bold text-slate-900">Execute Billing Cycle</h2>
          <p className="text-xs text-slate-500">
            Scans all active subscriptions with due periods. Idempotent: safe to run multiple times without duplicate invoices.
          </p>
        </div>

        <div className="flex justify-center gap-3">
          <button
            onClick={handleRunBilling}
            disabled={isRunning}
            className="inline-flex items-center gap-2 px-5 py-2.5 bg-indigo-600 hover:bg-indigo-700 disabled:bg-indigo-300 text-white rounded-lg text-sm font-semibold shadow-md transition"
          >
            <PlayCircle className="w-4 h-4" />
            <span>{isRunning ? 'Processing Cycle...' : 'Run Billing Engine'}</span>
          </button>
          {summary && (
            <button
              onClick={handleReset}
              className="inline-flex items-center gap-1.5 px-3 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg text-xs font-medium"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              <span>Reset Test</span>
            </button>
          )}
        </div>

        {summary && (
          <div className="mt-6 p-5 bg-slate-50 border border-slate-200 rounded-xl text-left space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-700 flex items-center gap-1.5">
                <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                Execution Summary
              </span>
              <span className="text-[11px] font-mono text-slate-400">{summary.timestamp}</span>
            </div>

            <div className="grid grid-cols-3 gap-3 pt-2 text-center">
              <div className="p-3 bg-white rounded-lg border border-slate-200 shadow-2xs">
                <span className="block text-xl font-bold text-emerald-600 font-mono">{summary.created}</span>
                <span className="text-[11px] text-slate-500 font-medium">Invoices Created</span>
              </div>
              <div className="p-3 bg-white rounded-lg border border-slate-200 shadow-2xs">
                <span className="block text-xl font-bold text-slate-600 font-mono">{summary.skipped}</span>
                <span className="text-[11px] text-slate-500 font-medium">Skipped (Current)</span>
              </div>
              <div className="p-3 bg-white rounded-lg border border-slate-200 shadow-2xs">
                <span className="block text-xl font-bold text-rose-600 font-mono">{summary.failed.length}</span>
                <span className="text-[11px] text-slate-500 font-medium">Failed</span>
              </div>
            </div>

            {runCount >= 2 && summary.created === 0 && (
              <p className="text-xs text-emerald-700 font-medium bg-emerald-50 p-2.5 rounded-lg border border-emerald-200 text-center">
                ✓ Idempotency verified: 0 new invoices created on repeat run.
              </p>
            )}
          </div>
        )}
      </div>
    </div>
  );
};
