import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth, UserRole } from '@/auth';

interface ProtectedRouteProps {
  roles?: UserRole[];
  children: React.ReactNode;
}

export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ roles, children }) => {
  const { isAuthenticated, role, isLoading } = useAuth();
  const location = useLocation();

  if (isLoading) {
    return (
      <div className="flex h-screen w-full items-center justify-center bg-slate-50">
        <div className="flex flex-col items-center gap-3">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-indigo-600 border-t-transparent" />
          <p className="text-sm text-slate-500 font-medium">Verifying access...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated || !role) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  if (roles && !roles.includes(role)) {
    // Redirect unauthorized roles to their allowed default home screen
    if (role === 'admin') return <Navigate to="/admin/products" replace />;
    if (role === 'staff') return <Navigate to="/staff/subscriptions" replace />;
    if (role === 'customer') return <Navigate to="/portal/subscriptions" replace />;
    return <Navigate to="/" replace />;
  }

  return <>{children}</>;
};
