// InvoiceDetailPage.tsx – Shows detailed view of a single invoice and actions
import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { getInvoice, confirmInvoice, cancelInvoice, sendInvoice, printInvoice } from '@/api/invoices';
import type { Invoice } from '@/api/mockData';

type InvoiceWithActions = Invoice & { allowed_actions?: string[] };

import { StatusBadge } from '@/components';
import { ArrowLeft } from 'lucide-react';
import { cn } from '@/lib/utils';
import { RecordPaymentDialog } from '@/components/RecordPaymentDialog';

export const InvoiceDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const invoiceId = Number(id);
  const [invoice, setInvoice] = useState<InvoiceWithActions | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showPaymentDialog, setShowPaymentDialog] = useState(false);

  const fetchInvoice = async () => {
    setLoading(true);
    try {
      const data = await getInvoice(invoiceId);
      setInvoice(data);
    } catch (e: any) {
      setError(e?.message ?? 'Failed to load invoice');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (!isNaN(invoiceId)) fetchInvoice();
  }, [invoiceId]);

  const handleAction = async (action: 'confirm' | 'cancel' | 'send' | 'print') => {
    if (!invoice) return;
    try {
      if (action === 'confirm') await confirmInvoice(invoice.id);
      if (action === 'cancel') await cancelInvoice(invoice.id);
      if (action === 'send') await sendInvoice(invoice.id);
      if (action === 'print') await printInvoice(invoice.id);
      await fetchInvoice();
    } catch (e: any) {
      alert(`Action failed: ${e?.message || 'unknown error'}`);
    }
  };

  const allowedActions = () => {
    // Use backend provided allowed_actions if present, else infer from status
    const actions: string[] = [];
    if (invoice?.allowed_actions) {
      return invoice.allowed_actions as string[];
    }
    const status = invoice?.status?.toLowerCase();
    if (status === 'draft') {
      actions.push('confirm', 'cancel');
    } else if (status === 'confirmed') {
      actions.push('send', 'print');
    } else if (status === 'paid') {
      actions.push('print');
    }
    return actions;
  };

  if (loading) {
    return <div className="text-center py-8 text-slate-500">Loading invoice...</div>;
  }

  if (error) {
    return (
      <div className="p-4 bg-rose-50 border border-rose-200 text-rose-700 rounded">
        <p>{error}</p>
        <button onClick={fetchInvoice} className="mt-2 underline text-sm">Retry</button>
      </div>
    );
  }

  if (!invoice) {
    return <div className="text-center py-8 text-slate-500">Invoice not found.</div>;
  }

  const actions = allowedActions();

  return (
    <div className="space-y-6 max-w-4xl mx-auto p-4">
      <div className="flex items-center space-x-4">
        <button onClick={() => window.history.back()} className="text-slate-500 hover:text-slate-700">
          <ArrowLeft className="w-5 h-5" /> Back
        </button>
        <h1 className="text-2xl font-bold">Invoice #{invoice.invoice_number}</h1>
        <StatusBadge status={invoice.status as any} kind="invoice" overdue={invoice.is_overdue} daysOverdue={invoice.days_overdue} />
      </div>
      <div className="grid grid-cols-2 gap-4">
        <div>
          <p className="font-medium">Customer</p>
          <p>{invoice.customer_name}</p>
        </div>
        <div>
          <p className="font-medium">Issue Date</p>
          <p>{invoice.issue_date}</p>
        </div>
        <div>
          <p className="font-medium">Due Date</p>
          <p>{invoice.due_date}</p>
        </div>
        <div>
          <p className="font-medium">Total</p>
          <p className="font-bold">${invoice.total}</p>
        </div>
        <div>
          <p className="font-medium">Paid</p>
          <p className="text-emerald-700">${invoice.amount_paid}</p>
        </div>
        <div>
          <p className="font-medium">Balance</p>
          <p className={cn('font-bold', Number(invoice.balance) > 0 ? 'text-rose-600' : 'text-slate-500')}>${invoice.balance}</p>
        </div>
      </div>
      {/* Line items table */}
      <div className="bg-white rounded-xl border border-slate-200 overflow-hidden shadow-xs">
        <table className="w-full text-left text-xs">
          <thead className="bg-slate-50 text-slate-600 border-b border-slate-200 uppercase font-semibold">
            <tr>
              <th className="p-2">Description</th>
              <th className="p-2">Qty</th>
              <th className="p-2">Unit Price</th>
              <th className="p-2">Amount</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-200">
            {invoice.lines?.map((line, idx) => (
              <tr key={idx} className="hover:bg-slate-50">
                <td className="p-2">{line.description}</td>
                <td className="p-2 text-center">{line.quantity}</td>
                <td className="p-2 text-right">${line.unit_price}</td>
                <td className="p-2 text-right font-medium">${line.total}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {/* Actions */}
      <div className="flex space-x-3">
        {actions.includes('confirm') && (
          <button onClick={() => handleAction('confirm')} className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded">
            Confirm
          </button>
        )}
        {actions.includes('cancel') && (
          <button onClick={() => handleAction('cancel')} className="px-4 py-2 bg-rose-600 hover:bg-rose-700 text-white rounded">
            Cancel
          </button>
        )}
        {actions.includes('send') && (
          <button onClick={() => handleAction('send')} className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded">
            Send
          </button>
        )}
        {actions.includes('print') && (
          <button onClick={() => handleAction('print')} className="px-4 py-2 bg-slate-600 hover:bg-slate-700 text-white rounded">
            Print
          </button>
        )}
        <button onClick={() => setShowPaymentDialog(true)} className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded">
          Record Payment
        </button>
      </div>
      {showPaymentDialog && (
        <RecordPaymentDialog
          invoiceId={invoice.id}
          open={true}
          onClose={() => setShowPaymentDialog(false)}
          onSuccess={fetchInvoice}
          balance={invoice.balance}
        />
      )}
    </div>
  );
};
