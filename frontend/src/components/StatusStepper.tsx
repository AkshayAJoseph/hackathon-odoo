import React from 'react';
import { Check, CircleDot } from 'lucide-react';
import { cn } from '@/lib/utils';

export type SubscriptionStep = 'draft' | 'quotation' | 'confirmed' | 'active' | 'closed';

const STEPS: { key: SubscriptionStep; label: string }[] = [
  { key: 'draft', label: 'Draft' },
  { key: 'quotation', label: 'Quotation' },
  { key: 'confirmed', label: 'Confirmed' },
  { key: 'active', label: 'Active' },
  { key: 'closed', label: 'Closed' },
];

export interface StatusStepperProps {
  status: string;
  className?: string;
}

export const StatusStepper: React.FC<StatusStepperProps> = ({ status, className }) => {
  const normalized = (status || '').toLowerCase().trim();
  const currentIndex = STEPS.findIndex((s) => s.key === normalized);
  // Default to 0 if not found
  const activeIndex = currentIndex === -1 ? 0 : currentIndex;

  return (
    <div className={cn('w-full py-3', className)}>
      <div className="flex items-center justify-between">
        {STEPS.map((step, idx) => {
          const isCompleted = idx < activeIndex;
          const isCurrent = idx === activeIndex;
          const isUpcoming = idx > activeIndex;

          return (
            <React.Fragment key={step.key}>
              <div className="flex flex-col items-center relative group">
                <div
                  className={cn(
                    'w-8 h-8 rounded-full flex items-center justify-center font-semibold text-xs border-2 transition-all duration-200',
                    isCompleted && 'bg-emerald-600 border-emerald-600 text-white shadow-sm',
                    isCurrent && 'bg-indigo-600 border-indigo-600 text-white ring-4 ring-indigo-100 shadow-md',
                    isUpcoming && 'bg-white border-slate-300 text-slate-400'
                  )}
                >
                  {isCompleted ? (
                    <Check className="w-4 h-4" />
                  ) : isCurrent ? (
                    <CircleDot className="w-4 h-4 animate-spin-slow" />
                  ) : (
                    <span>{idx + 1}</span>
                  )}
                </div>
                <span
                  className={cn(
                    'mt-2 text-xs font-medium tracking-tight',
                    isCurrent ? 'text-indigo-700 font-bold' : isCompleted ? 'text-emerald-700' : 'text-slate-400'
                  )}
                >
                  {step.label}
                </span>
              </div>

              {/* Connecting line between steps */}
              {idx < STEPS.length - 1 && (
                <div
                  className={cn(
                    'flex-1 h-0.5 mx-2 transition-all duration-300',
                    idx < activeIndex ? 'bg-emerald-600' : 'bg-slate-200'
                  )}
                />
              )}
            </React.Fragment>
          );
        })}
      </div>
    </div>
  );
};
