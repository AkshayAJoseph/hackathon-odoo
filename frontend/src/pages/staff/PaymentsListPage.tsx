// Payments list page – shows all payments from the backend API
import React, { useEffect, useState } from 'react';
import { listPayments } from '@/api/payments';
import { useNavigate } from 'react-router-dom';
import { cn } from '@/lib/utils';
import type { Payment } from '@/api/mockData';

export const PaymentsListPage: React.FC = () => {
  const navigate = useNavigate();
  const [payments, setPayments] = useState<Payment[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchPayments = async () => {
    setLoading(true);
    try {
      const data = await listPayments();
      setPayments(data);
    } catch (e: any) {
      setError(e?.message ?? 'Failed to load payments');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPayments();
  }, []);

  if (loading) {
    return <div className="text-center py-8 text-slate-500">Loading payments…</div>;
  }

  if (error) {
    return (
      <div className="p-4 bg-rose-50 border border-rose-200 text-rose-700 rounded">
        <p>{error}</p>
        <button onClick={fetchPayments} className="mt-2 underline text-sm">
          Retry
        </button>
      </div>
    );
  }

  if (payments.length === 0) {
    return <div className="text-center py-8 text-slate-500">No payments found.</div>;
  }

  return (
    <div className="space-y-6 max-w-4xl mx-auto p-4">
      <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Payments History</h1>
      <div className="bg-white rounded-xl border border-slate-200 overflow-hidden shadow-xs">
        <table className="w-full text-left text-xs">
          <thead className="bg-slate-50 text-slate-600 border-b border-slate-200 uppercase font-semibold">
            <tr>
              <th className="p-4">ID</th>
              <th className="p-4">Description</th>
              <th className="p-4">Amount</th>
              <th className="p-4">Date</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-200">
            {payments.map((pay) => (
              <tr
                key={pay.id}
                className={cn('cursor-pointer hover:bg-slate-50 transition-colors')}
                onClick={() => navigate(`/staff/payments/${pay.id}`)}
              >
                <td className="p-4 font-mono text-slate-900">{pay.id}</td>
                <td className="p-4 text-slate-900">{pay.note ?? '—'}</td>
                <td className="p-4 font-mono text-slate-900">${pay.amount}</td>
                <td className="p-4 text-slate-500">{pay.payment_date}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
