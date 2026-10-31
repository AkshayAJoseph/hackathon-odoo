// src/api/payments.ts

import { apiClient } from '@/api/client';
import type { Payment } from '@/api/mockData';

export interface PaymentsResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: Payment[];
}

export const listPayments = async (): Promise<Payment[]> => {
  const resp = await apiClient.get<PaymentsResponse>('/payments');
  return resp.results;
};
