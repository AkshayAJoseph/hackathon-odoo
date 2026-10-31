// Mock fixtures matching Brightloop docs/SPEC.md Section 6 response shapes

export interface User {
  id: number;
  email: string;
  name: string;
  role: 'admin' | 'staff' | 'customer';
  company?: string;
  phone?: string;
  address?: string;
}

export interface ProductVariant {
  id: number;
  product_id: number;
  attribute: string;
  value: string;
  extra_price: string;
}

export interface Product {
  id: number;
  name: string;
  type: 'service' | 'software' | 'addon';
  sales_price: string;
  cost_price: string;
  notes: string;
  is_active: boolean;
  variants: ProductVariant[];
}

export interface Plan {
  id: number;
  name: string;
  price: string;
  billing_period: 'daily' | 'weekly' | 'monthly' | 'yearly';
  min_quantity: number;
  available_from: string;
  available_to: string;
  auto_close: boolean;
  closable: boolean;
  pausable: boolean;
  renewable: boolean;
}

export interface Tax {
  id: number;
  name: string;
  rate_percent: string;
  type: 'percent' | 'fixed';
  is_active: boolean;
  applies_to: number | null;
}

export interface Discount {
  id: number;
  code: string;
  name: string;
  type: 'fixed' | 'percent';
  amount: string;
  min_purchase: string;
  min_quantity: number;
  start_date: string;
  end_date: string;
  usage_limit: number;
  used_count: number;
  scope: 'all' | 'specific_products';
}

export type SubscriptionStatus = 'draft' | 'quotation' | 'confirmed' | 'active' | 'closed';

export interface Subscription {
  id: number;
  subscription_number: string;
  customer_id: number;
  customer_name: string;
  customer_email: string;
  plan_id: number;
  plan_name: string;
  status: SubscriptionStatus;
  current_period_start: string;
  current_period_end: string;
  total_amount: string;
  allowed_actions: string[];
  lines: Array<{
    id: number;
    product_name: string;
    variant_name?: string;
    quantity: number;
    unit_price: string;
    tax_rate: string;
    line_total: string;
  }>;
}

export type InvoiceStatus = 'draft' | 'confirmed' | 'paid' | 'cancelled';

export interface Invoice {
  id: number;
  invoice_number: string;
  subscription_id: number;
  customer_name: string;
  status: InvoiceStatus;
  issue_date: string;
  due_date: string;
  subtotal: string;
  discount_total: string;
  tax_total: string;
  total: string;
  amount_paid: string;
  balance: string;
  is_overdue: boolean;
  days_overdue: number;
  sent_at: string | null;
  lines: Array<{
    id: number;
    description: string;
    quantity: number;
    unit_price: string;
    discount_amount: string;
    tax_amount: string;
    total: string;
  }>;
}

export const MOCK_USERS: Record<string, User> = {
  admin: {
    id: 1,
    email: 'admin@brightloop.io',
    name: 'Administrator',
    role: 'admin',
    company: 'Brightloop HQ',
  },
  staff: {
    id: 2,
    email: 'staff@brightloop.io',
    name: 'Sarah Connor',
    role: 'staff',
    company: 'Brightloop Operations',
  },
  customer: {
    id: 3,
    email: 'acme@client.com',
    name: 'Acme Corporation',
    role: 'customer',
    company: 'Acme Corp',
    phone: '+1-555-0199',
    address: '123 Innovation Way, Suite 400',
  },
};

export const MOCK_PRODUCTS: Product[] = [
  {
    id: 1,
    name: 'Brightloop Enterprise Cloud',
    type: 'software',
    sales_price: '499.00',
    cost_price: '150.00',
    notes: 'Primary subscription management license',
    is_active: true,
    variants: [
      { id: 101, product_id: 1, attribute: 'Brand', value: 'Odoo Integration', extra_price: '560.00' },
      { id: 102, product_id: 1, attribute: 'Storage', value: '1TB Extra', extra_price: '100.00' },
    ],
  },
  {
    id: 2,
    name: 'Dedicated Support Tier',
    type: 'service',
    sales_price: '250.00',
    cost_price: '80.00',
    notes: '24/7 dedicated engineering SLA support',
    is_active: true,
    variants: [],
  },
];

export const MOCK_PLANS: Plan[] = [
  {
    id: 1,
    name: 'Pro Monthly',
    price: '199.00',
    billing_period: 'monthly',
    min_quantity: 1,
    available_from: '2026-01-01',
    available_to: '2027-12-31',
    auto_close: false,
    closable: true,
    pausable: true,
    renewable: true,
  },
  {
    id: 2,
    name: 'Enterprise Annual',
    price: '1990.00',
    billing_period: 'yearly',
    min_quantity: 1,
    available_from: '2026-01-01',
    available_to: '2027-12-31',
    auto_close: true,
    closable: true,
    pausable: false,
    renewable: true,
  },
];

export const MOCK_TAXES: Tax[] = [
  { id: 1, name: 'Standard GST / VAT', rate_percent: '18.00', type: 'percent', is_active: true, applies_to: null },
  { id: 2, name: 'Digital Services Tax', rate_percent: '5.00', type: 'percent', is_active: true, applies_to: null },
];

export const MOCK_DISCOUNTS: Discount[] = [
  {
    id: 1,
    code: 'WELCOME10',
    name: 'Early Adopter 10%',
    type: 'percent',
    amount: '10.00',
    min_purchase: '100.00',
    min_quantity: 1,
    start_date: '2026-01-01',
    end_date: '2026-12-31',
    usage_limit: 100,
    used_count: 14,
    scope: 'all',
  },
  {
    id: 2,
    code: 'STARTUP50',
    name: 'Startup Discount $50',
    type: 'fixed',
    amount: '50.00',
    min_purchase: '250.00',
    min_quantity: 1,
    start_date: '2026-01-01',
    end_date: '2026-12-31',
    usage_limit: 50,
    used_count: 5,
    scope: 'all',
  },
];

export const MOCK_SUBSCRIPTIONS: Subscription[] = [
  {
    id: 1,
    subscription_number: 'SUB-00001',
    customer_id: 3,
    customer_name: 'Acme Corporation',
    customer_email: 'acme@client.com',
    plan_id: 1,
    plan_name: 'Pro Monthly',
    status: 'active',
    current_period_start: '2026-10-01',
    current_period_end: '2026-10-31',
    total_amount: '1059.00',
    allowed_actions: ['pause', 'renew', 'close'],
    lines: [
      {
        id: 1,
        product_name: 'Brightloop Enterprise Cloud',
        variant_name: 'Brand: Odoo Integration (+560.00)',
        quantity: 1,
        unit_price: '1059.00',
        tax_rate: '18.00',
        line_total: '1059.00',
      },
    ],
  },
  {
    id: 2,
    subscription_number: 'SUB-00002',
    customer_id: 3,
    customer_name: 'Acme Corporation',
    customer_email: 'acme@client.com',
    plan_id: 2,
    plan_name: 'Enterprise Annual',
    status: 'quotation',
    current_period_start: '2026-11-01',
    current_period_end: '2027-10-31',
    total_amount: '1990.00',
    allowed_actions: ['confirm', 'cancel'],
    lines: [
      {
        id: 2,
        product_name: 'Dedicated Support Tier',
        quantity: 1,
        unit_price: '1990.00',
        tax_rate: '18.00',
        line_total: '1990.00',
      },
    ],
  },
];

export const MOCK_INVOICES: Invoice[] = [
  {
    id: 1,
    invoice_number: 'INV-2026-0001',
    subscription_id: 1,
    customer_name: 'Acme Corporation',
    status: 'paid',
    issue_date: '2026-10-01',
    due_date: '2026-10-15',
    subtotal: '1059.00',
    discount_total: '0.00',
    tax_total: '190.62',
    total: '1249.62',
    amount_paid: '1249.62',
    balance: '0.00',
    is_overdue: false,
    days_overdue: 0,
    sent_at: '2026-10-01T10:00:00Z',
    lines: [
      {
        id: 1,
        description: 'Brightloop Enterprise Cloud (Odoo Brand)',
        quantity: 1,
        unit_price: '1059.00',
        discount_amount: '0.00',
        tax_amount: '190.62',
        total: '1249.62',
      },
    ],
  },
  {
    id: 2,
    invoice_number: 'INV-2026-0002',
    subscription_id: 1,
    customer_name: 'Acme Corporation',
    status: 'confirmed',
    issue_date: '2026-10-10',
    due_date: '2026-10-24',
    subtotal: '500.00',
    discount_total: '50.00',
    tax_total: '81.00',
    total: '531.00',
    amount_paid: '200.00',
    balance: '331.00',
    is_overdue: true,
    days_overdue: 7,
    sent_at: '2026-10-10T14:30:00Z',
    lines: [
      {
        id: 2,
        description: 'Monthly Maintenance & Addons',
        quantity: 1,
        unit_price: '500.00',
        discount_amount: '50.00',
        tax_amount: '81.00',
        total: '531.00',
      },
    ],
  },
];
