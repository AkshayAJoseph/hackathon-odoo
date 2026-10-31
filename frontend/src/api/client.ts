import {
  MOCK_USERS,
  MOCK_PRODUCTS,
  MOCK_PLANS,
  MOCK_TAXES,
  MOCK_DISCOUNTS,
  MOCK_SUBSCRIPTIONS,
  MOCK_INVOICES,
  User,
} from './mockData';

export interface ApiResponse<T = unknown> {
  data: T;
  status: number;
  message?: string;
}

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export interface AuthTokens {
  access: string;
  refresh: string;
}

class ApiClient {
  private baseURL: string;
  private isMockMode: boolean;
  private accessToken: string | null = null;
  private refreshToken: string | null = null;
  private isRefreshing: boolean = false;
  private refreshSubscribers: Array<(token: string) => void> = [];

  constructor() {
    this.baseURL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';
    this.isMockMode = import.meta.env.VITE_MOCK_MODE === 'true';

    // Hydrate tokens from storage
    this.accessToken = localStorage.getItem('bl_access_token');
    this.refreshToken = localStorage.getItem('bl_refresh_token');
  }

  public setTokens(tokens: AuthTokens) {
    this.accessToken = tokens.access;
    this.refreshToken = tokens.refresh;
    localStorage.setItem('bl_access_token', tokens.access);
    localStorage.setItem('bl_refresh_token', tokens.refresh);
  }

  public clearTokens() {
    this.accessToken = null;
    this.refreshToken = null;
    localStorage.removeItem('bl_access_token');
    localStorage.removeItem('bl_refresh_token');
  }

  public getAccessToken(): string | null {
    return this.accessToken;
  }

  public setMockMode(enabled: boolean) {
    this.isMockMode = enabled;
  }

  public getIsMockMode(): boolean {
    return this.isMockMode;
  }

  private onRefreshed(token: string) {
    this.refreshSubscribers.forEach((cb) => cb(token));
    this.refreshSubscribers = [];
  }

  private addRefreshSubscriber(cb: (token: string) => void) {
    this.refreshSubscribers.push(cb);
  }

  private async handleTokenRefresh(): Promise<string | null> {
    if (!this.refreshToken) {
      this.clearTokens();
      return null;
    }

    if (this.isMockMode) {
      const mockNewAccess = 'mock-access-token-refreshed-' + Date.now();
      this.setTokens({ access: mockNewAccess, refresh: this.refreshToken });
      return mockNewAccess;
    }

    try {
      const response = await fetch(`${this.baseURL}/auth/refresh/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh: this.refreshToken }),
      });

      if (!response.ok) {
        throw new Error('Refresh failed');
      }

      const data = await response.json();
      const newAccess = data.access;
      this.setTokens({ access: newAccess, refresh: data.refresh || this.refreshToken });
      return newAccess;
    } catch {
      this.clearTokens();
      return null;
    }
  }

  public async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    // Normalise endpoint
    const cleanEndpoint = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;

    // Handle Mock Mode
    if (this.isMockMode) {
      return this.handleMockRequest<T>(cleanEndpoint, options);
    }

    // Build headers
    const headers = new Headers(options.headers || {});
    if (!headers.has('Content-Type') && !(options.body instanceof FormData)) {
      headers.set('Content-Type', 'application/json');
    }
    if (this.accessToken && !headers.has('Authorization')) {
      headers.set('Authorization', `Bearer ${this.accessToken}`);
    }

    const url = `${this.baseURL}${cleanEndpoint}`;

    let response = await fetch(url, { ...options, headers });

    // Handle 401 Unauthorized - attempt token refresh
    if (response.status === 401 && this.refreshToken && cleanEndpoint !== '/auth/login/' && cleanEndpoint !== '/auth/refresh/') {
      if (!this.isRefreshing) {
        this.isRefreshing = true;
        const newToken = await this.handleTokenRefresh();
        this.isRefreshing = false;

        if (newToken) {
          this.onRefreshed(newToken);
          headers.set('Authorization', `Bearer ${newToken}`);
          response = await fetch(url, { ...options, headers });
        }
      } else {
        // Wait for token refresh in progress
        const retryToken = await new Promise<string>((resolve) => {
          this.addRefreshSubscriber(resolve);
        });
        headers.set('Authorization', `Bearer ${retryToken}`);
        response = await fetch(url, { ...options, headers });
      }
    }

    if (!response.ok) {
      let errorPayload: unknown;
      try {
        errorPayload = await response.json();
      } catch {
        errorPayload = { detail: response.statusText };
      }
      throw {
        status: response.status,
        data: errorPayload,
        message: response.statusText,
      };
    }

    // Handle 204 No Content
    if (response.status === 204) {
      return {} as T;
    }

    return (await response.json()) as T;
  }

  public get<T>(endpoint: string, options?: RequestInit): Promise<T> {
    return this.request<T>(endpoint, { ...options, method: 'GET' });
  }

  public post<T>(endpoint: string, body?: unknown, options?: RequestInit): Promise<T> {
    return this.request<T>(endpoint, {
      ...options,
      method: 'POST',
      body: body ? JSON.stringify(body) : undefined,
    });
  }

  public put<T>(endpoint: string, body?: unknown, options?: RequestInit): Promise<T> {
    return this.request<T>(endpoint, {
      ...options,
      method: 'PUT',
      body: body ? JSON.stringify(body) : undefined,
    });
  }

  public patch<T>(endpoint: string, body?: unknown, options?: RequestInit): Promise<T> {
    return this.request<T>(endpoint, {
      ...options,
      method: 'PATCH',
      body: body ? JSON.stringify(body) : undefined,
    });
  }

  public delete<T>(endpoint: string, options?: RequestInit): Promise<T> {
    return this.request<T>(endpoint, { ...options, method: 'DELETE' });
  }

  // Mock Request Dispatcher
  private async handleMockRequest<T>(endpoint: string, options: RequestInit): Promise<T> {
    // Artificial latency for realistic UI interaction
    await new Promise((r) => setTimeout(r, 60));

    const method = (options.method || 'GET').toUpperCase();

    // /auth/login/
    if (endpoint.includes('/auth/login') && method === 'POST') {
      const body = options.body ? JSON.parse(options.body as string) : {};
      const email = (body.email || '').toLowerCase();
      let role: User['role'] = 'admin';
      if (email.includes('staff')) role = 'staff';
      if (email.includes('customer') || email.includes('client') || email.includes('acme')) role = 'customer';

      const user = MOCK_USERS[role];
      return {
        access: `mock-jwt-access-${role}`,
        refresh: `mock-jwt-refresh-${role}`,
        user,
        role: user.role,
        name: user.name,
      } as T;
    }

    // /auth/signup/
    if (endpoint.includes('/auth/signup') && method === 'POST') {
      const body = options.body ? JSON.parse(options.body as string) : {};
      const newUser: User = {
        id: 99,
        email: body.email || 'newuser@client.com',
        name: body.name || 'New Customer',
        role: 'customer',
        company: body.company,
      };
      return {
        access: 'mock-jwt-access-customer',
        refresh: 'mock-jwt-refresh-customer',
        user: newUser,
        role: 'customer',
        name: newUser.name,
      } as T;
    }

    // /auth/forgot/
    if (endpoint.includes('/auth/forgot') && method === 'POST') {
      return {
        message: 'If the account exists, a link was sent. The link expires in 30 minutes.',
        detail: 'If the account exists, a link was sent. The link expires in 30 minutes.',
      } as T;
    }

    // /auth/reset/
    if (endpoint.includes('/auth/reset') && method === 'POST') {
      const body = options.body ? JSON.parse(options.body as string) : {};
      if (!body.uid || !body.token) {
        throw {
          status: 400,
          data: { detail: 'This password reset link is invalid or has expired (30-min window).' },
          message: 'Bad Request',
        };
      }
      return {
        message: 'Password reset successful.',
        detail: 'Password reset successful.',
      } as T;
    }

    // /auth/me/
    if (endpoint.includes('/auth/me')) {
      const role = localStorage.getItem('bl_mock_role') || 'admin';
      return (MOCK_USERS[role] || MOCK_USERS.admin) as T;
    }

    // /products/
    if (endpoint.includes('/products')) {
      return {
        count: MOCK_PRODUCTS.length,
        next: null,
        previous: null,
        results: MOCK_PRODUCTS,
      } as T;
    }

    // /plans/
    if (endpoint.includes('/plans')) {
      return {
        count: MOCK_PLANS.length,
        next: null,
        previous: null,
        results: MOCK_PLANS,
      } as T;
    }

    // /taxes/
    if (endpoint.includes('/taxes')) {
      return {
        count: MOCK_TAXES.length,
        next: null,
        previous: null,
        results: MOCK_TAXES,
      } as T;
    }

    // /discounts/
    if (endpoint.includes('/discounts')) {
      return {
        count: MOCK_DISCOUNTS.length,
        next: null,
        previous: null,
        results: MOCK_DISCOUNTS,
      } as T;
    }

    // /subscriptions/ or /portal/subscriptions/
    if (endpoint.includes('/subscriptions')) {
      return {
        count: MOCK_SUBSCRIPTIONS.length,
        next: null,
        previous: null,
        results: MOCK_SUBSCRIPTIONS,
      } as T;
    }

    // /invoices/ or /portal/invoices/
    if (endpoint.includes('/invoices')) {
      return {
        count: MOCK_INVOICES.length,
        next: null,
        previous: null,
        results: MOCK_INVOICES,
      } as T;
    }

    // /billing/run/
    if (endpoint.includes('/billing/run') && method === 'POST') {
      return {
        created: 2,
        skipped: 0,
        failed: [],
        timestamp: new Date().toISOString(),
      } as T;
    }

    // Default generic empty response
    return {} as T;
  }
}

export const apiClient = new ApiClient();
