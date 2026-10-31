import { apiClient } from '@/api/client';
import type { Subscription } from '@/api/mockData';

export interface PaginatedSubscriptionsResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: any[];
}

export const normalizeSubscription = (raw: any): Subscription => ({
  id: raw.id,
  subscription_number: raw.number || raw.subscription_number || `SUB-${raw.id}`,
  customer_id: raw.customer || raw.customer_id || 1,
  customer_name: raw.customer_name || `Customer #${raw.customer || raw.customer_id}`,
  customer_email: raw.customer_email || 'customer@brightloop.test',
  plan_id: raw.plan || raw.plan_id || 1,
  plan_name: raw.plan_name || `Plan #${raw.plan || raw.plan_id}`,
  status: raw.status || 'draft',
  current_period_start: raw.start_date || raw.current_period_start || 'N/A',
  current_period_end: raw.expiry_date || raw.next_billing_date || raw.current_period_end || 'Open',
  total_amount: raw.total_amount || '0.00',
  allowed_actions: raw.allowed_actions || [],
  lines: (raw.lines || []).map((l: any) => ({
    id: l.id,
    product_name: l.product_name || `Product #${l.product}`,
    variant_name: l.variant_name || undefined,
    quantity: l.quantity,
    unit_price: l.unit_price,
    tax_rate: l.tax_rate || 0,
    line_total: l.line_total,
  })),
});

/** List subscriptions from live backend (with mock fallback) */
export const listSubscriptions = async (): Promise<Subscription[]> => {
  const resp = await apiClient.get<any>('/subscriptions');
  const items = resp.results || resp || [];
  return Array.isArray(items) ? items.map(normalizeSubscription) : [];
};

/** Get a single subscription by ID */
export const getSubscription = async (id: number): Promise<Subscription> => {
  const resp = await apiClient.get<any>(`/subscriptions/${id}`);
  return normalizeSubscription(resp);
};

/** FSM Action triggers */
export const sendQuote = async (id: number): Promise<Subscription> => {
  const resp = await apiClient.post<any>(`/subscriptions/${id}/send-quote`);
  return normalizeSubscription(resp);
};

export const confirmSubscription = async (id: number): Promise<Subscription> => {
  const resp = await apiClient.post<any>(`/subscriptions/${id}/confirm`);
  return normalizeSubscription(resp);
};

export const activateSubscription = async (id: number): Promise<Subscription> => {
  const resp = await apiClient.post<any>(`/subscriptions/${id}/activate`);
  return normalizeSubscription(resp);
};

export const pauseSubscription = async (id: number): Promise<Subscription> => {
  const resp = await apiClient.post<any>(`/subscriptions/${id}/pause`);
  return normalizeSubscription(resp);
};

export const resumeSubscription = async (id: number): Promise<Subscription> => {
  const resp = await apiClient.post<any>(`/subscriptions/${id}/resume`);
  return normalizeSubscription(resp);
};

export const renewSubscription = async (id: number): Promise<Subscription> => {
  const resp = await apiClient.post<any>(`/subscriptions/${id}/renew`);
  return normalizeSubscription(resp);
};

export const closeSubscription = async (id: number): Promise<Subscription> => {
  const resp = await apiClient.post<any>(`/subscriptions/${id}/close`);
  return normalizeSubscription(resp);
};
