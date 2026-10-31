import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '@/auth';
import { ArrowRight, Shield, Zap, Layers, CheckCircle } from 'lucide-react';

export const LandingPage: React.FC = () => {
  const { isAuthenticated, role } = useAuth();

  const getDashboardLink = () => {
    if (!isAuthenticated) return '/login';
    if (role === 'admin') return '/admin/products';
    if (role === 'staff') return '/staff/subscriptions';
    return '/portal/subscriptions';
  };

  return (
    <div className="min-h-screen bg-slate-900 text-white flex flex-col justify-between">
      {/* Header */}
      <header className="max-w-7xl mx-auto w-full px-6 py-6 flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <div className="w-10 h-10 rounded-xl bg-indigo-600 flex items-center justify-center font-bold text-white shadow-lg">
            BL
          </div>
          <span className="font-bold text-xl tracking-tight">Brightloop</span>
        </div>
        <div className="flex items-center gap-3">
          {isAuthenticated ? (
            <Link
              to={getDashboardLink()}
              className="px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-sm font-semibold transition"
            >
              Open Console &rarr;
            </Link>
          ) : (
            <>
              <Link
                to="/login"
                className="px-4 py-2 rounded-lg text-slate-300 hover:text-white text-sm font-medium transition"
              >
                Sign In
              </Link>
              <Link
                to="/signup"
                className="px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-sm font-semibold transition"
              >
                Register
              </Link>
            </>
          )}
        </div>
      </header>

      {/* Hero */}
      <main className="max-w-5xl mx-auto px-6 py-16 text-center space-y-8">
        <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-indigo-950/80 border border-indigo-700/50 text-indigo-300 text-xs font-semibold">
          <Zap className="w-3.5 h-3.5 text-indigo-400" />
          <span>Brightloop Subscription Management Platform</span>
        </div>

        <h1 className="text-4xl sm:text-6xl font-extrabold tracking-tight leading-tight text-white">
          Enterprise Subscription <br />
          <span className="text-indigo-400">Billing & Lifecycle Engine</span>
        </h1>

        <p className="max-w-2xl mx-auto text-base sm:text-lg text-slate-400">
          Streamline recurring billing, quotation templates, automated tax calculations, and idempotent payment processing with role-scoped security.
        </p>

        <div className="flex flex-wrap justify-center gap-4 pt-4">
          <Link
            to={getDashboardLink()}
            className="flex items-center gap-2 px-6 py-3 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-semibold shadow-lg shadow-indigo-600/30 transition"
          >
            <span>{isAuthenticated ? 'Go to Console' : 'Launch Demo Console'}</span>
            <ArrowRight className="w-4 h-4" />
          </Link>
          <Link
            to="/dev/components"
            className="flex items-center gap-2 px-6 py-3 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 font-semibold border border-slate-700 transition"
          >
            <Layers className="w-4 h-4 text-slate-400" />
            <span>Component Showcase</span>
          </Link>
        </div>

        {/* Feature Badges */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-6 pt-12 text-left">
          <div className="p-5 rounded-xl bg-slate-800/50 border border-slate-800">
            <Shield className="w-6 h-6 text-indigo-400 mb-2" />
            <h3 className="font-semibold text-white text-sm">Role-Scoped Guards</h3>
            <p className="text-xs text-slate-400 mt-1">
              Admin, Staff, and Customer portal role separation strictly enforced across UI and API.
            </p>
          </div>
          <div className="p-5 rounded-xl bg-slate-800/50 border border-slate-800">
            <Layers className="w-6 h-6 text-emerald-400 mb-2" />
            <h3 className="font-semibold text-white text-sm">Strict Decimal Precision</h3>
            <p className="text-xs text-slate-400 mt-1">
              All financial totals and tax values carried as strings from API without browser rounding errors.
            </p>
          </div>
          <div className="p-5 rounded-xl bg-slate-800/50 border border-slate-800">
            <CheckCircle className="w-6 h-6 text-blue-400 mb-2" />
            <h3 className="font-semibold text-white text-sm">Lifecycle State Machine</h3>
            <p className="text-xs text-slate-400 mt-1">
              Visual status stepper and badges for Draft, Quotation, Confirmed, Active, and Closed.
            </p>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="max-w-7xl mx-auto w-full px-6 py-6 border-t border-slate-800/80 text-center text-xs text-slate-500">
        Brightloop Hackathon Project &copy; 2026. Built with Vite, React, Tailwind CSS.
      </footer>
    </div>
  );
};
