import React, { forwardRef, useId } from 'react';
import { cn } from '@/lib/utils';
import { AlertCircle } from 'lucide-react';

export interface MoneyInputProps
  extends Omit<React.InputHTMLAttributes<HTMLInputElement>, 'value' | 'onChange'> {
  /** Controlled monetary value (string or numeric) */
  value: string | number;
  /** Callback fired with the sanitized monetary string and parsed numeric value (or null if empty/invalid) */
  onChange?: (value: string, numValue: number | null) => void;
  /** Currency indicator symbol or code. Default: '₹' */
  currency?: string;
  /** Position of the currency indicator: 'left' | 'right'. Default: 'left' */
  currencyPosition?: 'left' | 'right';
  /** Field label rendered above the input */
  label?: string;
  /** Error message string or boolean flag indicating error state */
  error?: string | boolean;
  /** Helper text displayed below input when not in error state */
  helperText?: string;
  /** Whether the input is disabled */
  disabled?: boolean;
  /** Placeholder text. Default: '0.00' */
  placeholder?: string;
  /** Whether decimal numbers are allowed. Default: true */
  allowDecimals?: boolean;
  /** Maximum number of decimal places allowed. Default: 2 */
  decimalScale?: number;
  /** Whether negative amounts are allowed. Default: false */
  allowNegative?: boolean;
  /** Additional CSS classes for outer container */
  containerClassName?: string;
}

/**
 * Sanitizes input string to keep valid monetary characters according to options.
 */
function sanitizeMonetaryInput(
  raw: string,
  options: { allowDecimals?: boolean; decimalScale?: number; allowNegative?: boolean }
): string {
  const { allowDecimals = true, decimalScale = 2, allowNegative = false } = options;

  let cleaned = raw.trim();

  // Preserve leading minus if negative is allowed
  const isNegative = allowNegative && cleaned.startsWith('-');

  // Strip all non-numeric and non-decimal characters
  cleaned = cleaned.replace(/[^0-9.]/g, '');

  if (!allowDecimals) {
    cleaned = cleaned.replace(/\./g, '');
  } else {
    // Keep only the first decimal point
    const parts = cleaned.split('.');
    if (parts.length > 2) {
      cleaned = `${parts[0]}.${parts.slice(1).join('')}`;
    }
    // Limit digits after the decimal point
    if (parts.length >= 2 && typeof decimalScale === 'number' && decimalScale >= 0) {
      cleaned = `${parts[0]}.${parts[1].slice(0, decimalScale)}`;
    }
  }

  if (isNegative && cleaned.length > 0) {
    cleaned = `-${cleaned}`;
  }

  return cleaned;
}

/**
 * Computes numeric value from string or returns null.
 */
function parseNumericValue(val: string): number | null {
  if (val === '' || val === '-' || val === '.') return null;
  const num = Number(val);
  return isNaN(num) ? null : num;
}

/**
 * Reusable, typed monetary input component for Brightloop.
 * Displays a currency indicator (default INR/₹), supports controlled value/onChange,
 * placeholder, disabled, and error states without business calculations or conversions.
 */
export const MoneyInput = forwardRef<HTMLInputElement, MoneyInputProps>(
  (
    {
      value,
      onChange,
      currency = '₹',
      currencyPosition = 'left',
      label,
      error,
      helperText,
      disabled = false,
      placeholder = '0.00',
      allowDecimals = true,
      decimalScale = 2,
      allowNegative = false,
      containerClassName,
      className,
      id,
      required,
      ...restProps
    },
    ref
  ) => {
    const generatedId = useId();
    const inputId = id || generatedId;
    const errorId = `${inputId}-error`;
    const helperId = `${inputId}-helper`;

    const hasError = Boolean(error);
    const displayValue = value === null || value === undefined ? '' : String(value);

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
      const raw = e.target.value;
      const sanitized = sanitizeMonetaryInput(raw, {
        allowDecimals,
        decimalScale,
        allowNegative,
      });

      const numValue = parseNumericValue(sanitized);
      onChange?.(sanitized, numValue);
    };

    return (
      <div className={cn('w-full', containerClassName)}>
        {label && (
          <label
            htmlFor={inputId}
            className="block text-xs font-semibold text-slate-700 uppercase tracking-wide mb-1.5"
          >
            {label}
            {required && <span className="text-red-500 ml-1">*</span>}
          </label>
        )}

        <div
          className={cn(
            'group relative flex items-stretch rounded-lg border bg-white shadow-xs transition-colors',
            hasError
              ? 'border-red-300 focus-within:border-red-500 focus-within:ring-2 focus-within:ring-red-100'
              : 'border-slate-300 focus-within:border-indigo-600 focus-within:ring-2 focus-within:ring-indigo-100',
            disabled && 'bg-slate-50 border-slate-200 cursor-not-allowed opacity-80'
          )}
        >
          {currencyPosition === 'left' && (
            <span
              aria-hidden="true"
              className={cn(
                'inline-flex items-center px-3 text-xs font-semibold select-none border-r rounded-l-lg transition-colors font-mono',
                hasError
                  ? 'bg-red-50 text-red-600 border-red-200'
                  : disabled
                  ? 'bg-slate-100 text-slate-400 border-slate-200'
                  : 'bg-slate-50 text-slate-600 border-slate-200 group-hover:bg-slate-100/70'
              )}
            >
              {currency}
            </span>
          )}

          <input
            ref={ref}
            id={inputId}
            type="text"
            inputMode="decimal"
            value={displayValue}
            onChange={handleChange}
            disabled={disabled}
            placeholder={placeholder}
            aria-invalid={hasError}
            aria-describedby={hasError && typeof error === 'string' ? errorId : helperText ? helperId : undefined}
            required={required}
            className={cn(
              'w-full min-w-0 flex-1 bg-transparent px-3 py-2 text-sm text-slate-900 placeholder:text-slate-400 focus:outline-none font-mono',
              disabled && 'cursor-not-allowed text-slate-400',
              currencyPosition === 'left' ? 'rounded-r-lg' : 'rounded-l-lg',
              className
            )}
            {...restProps}
          />

          {currencyPosition === 'right' && (
            <span
              aria-hidden="true"
              className={cn(
                'inline-flex items-center px-3 text-xs font-semibold select-none border-l rounded-r-lg transition-colors font-mono',
                hasError
                  ? 'bg-red-50 text-red-600 border-red-200'
                  : disabled
                  ? 'bg-slate-100 text-slate-400 border-slate-200'
                  : 'bg-slate-50 text-slate-600 border-slate-200 group-hover:bg-slate-100/70'
              )}
            >
              {currency}
            </span>
          )}
        </div>

        {hasError && typeof error === 'string' && (
          <p id={errorId} className="mt-1.5 text-xs text-red-600 flex items-center gap-1 font-medium">
            <AlertCircle className="w-3.5 h-3.5 flex-shrink-0" />
            <span>{error}</span>
          </p>
        )}

        {!hasError && helperText && (
          <p id={helperId} className="mt-1.5 text-xs text-slate-500">
            {helperText}
          </p>
        )}
      </div>
    );
  }
);

MoneyInput.displayName = 'MoneyInput';
