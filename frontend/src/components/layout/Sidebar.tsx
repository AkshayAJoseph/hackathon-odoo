import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  Package,
  CalendarCheck,
  Percent,
  Receipt,
  Users,
  FileSpreadsheet,
  FileText,
  CreditCard,
  PlayCircle,
  Component,
  ShieldCheck,
  Briefcase,
  UserCheck,
} from 'lucide-react';
import { useAuth } from '@/auth';
import { cn } from '@/lib/utils';

interface NavItem {
  name: string;
  to: string;
  icon: React.ComponentType<{ className?: string }>;
}

export const Sidebar: React.FC = () => {
  const { role } = useAuth();

  // Role-specific navigation menus strictly enforcing role segregation
  let navItems: { section?: string; items: NavItem[] }[] = [];

  if (role === 'admin') {
    navItems = [
      {
        section: 'Overview',
        items: [
          { name: 'Dashboard', to: '/dashboard', icon: LayoutDashboard },
        ],
      },
      {
        section: 'Administration',
        items: [
          { name: 'Products & Variants', to: '/admin/products', icon: Package },
          { name: 'Subscription Plans', to: '/admin/plans', icon: CalendarCheck },
          { name: 'Tax Rates', to: '/admin/taxes', icon: Receipt },
          { name: 'Discounts', to: '/admin/discounts', icon: Percent },
          { name: 'Staff Management', to: '/admin/staff', icon: ShieldCheck },
        ],
      },
      {
        section: 'Operations & Billing',
        items: [
          { name: 'Subscriptions', to: '/staff/subscriptions', icon: FileSpreadsheet },
          { name: 'Invoices', to: '/staff/invoices', icon: CreditCard },
          { name: 'Customers', to: '/staff/customers', icon: Users },
          { name: 'Quotation Templates', to: '/staff/templates', icon: FileText },
          { name: 'Run Billing Engine', to: '/staff/billing', icon: PlayCircle },
        ],
      },
      {
        section: 'Developer Tools',
        items: [
          { name: 'Component Showcase', to: '/dev/components', icon: Component },
        ],
      },
    ];
  } else if (role === 'staff') {
    navItems = [
      {
        section: 'Operations',
        items: [
          { name: 'Dashboard', to: '/dashboard', icon: LayoutDashboard },
          { name: 'Subscriptions', to: '/staff/subscriptions', icon: FileSpreadsheet },
          { name: 'Invoices', to: '/staff/invoices', icon: CreditCard },
          { name: 'Payments', to: '/staff/payments', icon: CreditCard },
          { name: 'Customers', to: '/staff/customers', icon: Users },
          { name: 'Quotation Templates', to: '/staff/templates', icon: FileText },
          { name: 'Run Billing Engine', to: '/staff/billing', icon: PlayCircle },
        ],
      },
      {
        section: 'Developer Tools',
        items: [
          { name: 'Component Showcase', to: '/dev/components', icon: Component },
        ],
      },
    ];
  } else if (role === 'customer') {
    // Customer Portal: strictly portal items only
    navItems = [
      {
        section: 'Customer Portal',
        items: [
          { name: 'My Subscriptions', to: '/portal/subscriptions', icon: FileSpreadsheet },
          { name: 'My Invoices', to: '/portal/invoices', icon: CreditCard },
        ],
      },
    ];
  }

  const roleBadgeIcon = () => {
    if (role === 'admin') return <ShieldCheck className="w-3.5 h-3.5 text-indigo-400 mr-1" />;
    if (role === 'staff') return <Briefcase className="w-3.5 h-3.5 text-emerald-400 mr-1" />;
    return <UserCheck className="w-3.5 h-3.5 text-blue-400 mr-1" />;
  };

  return (
    <aside className="w-64 bg-slate-900 text-slate-200 flex flex-col shrink-0 border-r border-slate-800">
      {/* Brand Header */}
      <div className="h-16 flex items-center px-6 border-b border-slate-800">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-indigo-600 flex items-center justify-center font-bold text-white shadow-md">
            BL
          </div>
          <div>
            <h1 className="font-bold text-white text-base tracking-tight leading-none">Brightloop</h1>
            <p className="text-[11px] text-slate-400 mt-1 font-mono">Subscription ERP</p>
          </div>
        </div>
      </div>

      {/* Role Indicator Banner */}
      <div className="px-6 py-2.5 bg-slate-950/60 border-b border-slate-800/80 flex items-center justify-between text-xs">
        <span className="text-slate-400 font-medium">Active Workspace</span>
        <span className="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-semibold bg-slate-800 text-slate-200 uppercase tracking-wide">
          {roleBadgeIcon()}
          {role}
        </span>
      </div>

      {/* Navigation Sections */}
      <nav className="flex-1 overflow-y-auto px-4 py-4 space-y-6">
        {navItems.map((group, gIdx) => (
          <div key={gIdx} className="space-y-1">
            {group.section && (
              <h2 className="px-3 text-[11px] font-semibold uppercase tracking-wider text-slate-400 mb-2">
                {group.section}
              </h2>
            )}
            {group.items.map((item) => {
              const Icon = item.icon;
              return (
                <NavLink
                  key={item.to}
                  to={item.to}
                  className={({ isActive }) =>
                    cn(
                      'flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium transition-colors duration-150',
                      isActive
                        ? 'bg-indigo-600 text-white font-semibold shadow-sm'
                        : 'text-slate-300 hover:bg-slate-800/70 hover:text-white'
                    )
                  }
                >
                  <Icon className="w-4 h-4 shrink-0" />
                  <span>{item.name}</span>
                </NavLink>
              );
            })}
          </div>
        ))}
      </nav>

      {/* Footer System Status */}
      <div className="p-4 border-t border-slate-800 text-xs text-slate-400 flex items-center justify-between">
        <span className="flex items-center gap-1.5">
          <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
          <span>Vite + React TS</span>
        </span>
        <span className="text-[10px] bg-slate-800 px-1.5 py-0.5 rounded text-slate-400 font-mono">H1-Ready</span>
      </div>
    </aside>
  );
};
