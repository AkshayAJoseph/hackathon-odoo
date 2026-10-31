import React, { useState, useEffect } from 'react';
import { MOCK_USERS, apiClient } from '@/api';
import { ShieldCheck, UserPlus, Mail, Loader2 } from 'lucide-react';

interface StaffUser {
  id: number;
  name: string;
  email: string;
  role: 'staff' | 'admin' | 'customer';
  company?: string;
}

export const AdminStaffPage: React.FC = () => {
  const [showAddModal, setShowAddModal] = useState(false);
  const [staffName, setStaffName] = useState('');
  const [staffEmail, setStaffEmail] = useState('');
  const [staffPassword, setStaffPassword] = useState('StaffPass123!');
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [staffList, setStaffList] = useState<StaffUser[]>([
    MOCK_USERS.staff,
    { id: 4, name: 'Alex River', email: 'alex.staff@brightloop.io', role: 'staff', company: 'Operations' },
  ]);

  const fetchStaff = async () => {
    try {
      setLoading(true);
      const res = await apiClient.get<any>('/staff/');
      const list = res.results || res || [];
      if (Array.isArray(list) && list.length > 0) {
        setStaffList(list.map((u: any) => ({
          id: u.id,
          name: u.name || u.email.split('@')[0],
          email: u.email,
          role: u.role,
          company: 'Operations',
        })));
      }
    } catch (err) {
      console.warn('Could not load live staff directory, using default', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStaff();
  }, []);

  const handleCreateStaff = async () => {
    if (!staffEmail) return;
    setSubmitting(true);
    setError(null);
    try {
      await apiClient.post('/staff/', {
        name: staffName,
        email: staffEmail,
        password: staffPassword,
      });
      setShowAddModal(false);
      setStaffName('');
      setStaffEmail('');
      await fetchStaff();
    } catch (err: any) {
      setError(err?.message || 'Failed to create staff user');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Staff Management</h1>
          <p className="text-xs text-slate-500 mt-1">
            Admin privilege: Create and manage internal staff team members.
          </p>
        </div>
        <button
          onClick={() => setShowAddModal(true)}
          className="inline-flex items-center gap-1.5 px-3 py-2 bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-semibold rounded-lg shadow-sm"
        >
          <UserPlus className="w-4 h-4" />
          <span>Add Staff Member</span>
        </button>
      </div>

      <div className="bg-white rounded-xl border border-slate-200 overflow-hidden shadow-xs">
        <div className="p-4 bg-slate-50 border-b border-slate-200 flex justify-between items-center">
          <span className="text-xs font-semibold uppercase tracking-wider text-slate-700">Internal Staff Directory</span>
          {loading && <Loader2 className="w-4 h-4 animate-spin text-indigo-600" />}
        </div>
        <div className="divide-y divide-slate-200">
          {staffList.map((member) => (
            <div key={member.id} className="p-4 flex items-center justify-between hover:bg-slate-50">
              <div className="flex items-center gap-3">
                <div className="w-9 h-9 rounded-full bg-emerald-100 text-emerald-700 flex items-center justify-center font-bold text-sm">
                  {member.name.charAt(0).toUpperCase()}
                </div>
                <div>
                  <h2 className="text-sm font-semibold text-slate-900">{member.name}</h2>
                  <p className="text-xs text-slate-500 font-mono flex items-center gap-1">
                    <Mail className="w-3 h-3 text-slate-400" />
                    {member.email}
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-emerald-50 text-emerald-700 border border-emerald-200">
                  <ShieldCheck className="w-3 h-3 mr-1" />
                  {member.role === 'admin' ? 'Admin' : 'Staff'}
                </span>
                <span className="text-xs text-slate-400">{member.company || 'Operations'}</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {showAddModal && (
        <div className="fixed inset-0 bg-slate-900/40 backdrop-blur-xs flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-xl shadow-xl max-w-md w-full p-6 space-y-4 border border-slate-200">
            <h2 className="text-base font-bold text-slate-900">Provision Staff Account</h2>
            {error && (
              <div className="p-3 bg-rose-50 border border-rose-200 text-rose-700 text-xs rounded-lg">
                {error}
              </div>
            )}
            <div className="space-y-3 text-xs">
              <div>
                <label className="block font-semibold text-slate-700 mb-1">Full Name</label>
                <input
                  type="text"
                  value={staffName}
                  onChange={(e) => setStaffName(e.target.value)}
                  placeholder="Staff Name"
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg text-xs"
                />
              </div>
              <div>
                <label className="block font-semibold text-slate-700 mb-1">Corporate Email</label>
                <input
                  type="email"
                  value={staffEmail}
                  onChange={(e) => setStaffEmail(e.target.value)}
                  placeholder="staff@brightloop.io"
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg text-xs"
                />
              </div>
              <div>
                <label className="block font-semibold text-slate-700 mb-1">Initial Password</label>
                <input
                  type="password"
                  value={staffPassword}
                  onChange={(e) => setStaffPassword(e.target.value)}
                  placeholder="Initial Password"
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg text-xs font-mono"
                />
              </div>
            </div>
            <div className="flex justify-end gap-2 pt-2">
              <button
                type="button"
                onClick={() => setShowAddModal(false)}
                className="px-3 py-1.5 text-xs text-slate-600 hover:bg-slate-100 rounded-lg"
              >
                Cancel
              </button>
              <button
                type="button"
                disabled={submitting}
                onClick={handleCreateStaff}
                className="px-3 py-1.5 text-xs bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg font-semibold inline-flex items-center gap-1.5"
              >
                {submitting && <Loader2 className="w-3.5 h-3.5 animate-spin" />}
                <span>Create Staff</span>
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
