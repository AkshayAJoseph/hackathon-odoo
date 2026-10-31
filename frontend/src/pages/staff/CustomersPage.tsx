import React from 'react';
import { MOCK_USERS } from '@/api';
import { Users, Mail, Phone, MapPin, Building } from 'lucide-react';

export const CustomersPage: React.FC = () => {
  const customer = MOCK_USERS.customer;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Customer Accounts</h1>
          <p className="text-xs text-slate-500 mt-1">
            Registered customer clients and subscriber companies.
          </p>
        </div>
      </div>

      <div className="bg-white rounded-xl border border-slate-200 overflow-hidden shadow-xs">
        <div className="p-4 bg-slate-50 border-b border-slate-200">
          <span className="text-xs font-semibold uppercase tracking-wider text-slate-700">Client Directory</span>
        </div>
        <div className="p-5 flex items-center justify-between hover:bg-slate-50 transition">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-xl bg-blue-100 text-blue-700 flex items-center justify-center font-bold text-lg">
              <Building className="w-6 h-6" />
            </div>
            <div className="space-y-1">
              <h2 className="text-base font-bold text-slate-900">{customer.name}</h2>
              <div className="flex flex-wrap gap-4 text-xs text-slate-500">
                <span className="flex items-center gap-1 font-mono">
                  <Mail className="w-3.5 h-3.5 text-slate-400" />
                  {customer.email}
                </span>
                <span className="flex items-center gap-1">
                  <Phone className="w-3.5 h-3.5 text-slate-400" />
                  {customer.phone}
                </span>
                <span className="flex items-center gap-1">
                  <MapPin className="w-3.5 h-3.5 text-slate-400" />
                  {customer.address}
                </span>
              </div>
            </div>
          </div>
          <div>
            <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold bg-blue-50 text-blue-700 border border-blue-200">
              <Users className="w-3.5 h-3.5 mr-1" />
              Customer
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};
