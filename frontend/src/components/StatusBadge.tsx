import React from 'react';
import { cn } from '@/lib/utils';

export type BadgeStatus =
  | 'draft'
  | 'quotation'
  | 'confirmed'
  | 'active'
  | 'closed'
  | 'paid'
  | 'cancelled'
  | string;

export interface StatusBadgeProps {
  status: BadgeStatus;
  kind?: 'subscription' | 'invoice';
  overdue?: boolean;
  daysOverdue?: number;
  className?: string;
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({
  status,
  kind,
  overdue = false,
  daysOverdue,
  className,
}) => {
  const normalized = (status || '').toLowerCase().trim();

  // If marked overdue or has days overdue > 0 for invoices
  if (overdue || (kind === 'invoice' && typeof daysOverdue === 'number' && daysOverdue > 0)) {
    const overdueText = daysOverdue ? `Overdue (${daysOverdue}d)` : 'Overdue';
    return (
      <span
        className={cn(
          'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold tracking-wide border',
          'bg-rose-100 text-rose-800 border-rose-300 animate-pulse',
          className
        )}
      >
        <span className="w-1.5 h-1.5 rounded-full bg-rose-600 mr-1.5" />
        {overdueText}
      </span>
    );
  }

  // Exact colour mapping matching SPEC & Lead Guide:
  // draft grey, quotation blue, confirmed amber, active green, closed slate, paid green, cancelled red
  let colorClasses = 'bg-slate-100 text-slate-700 border-slate-300';
  let dotColor = 'bg-slate-500';

  switch (normalized) {
    case 'draft':
      colorClasses = 'bg-slate-100 text-slate-700 border-slate-300';
      dotColor = 'bg-slate-500';
      break;
    case 'quotation':
      colorClasses = 'bg-blue-50 text-blue-700 border-blue-200';
      dotColor = 'bg-blue-600';
      break;
    case 'confirmed':
      colorClasses = 'bg-amber-50 text-amber-700 border-amber-300';
      dotColor = 'bg-amber-500';
      break;
    case 'active':
      colorClasses = 'bg-emerald-50 text-emerald-700 border-emerald-300';
      dotColor = 'bg-emerald-600';
      break;
    case 'closed':
      colorClasses = 'bg-zinc-100 text-zinc-600 border-zinc-300';
      dotColor = 'bg-zinc-500';
      break;
    case 'paid':
      colorClasses = 'bg-emerald-50 text-emerald-700 border-emerald-300';
      dotColor = 'bg-emerald-600';
      break;
    case 'cancelled':
      colorClasses = 'bg-red-50 text-red-700 border-red-300';
      dotColor = 'bg-red-500';
      break;
    default:
      colorClasses = 'bg-slate-100 text-slate-700 border-slate-300';
      dotColor = 'bg-slate-400';
  }

  const label = normalized.charAt(0).toUpperCase() + normalized.slice(1);

  return (
    <span
      className={cn(
        'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border uppercase tracking-wider',
        colorClasses,
        className
      )}
    >
      <span className={cn('w-1.5 h-1.5 rounded-full mr-1.5', dotColor)} />
      {label}
    </span>
  );
};
