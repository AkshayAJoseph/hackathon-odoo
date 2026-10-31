import React from 'react';
import { DollarSign, Repeat, AlertTriangle, Users } from 'lucide-react';

export const DashboardPage: React.FC = () => {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Executive Dashboard</h1>
          <p className="text-xs text-slate-500 mt-1">
            Real-time financial telemetry, MRR/ARR velocity, and accounts receivable.
          </p>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-xs flex items-center justify-between">
          <div>
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Active MRR</span>
            <div className="text-2xl font-extrabold text-slate-900 font-mono mt-1">$12,450.00</div>
            <span className="text-[11px] text-emerald-600 font-medium">↑ +8.4% from last period</span>
          </div>
          <div className="w-10 h-10 rounded-lg bg-emerald-50 text-emerald-600 flex items-center justify-center">
            <Repeat className="w-5 h-5" />
          </div>
        </div>

        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-xs flex items-center justify-between">
          <div>
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">ARR Velocity</span>
            <div className="text-2xl font-extrabold text-slate-900 font-mono mt-1">$149,400.00</div>
            <span className="text-[11px] text-indigo-600 font-medium">Annualized contract value</span>
          </div>
          <div className="w-10 h-10 rounded-lg bg-indigo-50 text-indigo-600 flex items-center justify-center">
            <DollarSign className="w-5 h-5" />
          </div>
        </div>

        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-xs flex items-center justify-between">
          <div>
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Overdue Invoices</span>
            <div className="text-2xl font-extrabold text-rose-600 font-mono mt-1">$331.00</div>
            <span className="text-[11px] text-rose-500 font-medium">1 invoice requiring collection</span>
          </div>
          <div className="w-10 h-10 rounded-lg bg-rose-50 text-rose-600 flex items-center justify-center">
            <AlertTriangle className="w-5 h-5" />
          </div>
        </div>

        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-xs flex items-center justify-between">
          <div>
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Active Subscribers</span>
            <div className="text-2xl font-extrabold text-slate-900 font-mono mt-1">24</div>
            <span className="text-[11px] text-slate-500 font-medium">100% retention this month</span>
          </div>
          <div className="w-10 h-10 rounded-lg bg-blue-50 text-blue-600 flex items-center justify-center">
            <Users className="w-5 h-5" />
          </div>
        </div>
      </div>
    </div>
  );
};
