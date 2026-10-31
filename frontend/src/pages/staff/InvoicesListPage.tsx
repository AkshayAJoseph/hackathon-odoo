// Invoices list page using real backend API
import React, { useEffect, useState } from 'react';
import { listInvoices, confirmInvoice, cancelInvoice, sendInvoice, printInvoice } from '@/api/invoices';
import { useNavigate } from 'react-router-dom';
import { StatusBadge } from '@/components';
import { CreditCard, Printer, Send, CheckCircle2, XCircle } from 'lucide-react';
import { cn } from '@/lib/utils';
import type { Invoice } from '@/api/mockData';

export const InvoicesListPage: React.FC = () => {
  const navigate = useNavigate();
  const [invoices, setInvoices] = useState<Invoice[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchInvoices = async () => {
    setLoading(true);
    try {
      const data = await listInvoices();
      setInvoices(data);
    } catch (e: any) {
      setError(e?.message ?? 'Failed to load invoices');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchInvoices();
  }, []);

  const handleAction = async (id: number, action: 'confirm' | 'cancel' | 'send' | 'print') => {
    try {
      if (action === 'confirm') await confirmInvoice(id);
      if (action === 'cancel') await cancelInvoice(id);
      if (action === 'send') await sendInvoice(id);
      if (action === 'print') await printInvoice(id);
      // Refresh after action
      await fetchInvoices();
    } catch (e: any) {
      alert(`Action failed: ${e?.message || 'unknown error'}`);
    }
  };

  if (loading) {
    return <div className="text-center py-8 text-slate-500">Loading invoices...</div>;
  }

  if (error) {
    return (
      <div className="p-4 bg-rose-50 border border-rose-200 text-rose-700 rounded">
        <p>{error}</p>
        <button onClick={fetchInvoices} className="mt-2 underline text-sm">
          Retry
        </button>
      </div>
    );
  }

  if (invoices.length === 0) {
    return <div className="text-center py-8 text-slate-500">No invoices found.</div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Billing & Invoices</h1>
          <p className="text-xs text-slate-500 mt-1">Accounts receivable, invoice dispatch, and payment collection.</p>
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
            {invoices.map((inv) => (
              <tr
                key={inv.id} onClick={() => navigate(`/staff/invoices/${inv.id}`)}
                className={cn(
                  'cursor-pointer hover:bg-slate-50 transition-colors',
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
                  <StatusBadge status={inv.status} kind="invoice" overdue={inv.is_overdue} daysOverdue={inv.days_overdue} />
                </td>
                <td className="p-4 text-right space-x-2">
                  <button
                    title="Print Invoice"
                    className="p-1.5 text-slate-500 hover:text-slate-800 rounded"
                    onClick={() => handleAction(inv.id, 'print')}
                  >
                    <Printer className="w-3.5 h-3.5" />
                  </button>
                  <button
                    title="Email Invoice"
                    className="p-1.5 text-slate-500 hover:text-indigo-600 rounded"
                    onClick={() => handleAction(inv.id, 'send')}
                  >
                    <Send className="w-3.5 h-3.5" />
                  </button>
                  {/* Example additional actions */}
                  <button
                    title="Confirm"
                    className="p-1.5 text-green-600 hover:text-green-800 rounded"
                    onClick={() => handleAction(inv.id, 'confirm')}
                  >
                    <CheckCircle2 className="w-3.5 h-3.5" />
                  </button>
                  <button
                    title="Cancel"
                    className="p-1.5 text-rose-600 hover:text-rose-800 rounded"
                    onClick={() => handleAction(inv.id, 'cancel')}
                  >
                    <XCircle className="w-3.5 h-3.5" />
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
