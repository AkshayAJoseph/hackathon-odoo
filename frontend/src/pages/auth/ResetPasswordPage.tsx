import React, { useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { apiClient } from '@/api';
import { PasswordHints, evaluatePassword } from '@/components';
import { ArrowRight, Lock, CheckCircle2, AlertCircle, Loader2, RefreshCw } from 'lucide-react';

export const ResetPasswordPage: React.FC = () => {
  const { uid, token } = useParams<{ uid: string; token: string }>();
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const navigate = useNavigate();

  const isTokenMissing = !uid || !token;

  // Evaluate password rules including confirmation match
  const { isValid: isPasswordValid } = evaluatePassword(password, confirmPassword);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (isTokenMissing) {
      setError('Cannot reset password: Token or User ID is missing from URL.');
      return;
    }

    if (!isPasswordValid) {
      if (password !== confirmPassword) {
        setError('Passwords do not match.');
      } else {
        setError('Please satisfy all password requirements before proceeding.');
      }
      return;
    }

    setError('');
    setIsSubmitting(true);
    try {
      // Connect to backend reset-password endpoint
      await apiClient.post('/auth/reset/', {
        uid,
        token,
        new_password: password,
        password,
      });

      setSuccess(true);
      setTimeout(() => {
        navigate('/login');
      }, 2000);
    } catch (err: any) {
      const errorMsg =
        err?.data?.detail ||
        err?.data?.token?.[0] ||
        err?.data?.new_password?.[0] ||
        err?.data?.password?.[0] ||
        err?.data?.non_field_errors?.[0] ||
        err?.message ||
        'This password reset link is invalid or has expired (links are single-use and expire after 30 minutes).';
      setError(errorMsg);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-100 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <div className="flex justify-center">
          <div className="w-12 h-12 rounded-xl bg-indigo-600 flex items-center justify-center text-white font-bold text-xl shadow-lg">
            BL
          </div>
        </div>
        <h2 className="mt-4 text-center text-3xl font-extrabold text-slate-900 tracking-tight">
          Reset Your Password
        </h2>
        {token && uid ? (
          <p className="mt-2 text-center text-xs text-slate-500 font-mono">
            Token: {token.length > 12 ? `${token.substring(0, 10)}...` : token} | UID: {uid}
          </p>
        ) : (
          <p className="mt-2 text-center text-xs text-rose-500 font-medium">
            Reset token missing or malformed
          </p>
        )}
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-white py-8 px-6 shadow-md rounded-xl sm:px-10 border border-slate-200">
          {success ? (
            <div className="text-center space-y-4">
              <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-emerald-100 text-emerald-600">
                <CheckCircle2 className="h-6 w-6" />
              </div>
              <h3 className="text-base font-semibold text-slate-900">Password Reset Successful</h3>
              <p className="text-sm text-slate-600">
                Your password has been updated securely. Redirecting you to login...
              </p>
              <div className="pt-2">
                <Link
                  to="/login"
                  className="inline-flex items-center text-xs font-semibold text-indigo-600 hover:text-indigo-500 underline"
                >
                  Click here if not redirected automatically
                </Link>
              </div>
            </div>
          ) : (
            <>
              {isTokenMissing && (
                <div className="mb-4 p-3 bg-amber-50 border border-amber-200 rounded-lg text-sm text-amber-800 space-y-2">
                  <div className="flex items-start gap-2">
                    <AlertCircle className="w-4 h-4 text-amber-600 mt-0.5 shrink-0" />
                    <span>This reset link is missing required security tokens.</span>
                  </div>
                  <Link
                    to="/forgot"
                    className="inline-flex items-center text-xs font-semibold text-amber-900 underline"
                  >
                    Request a new password reset link
                  </Link>
                </div>
              )}

              {error && (
                <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-700 space-y-2">
                  <div className="flex items-start gap-2">
                    <AlertCircle className="w-4 h-4 text-red-500 mt-0.5 shrink-0" />
                    <span>{error}</span>
                  </div>
                  {error.toLowerCase().includes('expired') || error.toLowerCase().includes('invalid') ? (
                    <div className="pt-1">
                      <Link
                        to="/forgot"
                        className="inline-flex items-center gap-1 text-xs font-semibold text-red-800 underline"
                      >
                        <RefreshCw className="w-3 h-3" />
                        <span>Request a fresh reset link</span>
                      </Link>
                    </div>
                  ) : null}
                </div>
              )}

              <form className="space-y-4" onSubmit={handleSubmit}>
                <div>
                  <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wide">
                    New Password <span className="text-red-500">*</span>
                  </label>
                  <div className="mt-1 relative rounded-md shadow-xs">
                    <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-400">
                      <Lock className="h-4 w-4" />
                    </div>
                    <input
                      type="password"
                      required
                      disabled={isSubmitting || isTokenMissing}
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      className="block w-full pl-9 pr-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-hidden focus:ring-2 focus:ring-indigo-600 disabled:bg-slate-50 disabled:text-slate-500"
                      placeholder="Min 9 chars, 1 uppercase, 1 lowercase, 1 special"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wide">
                    Confirm New Password <span className="text-red-500">*</span>
                  </label>
                  <div className="mt-1 relative rounded-md shadow-xs">
                    <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-400">
                      <Lock className="h-4 w-4" />
                    </div>
                    <input
                      type="password"
                      required
                      disabled={isSubmitting || isTokenMissing}
                      value={confirmPassword}
                      onChange={(e) => setConfirmPassword(e.target.value)}
                      className="block w-full pl-9 pr-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-hidden focus:ring-2 focus:ring-indigo-600 disabled:bg-slate-50 disabled:text-slate-500"
                      placeholder="Re-enter new password"
                    />
                  </div>
                </div>

                {/* Live Password Hints checklist */}
                <div className="mt-3">
                  <PasswordHints password={password} confirmPassword={confirmPassword} />
                </div>

                <button
                  type="submit"
                  disabled={!isPasswordValid || isSubmitting || isTokenMissing}
                  className={`w-full flex justify-center items-center gap-2 py-2.5 px-4 border border-transparent rounded-lg shadow-sm text-sm font-semibold text-white transition-colors ${
                    isPasswordValid && !isSubmitting && !isTokenMissing
                      ? 'bg-indigo-600 hover:bg-indigo-700 focus:outline-hidden focus:ring-2 focus:ring-indigo-500'
                      : 'bg-slate-300 cursor-not-allowed text-slate-500'
                  }`}
                >
                  {isSubmitting ? (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin" />
                      <span>Updating Password...</span>
                    </>
                  ) : (
                    <>
                      <span>Update Password</span>
                      <ArrowRight className="w-4 h-4" />
                    </>
                  )}
                </button>
              </form>

              <div className="mt-6 text-center text-xs text-slate-500">
                Remembered your credentials?{' '}
                <Link to="/login" className="text-indigo-600 font-semibold hover:underline">
                  Sign in
                </Link>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
};

