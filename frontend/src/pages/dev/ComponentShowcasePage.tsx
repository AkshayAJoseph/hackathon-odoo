import React, { useState } from 'react';
import {
  StatusBadge,
  StatusStepper,
  SubscriptionStep,
  DataTable,
  Column,
  MoneyInput,
  PasswordHints,
  evaluatePassword,
} from '@/components';
import { MOCK_SUBSCRIPTIONS, Subscription } from '@/api';

import { FileSpreadsheet, Eye, RefreshCw, XCircle } from 'lucide-react';

export const ComponentShowcasePage: React.FC = () => {
  const [activeStep, setActiveStep] = useState<SubscriptionStep>('confirmed');

  // DataTable state
  const [tableLoading, setTableLoading] = useState(false);
  const [tableEmpty, setTableEmpty] = useState(false);
  const [selectedRow, setSelectedRow] = useState<Subscription | null>(null);

  // MoneyInput state
  const [inrValue, setInrValue] = useState('1499.00');
  const [inrNumeric, setInrNumeric] = useState<number | null>(1499);
  const [currencyChoice, setCurrencyChoice] = useState('₹');
  const [currencyPos, setCurrencyPos] = useState<'left' | 'right'>('left');
  const [simulateError, setSimulateError] = useState(false);
  const [simulateDisabled, setSimulateDisabled] = useState(false);
  const [allowNegatives, setAllowNegatives] = useState(false);

  // PasswordHints state
  const [demoPassword, setDemoPassword] = useState('Password123!');
  const [demoConfirmPassword, setDemoConfirmPassword] = useState('Password123!');

  const subscriptionStatuses = ['draft', 'quotation', 'confirmed', 'active', 'closed'];
  const invoiceStatuses = ['draft', 'confirmed', 'paid', 'cancelled'];

  const subscriptionColumns: Column<Subscription>[] = [
    {
      header: 'Reference',
      accessorKey: 'subscription_number',
      cell: (row) => (
        <div className="flex items-center gap-1.5 font-mono font-bold text-indigo-700">
          <FileSpreadsheet className="w-4 h-4 text-slate-400" />
          {row.subscription_number}
        </div>
      ),
    },
    {
      header: 'Customer',
      accessorKey: 'customer_name',
      cell: (row) => (
        <div>
          <span className="font-medium text-slate-900">{row.customer_name}</span>
          <span className="block text-[11px] text-slate-400 font-mono">{row.customer_email}</span>
        </div>
      ),
    },
    {
      header: 'Plan',
      accessorKey: 'plan_name',
      className: 'font-medium text-slate-800',
    },
    {
      header: 'Period',
      cell: (row) => (
        <span className="font-mono text-[11px] text-slate-500">
          {row.current_period_start} &rarr; {row.current_period_end}
        </span>
      ),
    },
    {
      header: 'Total Amount',
      align: 'right',
      cell: (row) => (
        <span className="font-mono font-bold text-slate-900">
          ₹{row.total_amount}
        </span>
      ),
    },
    {
      header: 'Status',
      align: 'center',
      cell: (row) => <StatusBadge status={row.status} kind="subscription" />,
    },
    {
      header: 'Action',
      align: 'right',
      cell: (row) => (
        <button
          type="button"
          onClick={(e) => {
            e.stopPropagation();
            setSelectedRow(row);
          }}
          className="inline-flex items-center gap-1 text-xs font-semibold text-indigo-600 hover:text-indigo-800 px-2 py-1 rounded bg-indigo-50 hover:bg-indigo-100 transition-colors"
        >
          <Eye className="w-3.5 h-3.5" />
          <span>Select</span>
        </button>
      ),
    },
  ];

  return (
    <div className="space-y-8">
      {/* Page Header */}
      <div>
        <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Component Showcase</h1>
        <p className="text-sm text-slate-600 mt-1">
          Visual test harness verifying StatusBadge, StatusStepper, DataTable, and MoneyInput for Brightloop.
        </p>
      </div>

      {/* 1. StatusBadge Section */}
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

      {/* 2. StatusStepper Section */}
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

      {/* 3. DataTable Section */}
      <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-xs space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
          <div>
            <h2 className="text-base font-semibold text-slate-900">3. DataTable Component</h2>
            <p className="text-xs text-slate-500 mt-0.5">
              Generic, typed table with custom cells, responsive horizontal scrolling, animated skeleton loading, and empty states.
            </p>
          </div>
          <div className="flex flex-wrap items-center gap-2">
            <button
              type="button"
              onClick={() => setTableLoading(!tableLoading)}
              className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium border transition-colors ${
                tableLoading
                  ? 'bg-indigo-50 border-indigo-300 text-indigo-700'
                  : 'bg-white border-slate-300 text-slate-700 hover:bg-slate-50'
              }`}
            >
              <RefreshCw className={`w-3.5 h-3.5 ${tableLoading ? 'animate-spin' : ''}`} />
              <span>{tableLoading ? 'Stop Loading' : 'Simulate Loading'}</span>
            </button>
            <button
              type="button"
              onClick={() => setTableEmpty(!tableEmpty)}
              className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium border transition-colors ${
                tableEmpty
                  ? 'bg-amber-50 border-amber-300 text-amber-700'
                  : 'bg-white border-slate-300 text-slate-700 hover:bg-slate-50'
              }`}
            >
              <XCircle className="w-3.5 h-3.5" />
              <span>{tableEmpty ? 'Restore Data' : 'Simulate Empty'}</span>
            </button>
          </div>
        </div>

        {selectedRow && (
          <div className="p-3 bg-indigo-50 border border-indigo-200 rounded-lg flex items-center justify-between text-xs">
            <div>
              <span className="font-semibold text-indigo-900">Row Clicked: </span>
              <span className="font-mono text-indigo-700 font-bold">{selectedRow.subscription_number}</span>
              <span className="text-indigo-800 ml-2">({selectedRow.customer_name} &bull; {selectedRow.plan_name})</span>
            </div>
            <button
              type="button"
              onClick={() => setSelectedRow(null)}
              className="text-indigo-600 hover:text-indigo-800 font-semibold"
            >
              Clear
            </button>
          </div>
        )}

        <DataTable<Subscription>
          data={tableEmpty ? [] : MOCK_SUBSCRIPTIONS}
          columns={subscriptionColumns}
          isLoading={tableLoading}
          loadingMessage="Fetching subscription records..."
          emptyMessage="No subscription records matching criteria"
          onRowClick={(row) => setSelectedRow(row)}
        />
      </div>

      {/* 4. MoneyInput Section */}
      <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-xs space-y-6">
        <div>
          <h2 className="text-base font-semibold text-slate-900">4. MoneyInput Component</h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Controlled monetary input with currency indicator (default INR/₹), placeholder, disabled, and error states.
          </p>
        </div>

        {/* Live Interactive Playground */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 p-4 bg-slate-50 rounded-xl border border-slate-200">
          <div className="space-y-4">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500">
              Interactive Component
            </h3>
            <MoneyInput
              label="Subscription Unit Price"
              value={inrValue}
              onChange={(str, num) => {
                setInrValue(str);
                setInrNumeric(num);
              }}
              currency={currencyChoice}
              currencyPosition={currencyPos}
              placeholder="0.00"
              disabled={simulateDisabled}
              error={simulateError ? 'Amount exceeds maximum allowable threshold (₹50,000)' : undefined}
              helperText="Base price excluding calculated taxes and discounts"
              allowNegative={allowNegatives}
              required
            />

            <div className="pt-2 text-xs text-slate-600 space-y-1 font-mono bg-white p-3 rounded-lg border border-slate-200">
              <div>
                <span className="font-bold text-slate-800">Controlled String:</span>{' '}
                <span className="text-indigo-600 font-bold">"{inrValue}"</span>
              </div>
              <div>
                <span className="font-bold text-slate-800">Parsed Numeric:</span>{' '}
                <span className="text-emerald-600 font-bold">
                  {inrNumeric !== null ? inrNumeric : 'null'}
                </span>
              </div>
            </div>
          </div>

          <div className="space-y-4">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500">
              Test Harness Controls
            </h3>
            <div className="grid grid-cols-2 gap-3 text-xs">
              <div>
                <label className="block text-slate-600 font-medium mb-1">Currency Symbol:</label>
                <select
                  value={currencyChoice}
                  onChange={(e) => setCurrencyChoice(e.target.value)}
                  className="w-full border border-slate-300 rounded px-2.5 py-1.5 bg-white font-mono text-xs"
                >
                  <option value="₹">₹ (Default INR Symbol)</option>
                  <option value="INR">INR (Currency Code)</option>
                  <option value="$">$ (USD Symbol)</option>
                  <option value="€">€ (EUR Symbol)</option>
                  <option value="£">£ (GBP Symbol)</option>
                </select>
              </div>

              <div>
                <label className="block text-slate-600 font-medium mb-1">Position:</label>
                <select
                  value={currencyPos}
                  onChange={(e) => setCurrencyPos(e.target.value as 'left' | 'right')}
                  className="w-full border border-slate-300 rounded px-2.5 py-1.5 bg-white text-xs"
                >
                  <option value="left">Left Prefix (Standard)</option>
                  <option value="right">Right Suffix</option>
                </select>
              </div>
            </div>

            <div className="flex flex-wrap gap-4 pt-2">
              <label className="flex items-center gap-2 text-xs font-medium text-slate-700 cursor-pointer">
                <input
                  type="checkbox"
                  checked={simulateError}
                  onChange={(e) => setSimulateError(e.target.checked)}
                  className="rounded text-indigo-600 focus:ring-indigo-500"
                />
                <span>Simulate Error State</span>
              </label>

              <label className="flex items-center gap-2 text-xs font-medium text-slate-700 cursor-pointer">
                <input
                  type="checkbox"
                  checked={simulateDisabled}
                  onChange={(e) => setSimulateDisabled(e.target.checked)}
                  className="rounded text-indigo-600 focus:ring-indigo-500"
                />
                <span>Simulate Disabled State</span>
              </label>

              <label className="flex items-center gap-2 text-xs font-medium text-slate-700 cursor-pointer">
                <input
                  type="checkbox"
                  checked={allowNegatives}
                  onChange={(e) => setAllowNegatives(e.target.checked)}
                  className="rounded text-indigo-600 focus:ring-indigo-500"
                />
                <span>Allow Negative (Credit)</span>
              </label>
            </div>
          </div>
        </div>

        {/* State Presets Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 pt-2">
          <div>
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider block mb-2">
              Default State (INR / ₹)
            </span>
            <MoneyInput
              value="500.00"
              placeholder="0.00"
              helperText="Standard product price"
            />
          </div>

          <div>
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider block mb-2">
              Disabled State
            </span>
            <MoneyInput
              value="2400.00"
              disabled
              helperText="Locked contract value"
            />
          </div>

          <div>
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider block mb-2">
              Error State
            </span>
            <MoneyInput
              value="99999.00"
              error="Deposit exceeds company credit limit"
            />
          </div>
        </div>
      </div>

      {/* 5. PasswordHints Section */}
      <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-xs space-y-6">
        <div>
          <h2 className="text-base font-semibold text-slate-900">5. PasswordHints Component</h2>
          <p className="text-xs text-slate-500 mt-0.5">
            SPEC 5.1 &amp; Must-pass validation checklist: Strictly &gt; 8 characters (8 characters rejected, 9 accepted), 1 uppercase, 1 lowercase, 1 special character.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 p-4 bg-slate-50 rounded-xl border border-slate-200">
          <div className="space-y-4">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500">
              Interactive Test Inputs
            </h3>

            <div>
              <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wide mb-1">
                Password:
              </label>
              <input
                type="text"
                value={demoPassword}
                onChange={(e) => setDemoPassword(e.target.value)}
                className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm bg-white font-mono focus:outline-hidden focus:ring-2 focus:ring-indigo-600"
                placeholder="Type a password..."
              />
              <span className="text-[11px] text-slate-500 mt-1 block font-mono">
                Length: <strong className="text-slate-800">{demoPassword.length}</strong> chars &bull; Rule &gt; 8 status:{' '}
                {demoPassword.length > 8 ? (
                  <span className="text-emerald-600 font-bold">PASS (&ge; 9)</span>
                ) : (
                  <span className="text-rose-600 font-bold">FAIL (8 or less)</span>
                )}
              </span>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wide mb-1">
                Confirm Password:
              </label>
              <input
                type="text"
                value={demoConfirmPassword}
                onChange={(e) => setDemoConfirmPassword(e.target.value)}
                className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm bg-white font-mono focus:outline-hidden focus:ring-2 focus:ring-indigo-600"
                placeholder="Confirm password..."
              />
            </div>

            <div className="pt-2">
              <span className="text-xs font-bold text-slate-600 block mb-2">Preset Test Cases:</span>
              <div className="flex flex-wrap gap-2">
                <button
                  type="button"
                  onClick={() => {
                    setDemoPassword('Pass!123'); // Exactly 8 chars
                    setDemoConfirmPassword('Pass!123');
                  }}
                  className="px-2.5 py-1 text-xs rounded-md bg-rose-50 text-rose-700 hover:bg-rose-100 border border-rose-200 font-mono font-medium"
                >
                  8 Chars ("Pass!123" &rarr; Fails)
                </button>

                <button
                  type="button"
                  onClick={() => {
                    setDemoPassword('Pass!1234'); // Exactly 9 chars
                    setDemoConfirmPassword('Pass!1234');
                  }}
                  className="px-2.5 py-1 text-xs rounded-md bg-emerald-50 text-emerald-700 hover:bg-emerald-100 border border-emerald-200 font-mono font-medium"
                >
                  9 Chars ("Pass!1234" &rarr; Passes)
                </button>

                <button
                  type="button"
                  onClick={() => {
                    setDemoPassword('password123!');
                    setDemoConfirmPassword('password123!');
                  }}
                  className="px-2.5 py-1 text-xs rounded-md bg-amber-50 text-amber-700 hover:bg-amber-100 border border-amber-200 font-mono font-medium"
                >
                  No Upper ("password123!")
                </button>

                <button
                  type="button"
                  onClick={() => {
                    setDemoPassword('Password123');
                    setDemoConfirmPassword('Password123');
                  }}
                  className="px-2.5 py-1 text-xs rounded-md bg-amber-50 text-amber-700 hover:bg-amber-100 border border-amber-200 font-mono font-medium"
                >
                  No Special ("Password123")
                </button>
              </div>
            </div>
          </div>

          <div className="space-y-4">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500">
              Live Checklist Display
            </h3>
            <PasswordHints password={demoPassword} confirmPassword={demoConfirmPassword} />

            <div className="p-3 rounded-lg border bg-white text-xs font-mono">
              Overall Validity:{' '}
              {evaluatePassword(demoPassword, demoConfirmPassword).isValid ? (
                <span className="font-bold text-emerald-600">VALID (Submit Enabled)</span>
              ) : (
                <span className="font-bold text-rose-600">INVALID (Submit Disabled)</span>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};


