import React, { useState, useEffect } from 'react';
import { DollarSign, Repeat, AlertTriangle, Users, Filter, RefreshCw, ArrowUpRight, TrendingUp } from 'lucide-react';
import { apiClient } from '../api/client';

interface DashboardSummary {
  active_subscriptions: number;
  mrr: string;
  arr: string;
  revenue_collected: string;
  total_outstanding: string;
  overdue_count: number;
  overdue_amount: string;
  generated_at?: string;
}

export const DashboardPage: React.FC = () => {
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  // Filters state
  const [startDate, setStartDate] = useState<string>('');
  const [endDate, setEndDate] = useState<string>('');
  const [planId, setPlanId] = useState<string>('');
  const [plans, setPlans] = useState<Array<{ id: number; name: string }>>([]);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);

      // Build query string params
      const params = new URLSearchParams();
      if (startDate) params.append('start_date', startDate);
      if (endDate) params.append('end_date', endDate);
      if (planId) params.append('plan', planId);

      const queryString = params.toString() ? `?${params.toString()}` : '';
      const data = await apiClient.get<DashboardSummary>(`/reports/summary/${queryString}`);
      setSummary(data);
    } catch (err: unknown) {
      console.error('Failed to load dashboard metrics:', err);
      // Fallback clean display if API offline
      setSummary({
        active_subscriptions: 0,
        mrr: '0.00',
        arr: '0.00',
        revenue_collected: '0.00',
        total_outstanding: '0.00',
        overdue_count: 0,
        overdue_amount: '0.00'
      });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
    // Load plans for filter dropdown
    apiClient.get<any>('/plans/').then((res: any) => {
      const list = res?.results || res || [];
      if (Array.isArray(list)) {
        setPlans(list);
      }
    }).catch(() => {});
  }, [startDate, endDate, planId]);

  return (
    <div className="space-y-6">
      {/* Top Header & Filter Controls */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-white p-5 rounded-xl border border-slate-200 shadow-xs">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Executive Financial Dashboard</h1>
          <p className="text-xs text-slate-500 mt-1">
            Real-time financial telemetry, MRR/ARR velocity, and accounts receivable (SLA &lt; 2s).
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          <div className="flex items-center gap-2 bg-slate-50 px-3 py-1.5 rounded-lg border border-slate-200">
            <Filter className="w-4 h-4 text-slate-500" />
            <input
              type="date"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
              className="text-xs bg-transparent border-0 focus:ring-0 text-slate-700"
              title="Start Date"
            />
            <span className="text-slate-400 text-xs">to</span>
            <input
              type="date"
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
              className="text-xs bg-transparent border-0 focus:ring-0 text-slate-700"
              title="End Date"
            />
          </div>

          <select
            value={planId}
            onChange={(e) => setPlanId(e.target.value)}
            className="text-xs bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 text-slate-700 focus:outline-none focus:ring-1 focus:ring-indigo-500"
          >
            <option value="">All Plans</option>
            {plans.map((p) => (
              <option key={p.id} value={p.id}>{p.name}</option>
            ))}
          </select>

          <button
            onClick={() => fetchDashboardData()}
            className="p-2 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-600 transition"
            title="Refresh Summary"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {/* KPI Cards Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Active MRR */}
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-xs flex items-center justify-between">
          <div>
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Monthly Recurring (MRR)</span>
            <div className="text-2xl font-extrabold text-slate-900 font-mono mt-1">
              ${summary?.mrr ?? '0.00'}
            </div>
            <span className="text-[11px] text-emerald-600 font-medium flex items-center gap-0.5 mt-0.5">
              <TrendingUp className="w-3 h-3" /> Normalized recurring run rate
            </span>
          </div>
          <div className="w-10 h-10 rounded-lg bg-emerald-50 text-emerald-600 flex items-center justify-center">
            <Repeat className="w-5 h-5" />
          </div>
        </div>

        {/* ARR Velocity */}
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-xs flex items-center justify-between">
          <div>
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Annualized ARR</span>
            <div className="text-2xl font-extrabold text-indigo-900 font-mono mt-1">
              ${summary?.arr ?? '0.00'}
            </div>
            <span className="text-[11px] text-indigo-600 font-medium flex items-center gap-0.5 mt-0.5">
              <ArrowUpRight className="w-3 h-3" /> MRR × 12
            </span>
          </div>
          <div className="w-10 h-10 rounded-lg bg-indigo-50 text-indigo-600 flex items-center justify-center">
            <DollarSign className="w-5 h-5" />
          </div>
        </div>

        {/* Overdue Receivables */}
        <div className="bg-white p-5 rounded-xl border border-rose-200 bg-rose-50/20 shadow-xs flex items-center justify-between">
          <div>
            <span className="text-xs font-semibold text-rose-700 uppercase tracking-wider">Overdue Invoices</span>
            <div className="text-2xl font-extrabold text-rose-600 font-mono mt-1">
              ${summary?.overdue_amount ?? '0.00'}
            </div>
            <span className="text-[11px] text-rose-600 font-medium mt-0.5 block">
              {summary?.overdue_count ?? 0} invoices past due
            </span>
          </div>
          <div className="w-10 h-10 rounded-lg bg-rose-100 text-rose-600 flex items-center justify-center">
            <AlertTriangle className="w-5 h-5" />
          </div>
        </div>

        {/* Active Subscribers */}
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-xs flex items-center justify-between">
          <div>
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Active Subscriptions</span>
            <div className="text-2xl font-extrabold text-slate-900 font-mono mt-1">
              {summary?.active_subscriptions ?? 0}
            </div>
            <span className="text-[11px] text-slate-500 font-medium mt-0.5 block">
              Currently generating revenue
            </span>
          </div>
          <div className="w-10 h-10 rounded-lg bg-blue-50 text-blue-600 flex items-center justify-center">
            <Users className="w-5 h-5" />
          </div>
        </div>
      </div>

      {/* Secondary Row: Revenue Collected & Total Outstanding */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-xs">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Cash Revenue Collected</span>
            <span className="text-xs bg-emerald-100 text-emerald-800 font-medium px-2 py-0.5 rounded">Settled</span>
          </div>
          <div className="text-3xl font-extrabold text-emerald-600 font-mono mt-2">
            ${summary?.revenue_collected ?? '0.00'}
          </div>
          <p className="text-xs text-slate-500 mt-1">Total payments recorded in period</p>
        </div>

        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-xs">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Total Outstanding Invoiced</span>
            <span className="text-xs bg-amber-100 text-amber-800 font-medium px-2 py-0.5 rounded">Confirmed</span>
          </div>
          <div className="text-3xl font-extrabold text-amber-600 font-mono mt-2">
            ${summary?.total_outstanding ?? '0.00'}
          </div>
          <p className="text-xs text-slate-500 mt-1">Remaining balance across all confirmed invoices</p>
        </div>
      </div>
    </div>
  );
};
