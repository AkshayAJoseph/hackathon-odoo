import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '@/auth';
import { Shield, ArrowRight, Lock, Mail, Loader2, AlertCircle } from 'lucide-react';

export const LoginPage: React.FC = () => {
  const [email, setEmail] = useState('admin@brightloop.io');
  const [password, setPassword] = useState('Password123!');
  const [error, setError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const { login, isMockMode } = useAuth();
  const navigate = useNavigate();

  const handleRoleRedirect = (role?: string) => {
    switch (role) {
      case 'admin':
        navigate('/admin/products');
        break;
      case 'staff':
        navigate('/staff/subscriptions');
        break;
      case 'customer':
      default:
        navigate('/portal/subscriptions');
        break;
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    const trimmedEmail = email.trim();
    if (!trimmedEmail) {
      setError('Please enter your email address.');
      return;
    }
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(trimmedEmail)) {
      setError('Please enter a valid email address.');
      return;
    }
    if (!password) {
      setError('Please enter your password.');
      return;
    }

    setIsSubmitting(true);
    try {
      const user = await login(trimmedEmail, password);
      handleRoleRedirect(user?.role);
    } catch (err: any) {
      const errorMsg =
        err?.data?.detail ||
        err?.data?.non_field_errors?.[0] ||
        err?.data?.email?.[0] ||
        err?.data?.password?.[0] ||
        err?.data?.message ||
        err?.message ||
        'Invalid email or password. Please try again.';
      setError(errorMsg);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleQuickFill = async (presetEmail: string) => {
    setEmail(presetEmail);
    setPassword('Password123!');
    setError('');
    setIsSubmitting(true);
    try {
      const user = await login(presetEmail, 'Password123!');
      handleRoleRedirect(user?.role);
    } catch (err: any) {
      setError(err?.data?.detail || 'Quick mock sign in failed.');
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
          Brightloop ERP
        </h2>
        <p className="mt-2 text-center text-sm text-slate-600">
          Sign in to your subscription management console
        </p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-white py-8 px-6 shadow-md rounded-xl sm:px-10 border border-slate-200">
          {error && (
            <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-700 flex items-start gap-2">
              <AlertCircle className="w-4 h-4 text-red-500 mt-0.5 shrink-0" />
              <span>{error}</span>
            </div>
          )}

          <form className="space-y-5" onSubmit={handleSubmit}>
            <div>
              <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wide">
                Email Address
              </label>
              <div className="mt-1 relative rounded-md shadow-xs">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-400">
                  <Mail className="h-4 w-4" />
                </div>
                <input
                  type="email"
                  required
                  disabled={isSubmitting}
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="block w-full pl-9 pr-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-hidden focus:ring-2 focus:ring-indigo-600 focus:border-indigo-600 disabled:bg-slate-50 disabled:text-slate-500"
                  placeholder="you@company.com"
                />
              </div>
            </div>

            <div>
              <div className="flex items-center justify-between">
                <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wide">
                  Password
                </label>
                <Link to="/forgot" className="text-xs text-indigo-600 hover:text-indigo-500 font-medium">
                  Forgot password?
                </Link>
              </div>
              <div className="mt-1 relative rounded-md shadow-xs">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-400">
                  <Lock className="h-4 w-4" />
                </div>
                <input
                  type="password"
                  required
                  disabled={isSubmitting}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="block w-full pl-9 pr-3 py-2 border border-slate-300 rounded-lg text-sm focus:outline-hidden focus:ring-2 focus:ring-indigo-600 focus:border-indigo-600 disabled:bg-slate-50 disabled:text-slate-500"
                  placeholder="•••••••••"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={isSubmitting}
              className="w-full flex justify-center items-center gap-2 py-2.5 px-4 border border-transparent rounded-lg shadow-sm text-sm font-semibold text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-hidden focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-colors disabled:opacity-70 disabled:cursor-not-allowed"
            >
              {isSubmitting ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Signing in...</span>
                </>
              ) : (
                <>
                  <span>Sign in</span>
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>
          </form>

          {/* Quick Mock Login shortcuts for testing Hour 1 */}
          {isMockMode && (
            <div className="mt-6 pt-5 border-t border-slate-200">
              <p className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-2.5 text-center flex items-center justify-center gap-1">
                <Shield className="w-3.5 h-3.5 text-indigo-500" />
                Quick Mock Login by Role
              </p>
              <div className="grid grid-cols-3 gap-2">
                <button
                  type="button"
                  disabled={isSubmitting}
                  onClick={() => handleQuickFill('admin@brightloop.io')}
                  className="px-2 py-1.5 text-xs font-medium rounded-md bg-indigo-50 text-indigo-700 hover:bg-indigo-100 border border-indigo-200 text-center transition-colors disabled:opacity-50"
                >
                  Admin
                </button>
                <button
                  type="button"
                  disabled={isSubmitting}
                  onClick={() => handleQuickFill('staff@brightloop.io')}
                  className="px-2 py-1.5 text-xs font-medium rounded-md bg-emerald-50 text-emerald-700 hover:bg-emerald-100 border border-emerald-200 text-center transition-colors disabled:opacity-50"
                >
                  Staff
                </button>
                <button
                  type="button"
                  disabled={isSubmitting}
                  onClick={() => handleQuickFill('customer@acme.com')}
                  className="px-2 py-1.5 text-xs font-medium rounded-md bg-blue-50 text-blue-700 hover:bg-blue-100 border border-blue-200 text-center transition-colors disabled:opacity-50"
                >
                  Customer
                </button>
              </div>
            </div>
          )}

          <div className="mt-6 text-center text-xs text-slate-500">
            Don&apos;t have an account?{' '}
            <Link to="/signup" className="text-indigo-600 font-semibold hover:underline">
              Register now
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};
