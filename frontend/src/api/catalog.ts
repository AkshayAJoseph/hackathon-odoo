// Frontend API utilities for catalog (products & variants)

import { apiClient } from '@/api/client';
import type { Product, ProductVariant } from '@/api/mockData';
import { addMockProduct, addMockVariant } from '@/api/mockData';

/** Paginated response shape used by the mock client */
export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

/** Fetch all products (mock or real) */
export const listProducts = async (): Promise<Product[]> => {
  const resp = await apiClient.get<PaginatedResponse<Product>>('/products');
  return resp.results;
};

/** Create a new product. In mock mode we use the helper to keep the in‑memory store in sync. */
export const createProduct = async (
  payload: Omit<Product, 'id' | 'variants'>
): Promise<Product> => {
  if (apiClient.getIsMockMode?.()) {
    // The mock helper returns the full product with an assigned id.
    return addMockProduct(payload) as Product;
  }
  // Real backend endpoint (assumed) – POST /products/
  return apiClient.post<Product>('/products/', payload);
};

/** Add a variant to an existing product. */
export const addVariant = async (
  productId: number,
  payload: Omit<ProductVariant, 'id' | 'product_id'>
): Promise<ProductVariant> => {
  if (apiClient.getIsMockMode?.()) {
    return addMockVariant(productId, payload) as ProductVariant;
  }
  // Real backend endpoint (assumed) – POST /products/{id}/variants/
  return apiClient.post<ProductVariant>(`/products/${productId}/variants/`, payload);
};
