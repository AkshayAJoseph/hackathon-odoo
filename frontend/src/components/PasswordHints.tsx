import React from 'react';
import { cn } from '@/lib/utils';
import { Check, X } from 'lucide-react';

export interface PasswordRule {
  id: string;
  label: string;
  met: boolean;
}

export interface PasswordValidation {
  /** Whether the password length is strictly greater than 8 (i.e. at least 9 characters) */
  isLengthValid: boolean;
  /** Whether the password contains at least one uppercase ASCII letter */
  hasUppercase: boolean;
  /** Whether the password contains at least one lowercase ASCII letter */
  hasLowercase: boolean;
  /** Whether the password contains at least one special character */
  hasSpecialChar: boolean;
  /** Whether confirmPassword matches password (if confirmPassword was provided) */
  passwordsMatch?: boolean;
  /** Whether all password rules are satisfied */
  isValid: boolean;
  /** List of evaluated rules with met status */
  rules: PasswordRule[];
}

/**
 * Validates password according to Brightloop SPEC 5.1:
 * - Length strictly greater than 8 characters (8 rejected, 9 accepted)
 * - At least one uppercase letter (A-Z)
 * - At least one lowercase letter (a-z)
 * - At least one special character (non-alphanumeric)
 * - Optionally checks password confirmation match
 */
export function evaluatePassword(password: string, confirmPassword?: string): PasswordValidation {
  // STRICT SPEC 5.1: length > 8 (so exactly 8 characters fails, 9+ characters passes)
  const isLengthValid = password.length > 8;
  const hasUppercase = /[A-Z]/.test(password);
  const hasLowercase = /[a-z]/.test(password);
  const hasSpecialChar = /[^a-zA-Z0-9]/.test(password);

  const rules: PasswordRule[] = [
    {
      id: 'length',
      label: 'More than 8 characters (at least 9)',
      met: isLengthValid,
    },
    {
      id: 'uppercase',
      label: 'At least one uppercase letter (A-Z)',
      met: hasUppercase,
    },
    {
      id: 'lowercase',
      label: 'At least one lowercase letter (a-z)',
      met: hasLowercase,
    },
    {
      id: 'special',
      label: 'At least one special character (!@#$%^&*...)',
      met: hasSpecialChar,
    },
  ];

  let passwordsMatch: boolean | undefined = undefined;
  if (confirmPassword !== undefined) {
    passwordsMatch = password.length > 0 && password === confirmPassword;
    rules.push({
      id: 'match',
      label: 'Passwords match',
      met: passwordsMatch,
    });
  }

  const isValid =
    isLengthValid &&
    hasUppercase &&
    hasLowercase &&
    hasSpecialChar &&
    (passwordsMatch === undefined || passwordsMatch);

  return {
    isLengthValid,
    hasUppercase,
    hasLowercase,
    hasSpecialChar,
    passwordsMatch,
    isValid,
    rules,
  };
}

export interface PasswordHintsProps {
  /** The password string being entered */
  password: string;
  /** Optional confirmation password string */
  confirmPassword?: string;
  /** Optional title override */
  title?: string;
  /** Additional container styling */
  className?: string;
}

/**
 * Reusable PasswordHints component.
 * Dynamically displays progress against Brightloop's 4 password rules (plus optional confirmation).
 */
export const PasswordHints: React.FC<PasswordHintsProps> = ({
  password,
  confirmPassword,
  title = 'Password Requirements:',
  className,
}) => {
  const { rules } = evaluatePassword(password, confirmPassword);

  return (
    <div
      className={cn(
        'p-3 bg-slate-50 border border-slate-200 rounded-lg space-y-1.5 text-xs transition-colors',
        className
      )}
    >
      {title && <span className="font-semibold text-slate-700 block mb-1">{title}</span>}
      <ul className="space-y-1">
        {rules.map((rule) => (
          <li
            key={rule.id}
            className={cn(
              'flex items-center gap-2 transition-colors',
              rule.met ? 'text-emerald-700 font-medium' : 'text-slate-500'
            )}
          >
            <span
              className={cn(
                'flex items-center justify-center w-4 h-4 rounded-full border transition-colors',
                rule.met
                  ? 'bg-emerald-100 border-emerald-300 text-emerald-600'
                  : 'bg-slate-100 border-slate-300 text-slate-400'
              )}
            >
              {rule.met ? <Check className="w-2.5 h-2.5 stroke-[3]" /> : <X className="w-2.5 h-2.5 stroke-[2.5]" />}
            </span>
            <span>{rule.label}</span>
          </li>
        ))}
      </ul>
    </div>
  );
};
