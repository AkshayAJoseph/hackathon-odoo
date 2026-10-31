import React, { useState, useEffect } from 'react';
import { StatusBadge } from '@/components';
import { CreditCard, Printer, Shield, RefreshCw } from 'lucide-react';
import { apiClient } from '@/api';
import { cn } from '@/lib/utils';

interface InvoiceItem {
  id: number;
  number?: string;
  invoice_number?: string;
  issue_date: string;
  due_date: string;
  total: string;
  amount_paid: string;
  balance?: string;
  status: string;
}

export const CustomerInvoicesPage: React.FC = () => {
  const [invoices, setInvoices] = useState<InvoiceItem[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  const fetchInvoices = async () => {
    try {
      setLoading(true);
      const res = await apiClient.get<any>('/portal/invoices/');
      const list = res.results || res || [];
      if (Array.isArray(list)) {
        setInvoices(list);
      }
    } catch (err) {
      console.error('Failed to load customer invoices:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchInvoices();
  }, []);

  const handlePrint = (invId: number) => {
    const url = `${import.meta.env.VITE_API_URL || 'http://localhost:8000/api'}/invoices/${invId}/print/`;
    window.open(url, '_blank');
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">My Invoices</h1>
          <p className="text-xs text-slate-500 mt-1">
            Download statements, track outstanding balances, and check payment history.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1.5 px-3 py-1 bg-emerald-50 text-emerald-700 text-xs font-semibold rounded-lg border border-emerald-200">
            <Shield className="w-3.5 h-3.5" />
            <span>Customer Scoped</span>
          </div>
          <button
            onClick={fetchInvoices}
            className="p-1.5 bg-slate-100 hover:bg-slate-200 rounded-lg text-slate-600 transition"
            title="Refresh Invoices"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      <div className="bg-white rounded-xl border border-slate-200 overflow-hidden shadow-xs">
        <table className="w-full text-left text-xs">
          <thead className="bg-slate-50 text-slate-600 border-b border-slate-200 uppercase font-semibold">
            <tr>
              <th className="p-4">Invoice #</th>
              <th className="p-4">Issue Date</th>
              <th className="p-4">Due Date</th>
              <th className="p-4">Invoice Total</th>
              <th className="p-4">Amount Paid</th>
              <th className="p-4">Balance</th>
              <th className="p-4">Status</th>
              <th className="p-4 text-right">Receipt</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-200">
            {invoices.length === 0 ? (
              <tr>
                <td colSpan={8} className="p-6 text-center text-slate-400">
                  {loading ? 'Loading invoices...' : 'No invoices found.'}
                </td>
              </tr>
            ) : (
              invoices.map((inv) => {
                const invNum = inv.number || inv.invoice_number || `INV-${inv.id}`;
                const totalNum = Number(inv.total) || 0;
                const paidNum = Number(inv.amount_paid) || 0;
                const balanceVal = inv.balance !== undefined ? inv.balance : (totalNum - paidNum).toFixed(2);

                return (
                  <tr key={inv.id} className="hover:bg-slate-50">
                    <td className="p-4 font-mono font-bold text-indigo-700 flex items-center gap-1.5">
                      <CreditCard className="w-4 h-4 text-slate-400" />
                      {invNum}
                    </td>
                    <td className="p-4 font-mono text-slate-500">{inv.issue_date}</td>
                    <td className="p-4 font-mono text-slate-500">{inv.due_date}</td>
                    <td className="p-4 font-mono font-bold text-slate-900">${inv.total}</td>
                    <td className="p-4 font-mono text-emerald-700 font-semibold">${inv.amount_paid}</td>
                    <td className={cn('p-4 font-mono font-bold', Number(balanceVal) > 0 ? 'text-rose-600' : 'text-slate-500')}>
                      ${balanceVal}
                    </td>
                    <td className="p-4">
                      <StatusBadge
                        status={inv.status}
                        kind="invoice"
                      />
                    </td>
                    <td className="p-4 text-right">
                      <button
                        onClick={() => handlePrint(inv.id)}
                        className="inline-flex items-center gap-1 px-2.5 py-1 text-[11px] font-semibold text-slate-700 bg-slate-100 hover:bg-slate-200 rounded border border-slate-300 transition"
                      >
                        <Printer className="w-3.5 h-3.5" />
                        Print / Receipt
                      </button>
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};
