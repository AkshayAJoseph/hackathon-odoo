import React, { useState } from 'react';
import { StatusBadge, StatusStepper, SubscriptionStep } from '@/components';

export const ComponentShowcasePage: React.FC = () => {
  const [activeStep, setActiveStep] = useState<SubscriptionStep>('confirmed');

  const subscriptionStatuses = ['draft', 'quotation', 'confirmed', 'active', 'closed'];
  const invoiceStatuses = ['draft', 'confirmed', 'paid', 'cancelled'];

  return (
    <div className="space-y-8">
      {/* Page Header */}
      <div>
        <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Component Showcase</h1>
        <p className="text-sm text-slate-600 mt-1">
          Visual test harness verifying StatusBadge and StatusStepper component states for Brightloop.
        </p>
      </div>

      {/* StatusBadge Section */}
      <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-xs space-y-6">
        <div>
          <h2 className="text-base font-semibold text-slate-900">1. StatusBadge Component</h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Strict colour-coding according to specification (Draft: grey, Quotation: blue, Confirmed: amber, Active: green, Closed: slate, Paid: green, Cancelled: red, Overdue: red with days)
          </p>
        </div>

        <div className="space-y-4">
          <div>
            <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2">
              Subscription Statuses
            </h3>
            <div className="flex flex-wrap gap-3">
              {subscriptionStatuses.map((st) => (
                <div key={st} className="flex items-center gap-2 bg-slate-50 p-2 rounded-lg border border-slate-200">
                  <span className="text-xs text-slate-500 font-mono w-20">{st}:</span>
                  <StatusBadge status={st} kind="subscription" />
                </div>
              ))}
            </div>
          </div>

          <div>
            <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2">
              Invoice Statuses & Overdue Variant
            </h3>
            <div className="flex flex-wrap gap-3">
              {invoiceStatuses.map((st) => (
                <div key={st} className="flex items-center gap-2 bg-slate-50 p-2 rounded-lg border border-slate-200">
                  <span className="text-xs text-slate-500 font-mono w-20">{st}:</span>
                  <StatusBadge status={st} kind="invoice" />
                </div>
              ))}
              <div className="flex items-center gap-2 bg-slate-50 p-2 rounded-lg border border-slate-200">
                <span className="text-xs text-slate-500 font-mono w-20">overdue:</span>
                <StatusBadge status="confirmed" kind="invoice" overdue daysOverdue={12} />
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* StatusStepper Section */}
      <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-xs space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-base font-semibold text-slate-900">2. StatusStepper Component</h2>
            <p className="text-xs text-slate-500 mt-0.5">
              Draft &rarr; Quotation &rarr; Confirmed &rarr; Active &rarr; Closed status flow
            </p>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-xs font-medium text-slate-600">Simulate Step:</span>
            <select
              value={activeStep}
              onChange={(e) => setActiveStep(e.target.value as SubscriptionStep)}
              className="text-xs border border-slate-300 rounded px-2.5 py-1 bg-white focus:outline-hidden focus:ring-2 focus:ring-indigo-500"
            >
              {subscriptionStatuses.map((s) => (
                <option key={s} value={s}>
                  {s.toUpperCase()}
                </option>
              ))}
            </select>
          </div>
        </div>

        <div className="p-4 bg-slate-50 rounded-lg border border-slate-200">
          <StatusStepper status={activeStep} />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2">
          {subscriptionStatuses.map((st) => (
            <div key={st} className="p-3 bg-slate-50 rounded-md border border-slate-100">
              <span className="text-xs font-semibold text-slate-700 block mb-1">State: {st}</span>
              <StatusStepper status={st} />
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
