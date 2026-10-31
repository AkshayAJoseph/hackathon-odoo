import React, { useEffect, useState } from 'react';
import { FileText, Plus, ArrowRight, Loader2 } from 'lucide-react';
import { Link } from 'react-router-dom';
import { listQuotationTemplates } from '@/api/plans';

interface TemplateItem {
  id: number;
  name: string;
  plan_name?: string;
  validity_days: number;
  lines_count?: number;
  lines?: any[];
  base_value?: string;
}

const DEFAULT_TEMPLATES: TemplateItem[] = [
  {
    id: 1,
    name: 'Standard Cloud SaaS Bundle',
    plan_name: 'Pro Monthly',
    validity_days: 30,
    lines_count: 2,
    base_value: '1059.00',
  },
  {
    id: 2,
    name: 'Enterprise ERP + Odoo Suite',
    plan_name: 'Enterprise Annual',
    validity_days: 45,
    lines_count: 3,
    base_value: '2550.00',
  },
];

export const TemplatesPage: React.FC = () => {
  const [templates, setTemplates] = useState<TemplateItem[]>(DEFAULT_TEMPLATES);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    let mounted = true;
    listQuotationTemplates()
      .then((data) => {
        if (mounted && data && data.length > 0) {
          const mapped = data.map((t: any) => ({
            id: t.id,
            name: t.name,
            plan_name: t.plan?.name || t.plan_name || `Plan #${t.plan}`,
            validity_days: t.validity_days,
            lines_count: t.lines?.length || 0,
            base_value: t.base_value || '1000.00',
          }));
          setTemplates(mapped);
        }
      })
      .catch((err) => {
        console.warn('Failed to load quotation templates, using default', err);
      })
      .finally(() => {
        if (mounted) setLoading(false);
      });
    return () => {
      mounted = false;
    };
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Quotation Templates</h1>
          <p className="text-xs text-slate-500 mt-1">
            Preset quote configurations for rapid subscription provisioning.
          </p>
        </div>
        <button className="inline-flex items-center gap-1.5 px-3 py-2 bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-semibold rounded-lg shadow-sm">
          <Plus className="w-4 h-4" />
          <span>New Template</span>
        </button>
      </div>

      {loading && templates.length === 0 ? (
        <div className="flex items-center justify-center p-12 text-slate-400">
          <Loader2 className="w-6 h-6 animate-spin mr-2 text-indigo-600" />
          <span className="text-sm">Loading templates...</span>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {templates.map((tpl) => (
            <div key={tpl.id} className="bg-white rounded-xl border border-slate-200 p-6 shadow-xs space-y-4">
              <div className="flex items-start justify-between">
                <div>
                  <div className="flex items-center gap-2">
                    <FileText className="w-5 h-5 text-indigo-600" />
                    <h2 className="font-bold text-slate-900 text-base">{tpl.name}</h2>
                  </div>
                  <p className="text-xs text-slate-500 mt-1">Preset Plan: {tpl.plan_name}</p>
                </div>
                <span className="text-base font-bold text-slate-900 font-mono">${tpl.base_value}</span>
              </div>

              <div className="text-xs text-slate-500 flex justify-between py-2 border-y border-slate-100">
                <span>Validity: {tpl.validity_days} Days</span>
                <span>Included Items: {tpl.lines_count ?? tpl.lines?.length ?? 0} lines</span>
              </div>

              <div className="pt-1 flex justify-end">
                <Link
                  to="/staff/subscriptions"
                  className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-indigo-50 hover:bg-indigo-100 text-indigo-700 font-semibold text-xs rounded-lg transition"
                >
                  <span>Create Subscription from Template</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </Link>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
