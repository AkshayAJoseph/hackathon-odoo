import React from 'react';
import { Outlet, useNavigate } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { useAuth, UserRole } from '@/auth';
import { LogOut, UserCircle2, Sparkles } from 'lucide-react';

export const Shell: React.FC = () => {
  const { user, role, logout, setMockRole, isMockMode } = useAuth();
  const navigate = useNavigate();

  const handleRoleSwitch = (newRole: UserRole) => {
    setMockRole(newRole);
    if (newRole === 'admin') navigate('/admin/products');
    else if (newRole === 'staff') navigate('/staff/subscriptions');
    else if (newRole === 'customer') navigate('/portal/subscriptions');
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className="flex h-screen w-full bg-slate-100 overflow-hidden">
      {/* Sidebar navigation */}
      <Sidebar />

      {/* Main content wrapper */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        {/* Top Navbar */}
        <header className="h-16 bg-white border-b border-slate-200 px-6 flex items-center justify-between shrink-0 shadow-xs">
          <div className="flex items-center gap-3">
            {isMockMode && (
              <div className="flex items-center gap-2 bg-indigo-50 border border-indigo-200 px-3 py-1.5 rounded-lg text-xs">
                <span className="flex items-center gap-1 font-semibold text-indigo-900">
                  <Sparkles className="w-3.5 h-3.5 text-indigo-600" />
                  Mock Role Switcher:
                </span>
                <div className="flex items-center gap-1">
                  {(['admin', 'staff', 'customer'] as UserRole[]).map((r) => (
                    <button
                      key={r}
                      onClick={() => handleRoleSwitch(r)}
                      className={`px-2.5 py-1 rounded text-xs font-medium transition-all ${
                        role === r
                          ? 'bg-indigo-600 text-white shadow-xs'
                          : 'bg-white text-slate-700 hover:bg-slate-100 border border-slate-200'
                      }`}
                    >
                      {r.charAt(0).toUpperCase() + r.slice(1)}
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* User profile and logout */}
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2.5 text-right">
              <div>
                <p className="text-sm font-semibold text-slate-900 leading-tight">
                  {user?.name || 'Authorized User'}
                </p>
                <p className="text-xs text-slate-500 font-mono">
                  {user?.email || 'user@brightloop.io'}
                </p>
              </div>
              <div className="w-9 h-9 rounded-full bg-slate-200 flex items-center justify-center text-slate-600 font-semibold border border-slate-300">
                <UserCircle2 className="w-6 h-6" />
              </div>
            </div>

            <div className="h-6 w-px bg-slate-200" />

            <button
              onClick={handleLogout}
              title="Sign Out"
              className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-slate-600 hover:text-rose-600 hover:bg-rose-50 rounded-md transition-colors"
            >
              <LogOut className="w-4 h-4" />
              <span>Logout</span>
            </button>
          </div>
        </header>

        {/* Page Content Viewport */}
        <main className="flex-1 overflow-y-auto p-6">
          <div className="max-w-7xl mx-auto">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  );
};
