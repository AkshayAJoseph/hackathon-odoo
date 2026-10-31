import { apiClient } from '@/api/client';
import type { Plan } from '@/api/mockData';

export const listPlans = async (): Promise<Plan[]> => {
  const resp = await apiClient.get<any>('/plans');
  const items = resp.results || resp || [];
  return Array.isArray(items) ? items : [];
};

export const createPlan = async (payload: Partial<Plan>): Promise<Plan> => {
  return apiClient.post<Plan>('/plans/', payload);
};

export const listQuotationTemplates = async (): Promise<any[]> => {
  const resp = await apiClient.get<any>('/quotation-templates');
  const items = resp.results || resp || [];
  return Array.isArray(items) ? items : [];
};

export const createSubscriptionFromTemplate = async (templateId: number, customerId: number): Promise<any> => {
  return apiClient.post<any>(`/quotation-templates/${templateId}/create-subscription`, {
    customer: customerId,
  });
};
