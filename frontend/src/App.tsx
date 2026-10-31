import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider } from '@/auth';
import { ProtectedRoute, Shell } from '@/components';

// Public pages
import { LandingPage } from '@/pages/LandingPage';
import { LoginPage } from '@/pages/auth/LoginPage';
import { SignUpPage } from '@/pages/auth/SignUpPage';
import { ForgotPasswordPage } from '@/pages/auth/ForgotPasswordPage';
import { ResetPasswordPage } from '@/pages/auth/ResetPasswordPage';

// Admin pages
import { AdminProductsPage } from '@/pages/admin/AdminProductsPage';
import { AdminPlansPage } from '@/pages/admin/AdminPlansPage';
import { AdminTaxesPage } from '@/pages/admin/AdminTaxesPage';
import { AdminDiscountsPage } from '@/pages/admin/AdminDiscountsPage';
import { AdminStaffPage } from '@/pages/admin/AdminStaffPage';

// Staff pages
import { SubscriptionsListPage } from '@/pages/staff/SubscriptionsListPage';
import { SubscriptionsDetailPage } from '@/pages/staff/SubscriptionsDetailPage';
import { InvoicesListPage } from '@/pages/staff/InvoicesListPage';
import { CustomersPage } from '@/pages/staff/CustomersPage';
import { TemplatesPage } from '@/pages/staff/TemplatesPage';
import { BillingRunPage } from '@/pages/staff/BillingRunPage';
import { PaymentsListPage } from '@/pages/staff/PaymentsListPage';

// Customer Portal pages
import { CustomerSubscriptionsPage } from '@/pages/portal/CustomerSubscriptionsPage';
import { CustomerInvoicesPage } from '@/pages/portal/CustomerInvoicesPage';

// Shared / Dev pages
import { DashboardPage } from '@/pages/DashboardPage';
import { ComponentShowcasePage } from '@/pages/dev/ComponentShowcasePage';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 60 * 1000,
      retry: 1,
    },
  },
});

export const App: React.FC = () => {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <Routes>
          {/* Public routes */}
          <Route path="/" element={<LandingPage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/signup" element={<SignUpPage />} />
          <Route path="/forgot" element={<ForgotPasswordPage />} />
          <Route path="/reset/:uid/:token" element={<ResetPasswordPage />} />

          {/* Authenticated Application Shell */}
          <Route
            element={
              <ProtectedRoute>
                <Shell />
              </ProtectedRoute>
            }
          >
            {/* Developer visual harness */}
            <Route path="/dev/components" element={<ComponentShowcasePage />} />

            {/* Dashboard (Staff & Admin) */}
            <Route
              path="/dashboard"
              element={
                <ProtectedRoute roles={['admin', 'staff']}>
                  <DashboardPage />
                </ProtectedRoute>
              }
            />

            {/* Admin only routes */}
            <Route
              path="/admin/products"
              element={
                <ProtectedRoute roles={['admin']}>
                  <AdminProductsPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/admin/plans"
              element={
                <ProtectedRoute roles={['admin']}>
                  <AdminPlansPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/admin/taxes"
              element={
                <ProtectedRoute roles={['admin']}>
                  <AdminTaxesPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/admin/discounts"
              element={
                <ProtectedRoute roles={['admin']}>
                  <AdminDiscountsPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/admin/staff"
              element={
                <ProtectedRoute roles={['admin']}>
                  <AdminStaffPage />
                </ProtectedRoute>
              }
            />

            {/* Staff & Admin operational routes */}
            <Route
              path="/staff/subscriptions"
              element={
                <ProtectedRoute roles={['admin', 'staff']}>
                  <SubscriptionsListPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/staff/subscriptions/:id"
              element={
                <ProtectedRoute roles={['admin', 'staff']}>
                  <SubscriptionsDetailPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/staff/invoices"
              element={
                <ProtectedRoute roles={['admin', 'staff']}>
                  <InvoicesListPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/staff/customers"
              element={
                <ProtectedRoute roles={['admin', 'staff']}>
                  <CustomersPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/staff/templates"
              element={
                <ProtectedRoute roles={['admin', 'staff']}>
                  <TemplatesPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/staff/billing"
              element={
                <ProtectedRoute roles={['admin', 'staff']}>
                  <BillingRunPage />
                </ProtectedRoute>
              }
                            />
                <Route
                  path="/staff/payments"
                  element={
                    <ProtectedRoute roles={['admin', 'staff']}>
                      <PaymentsListPage />
                    </ProtectedRoute>
                  }
                />

            {/* Customer Portal routes */}
            <Route
              path="/portal/subscriptions"
              element={
                <ProtectedRoute roles={['customer']}>
                  <CustomerSubscriptionsPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/portal/invoices"
              element={
                <ProtectedRoute roles={['customer']}>
                  <CustomerInvoicesPage />
                </ProtectedRoute>
              }
            />
          </Route>

          {/* Catch-all redirect */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </AuthProvider>
    </QueryClientProvider>
  );
};
