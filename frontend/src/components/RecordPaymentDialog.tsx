// RecordPaymentDialog.tsx – reusable modal dialog for recording a payment on an invoice
import React, { useState } from 'react';
import { X } from 'lucide-react';

import { recordInvoicePayment } from '@/api/invoices';


interface RecordPaymentDialogProps {
  invoiceId: number;
  open: boolean;
  onClose: () => void;
  onSuccess: () => void; // callback to refresh invoice details after payment recorded
  balance: string; // outstanding amount as string (decimal)
}

export const RecordPaymentDialog: React.FC<RecordPaymentDialogProps> = ({ invoiceId, open, onClose, onSuccess, balance }) => {
  const [method, setMethod] = useState('card');
  const [amount, setAmount] = useState('');
  const [paymentDate, setPaymentDate] = useState('');
  const [note, setNote] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  if (!open) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    const amtNum = Number(amount);
    const balNum = Number(balance);
    if (isNaN(amtNum) || amtNum <= 0) {
      setError('Amount must be a positive number');
      return;
    }
    if (amtNum > balNum) {
      setError('Amount cannot exceed outstanding balance');
      return;
    }
    setSubmitting(true);
    try {
      await recordInvoicePayment(invoiceId, {
        method,
        amount: amount.toString(),
        payment_date: paymentDate || undefined,
        note: note || undefined,
      });
      onSuccess();
      onClose();
    } catch (e: any) {
      setError(e?.message ?? 'Failed to record payment');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/30">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-md p-6 relative">
        <button
          className="absolute top-2 right-2 text-slate-400 hover:text-slate-600"
          onClick={onClose}
        >
          <X className="w-5 h-5" />
        </button>
        <h2 className="text-lg font-semibold mb-4">Record Payment</h2>
        {error && (
          <div className="p-2 mb-3 bg-rose-50 border border-rose-200 text-rose-700 rounded">
            {error}
          </div>
        )}
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1" htmlFor="method">
              Payment Method
            </label>
            <select
              id="method"
              value={method}
              onChange={(e) => setMethod(e.target.value)}
              className="w-full border rounded px-2 py-1"
            >
              <option value="card">Card</option>
              <option value="bank_transfer">Bank Transfer</option>
              <option value="upi">UPI</option>
              <option value="cash">Cash</option>
              <option value="cheque">Cheque</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium mb-1" htmlFor="amount">
              Amount (outstanding: {balance})
            </label>
            <input
              id="amount"
              type="number"
              step="0.01"
              min="0"
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
              className="w-full border rounded px-2 py-1"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1" htmlFor="paymentDate">
              Payment Date (optional)
            </label>
            <input
              id="paymentDate"
              type="date"
              value={paymentDate}
              onChange={(e) => setPaymentDate(e.target.value)}
              className="w-full border rounded px-2 py-1"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1" htmlFor="note">
              Note (optional)
            </label>
            <textarea
              id="note"
              rows={2}
              value={note}
              onChange={(e) => setNote(e.target.value)}
              className="w-full border rounded px-2 py-1"
            />
          </div>
          <div className="flex justify-end space-x-2 pt-2">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded"
              disabled={submitting}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded disabled:opacity-50"
              disabled={submitting}
            >
              {submitting ? 'Recording...' : 'Record'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
