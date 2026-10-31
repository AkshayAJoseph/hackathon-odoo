// API utilities for invoices and invoice actions

import { apiClient } from '@/api/client';
import type { Invoice } from '@/api/mockData';

/** Paginated response for invoices */
export interface InvoicesResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: Invoice[];
}

/** Fetch all invoices (real backend or mock fallback) */
export const listInvoices = async (): Promise<Invoice[]> => {
  const resp = await apiClient.get<InvoicesResponse>('/invoices');
  return resp.results;
};

/** Fetch a single invoice by ID */
export const getInvoice = async (id: number): Promise<Invoice> => {
  return apiClient.get<Invoice>(`/invoices/${id}`);
};

/** Confirm an invoice */
export const confirmInvoice = async (id: number): Promise<void> => {
  await apiClient.post<void>(`/invoices/${id}/confirm/`);
};

/** Cancel an invoice */
export const cancelInvoice = async (id: number): Promise<void> => {
  await apiClient.post<void>(`/invoices/${id}/cancel/`);
};

/** Send (email) an invoice */
export const sendInvoice = async (id: number): Promise<void> => {
  await apiClient.post<void>(`/invoices/${id}/send/`);
};

/** Print an invoice – returns a printable URL or PDF blob (handled by backend) */
export const printInvoice = async (id: number): Promise<void> => {
  // For simplicity we just trigger the endpoint; UI could open a new tab.
  await apiClient.get<void>(`/invoices/${id}/print/`);
};

/** Record a payment on an invoice */
export interface RecordPaymentPayload {
  method: string; // e.g., 'credit_card', 'bank_transfer'
  amount: string; // decimal string
  payment_date?: string; // ISO date optional
  note?: string;
}

export const recordInvoicePayment = async (
  id: number,
  payload: RecordPaymentPayload
): Promise<void> => {
  await apiClient.post<void>(`/invoices/${id}/payments/`, payload);
};
