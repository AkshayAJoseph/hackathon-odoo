import React from 'react';
import { MOCK_INVOICES } from '@/api';
import { StatusBadge } from '@/components';
import { CreditCard, Printer, Send } from 'lucide-react';
import { cn } from '@/lib/utils';

export const InvoicesListPage: React.FC = () => {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Billing & Invoices</h1>
          <p className="text-xs text-slate-500 mt-1">
            Accounts receivable, invoice dispatch, and payment collection.
          </p>
        </div>
      </div>

      <div className="bg-white rounded-xl border border-slate-200 overflow-hidden shadow-xs">
        <table className="w-full text-left text-xs">
          <thead className="bg-slate-50 text-slate-600 border-b border-slate-200 uppercase font-semibold">
            <tr>
              <th className="p-4">Invoice #</th>
              <th className="p-4">Customer</th>
              <th className="p-4">Due Date</th>
              <th className="p-4">Total</th>
              <th className="p-4">Paid</th>
              <th className="p-4">Balance</th>
              <th className="p-4">Status</th>
              <th className="p-4 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-200">
            {MOCK_INVOICES.map((inv) => (
              <tr
                key={inv.id}
                className={cn(
                  'hover:bg-slate-50 transition-colors',
                  inv.is_overdue && 'bg-rose-50/60 border-l-4 border-l-rose-500'
                )}
              >
                <td className="p-4 font-mono font-bold text-indigo-700 flex items-center gap-1.5">
                  <CreditCard className="w-4 h-4 text-slate-400" />
                  {inv.invoice_number}
                </td>
                <td className="p-4 font-medium text-slate-900">{inv.customer_name}</td>
                <td className="p-4 font-mono text-slate-500">{inv.due_date}</td>
                <td className="p-4 font-mono font-bold text-slate-900">${inv.total}</td>
                <td className="p-4 font-mono text-emerald-700 font-semibold">${inv.amount_paid}</td>
                <td className={cn('p-4 font-mono font-bold', Number(inv.balance) > 0 ? 'text-rose-600' : 'text-slate-500')}>
                  ${inv.balance}
                </td>
                <td className="p-4">
                  <StatusBadge
                    status={inv.status}
                    kind="invoice"
                    overdue={inv.is_overdue}
                    daysOverdue={inv.days_overdue}
                  />
                </td>
                <td className="p-4 text-right space-x-2">
                  <button title="Print Invoice" className="p-1.5 text-slate-500 hover:text-slate-800 rounded">
                    <Printer className="w-3.5 h-3.5" />
                  </button>
                  <button title="Email Invoice" className="p-1.5 text-slate-500 hover:text-indigo-600 rounded">
                    <Send className="w-3.5 h-3.5" />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
