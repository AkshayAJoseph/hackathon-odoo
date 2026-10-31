# Brightloop Subscription Management System - Specification

## 2. Requirements Checklist

| # | Scene | Requirement | Priority |
|---|---|---|---|
| 1 | Sign up | Register with email + password; email unique across accounts | P0 |
| 2 | Sign up | Password: more than 8 characters, 1 uppercase, 1 lowercase, 1 special character | P0 |
| 3 | Sign up | Forgot password sends a reset link to registered email; token expires (30 min); link sets new password | P0 |
| 4 | Roles | Three roles: Admin, Internal staff, Customer (portal) | P0 |
| 5 | Roles | Customer sees only own subscriptions and invoices (enforced in backend queries) | P0 |
| 6 | Roles | Only Admin can create staff members; staff have limited access | P0 |
| 7 | Products | Product: name, type, sales_price, cost_price, notes, is_active | P0 |
| 8 | Products | Variants (attribute + value + extra_price), e.g. Brand = Odoo adds 560 | P0 |
| 9 | Plans | Plan: price, billing_period (daily/weekly/monthly/yearly), min_quantity, available_from and available_to dates | P0 |
| 10 | Plans | Per-plan flags set by Admin: auto_close at end, closable early, pausable, renewable | P0 |
| 11 | Quotes | Quotation templates: preset plan + product lines, validity in days | P0 |
| 12 | Quotes | Create a subscription from a template (lines copied in) | P0 |
| 13 | Subscription | Own number (SUB-00001), customer, plan, start date, expiry date, payment terms | P0 |
| 14 | Subscription | Lines: product, quantity, unit price, taxes, amount | P0 |
| 15 | Subscription | Status flow Draft, Quotation, Confirmed, Active, Closed | P0 |
| 16 | Billing | Invoices generated automatically from due subscriptions, with customer, lines, taxes, totals prefilled | P0 |
| 17 | Billing | Tax calculated automatically from Admin-defined tax rules | P0 |
| 18 | Billing | Invoice actions: confirm, cancel, send, print; status Draft, Confirmed, Paid | P0 |
| 19 | Billing | Never billed twice, never skipped (idempotent billing, per-period uniqueness) | P0 |
| 20 | Discounts | Admin-only rules: fixed or percentage, min purchase or min quantity, start/end dates, usage limit | P0 |
| 21 | Discounts | Applies to specific products or whole subscriptions; auto-appears on next invoice; stops at expiry or limit | P0 |
| 22 | Payments | Record method, amount, date, note against an invoice | P0 |
| 23 | Payments | Invoice shows paid vs outstanding; overdue list for chasing | P0 |
| 24 | Reporting | One dashboard: active subscriptions, revenue collected, amount owed, overdue invoices | P0 |
| 25 | Performance | Every page under 2 seconds with thousands of subscriptions | P0 |
| 26 | Extra | MRR / ARR, CSV export, audit trail | P1 |
| 27 | Extra | Email notifications, partial payments | P2 |

## 3. Architecture and Project Structure

- Backend: Django 5 + DRF + PostgreSQL (or SQLite for local test/dev)
- Frontend: React + Vite + Tailwind + shadcn/ui
- Auth: JWT (SimpleJWT) with role claim

```
brightloop/
├── AGENTS.md
├── docs/
│   └── SPEC.md
├── backend/
│   ├── config/             # settings, urls, jwt, email
│   ├── accounts/           # User(role), signup, login, reset, staff creation
│   ├── catalog/            # Product, ProductVariant, Tax
│   ├── plans/              # Plan, QuotationTemplate, TemplateLine
│   ├── subscriptions/      # Subscription, SubscriptionLine, status machine
│   ├── discounts/          # Discount, DiscountUsage
│   ├── billing/            # Invoice, InvoiceLine, billing engine, numbering
│   ├── payments/           # Payment, method enum
│   ├── reports/            # dashboard aggregates, CSV export
│   └── core/               # permissions, pagination, audit log, seed command
└── frontend/
```

## 4. Database Schema & State Machines

### Table Specifications
- **User**: email (unique), password, role (admin/staff/customer), name, is_active, address, phone, company
- **Product**: name, type (service/software/addon), sales_price, cost_price, notes, is_active
- **ProductVariant**: product FK, attribute (e.g. Brand), value (e.g. Odoo), extra_price (Decimal, e.g. 560)
- **Tax**: name, rate_percent, type (percent/fixed), is_active, applies_to (optional product FK or None for all)
- **Plan**: name, price, billing_period (daily/weekly/monthly/yearly), min_quantity, available_from, available_to, auto_close, closable, pausable, renewable
- **QuotationTemplate**: name, plan FK, validity_days, notes
- **TemplateLine**: template FK, product FK, variant FK (nullable), quantity
- **Subscription**: number (unique, e.g. SUB-00001), customer FK, plan FK, start_date, expiry_date, payment_terms, status (draft/quotation/confirmed/active/closed), is_paused, next_billing_date, created_by. Indexes: (status, customer, next_billing_date, expiry_date).
- **SubscriptionLine**: subscription FK, product FK, variant FK, quantity, unit_price, tax FK, discount_amount, line_total
- **Discount**: name, kind (fixed/percent), value, min_purchase, min_quantity, start_date, end_date, usage_limit, times_used, scope (product/subscription), product FK (nullable), is_active
- **DiscountUsage**: discount FK, invoice FK, subscription FK, amount, created_at
- **Invoice**: number (unique, e.g. INV-00001), subscription FK, customer FK, period_start, period_end, issue_date, due_date, status (draft/confirmed/paid/cancelled), subtotal, discount_total, tax_total, total, amount_paid, sent_at. UNIQUE(subscription, period_start). Indexes: (status, due_date, customer).
- **InvoiceLine**: invoice FK, product FK, description, quantity, unit_price, discount, tax_rate, tax_amount, line_total
- **Payment**: invoice FK, method (card/bank_transfer/upi/cash/cheque), amount, payment_date, note, recorded_by. Indexes: (invoice, payment_date).
- **AuditLog**: actor FK, action, entity, entity_id, from_status, to_status, note, timestamp

### State Machines & Allowed Transitions
- **Subscription**:
  - Draft -> Quotation (Staff, Admin)
  - Quotation -> Confirmed (Staff, Admin, Customer)
  - Confirmed -> Active (System on start date, or Staff manually)
  - Active -> Closed (System on expiry if auto_close, or Staff if closable)
  - Pause / Resume on Active if plan.pausable
  - Renew on Active if plan.renewable (extends expiry by one period)
- **Invoice**:
  - Draft -> Confirmed (Staff, Admin)
  - Draft or Confirmed -> Cancelled (Staff, Admin). Paid invoices cannot be cancelled.
  - Confirmed -> Paid (System, when sum of payments >= total)
  - Send and Print do not change status (mark sent_at on send).

## 5. Business Rules (The Core)

### 5.1 Password Validation
`len(pw) > 8` (must be 9+ characters), at least 1 uppercase, at least 1 lowercase, at least 1 special char (`not c.isalnum()`).

### 5.2 Password Reset
Single-use token with 30-minute expiry; email reset link to `/reset/<uid>/<token>`; no account enumeration.

### 5.3 Pricing and Line Totals
- unit_price = product.sales_price + variant.extra_price
- line_net = quantity * unit_price - discount
- tax = line_net * (rate / 100)
- line_total = line_net + tax
Discount comes off before tax. Round each line to 2 decimals using `ROUND_HALF_UP`.
Invoice totals = sum of invoice lines.

### 5.4 Tax Engine
Resolution order for a line: tax on product, else default tax, else 0. Store rate used on invoice line.

### 5.5 Discount Engine
Eligibility:
1. Active and start_date <= date <= end_date.
2. times_used < usage_limit (if limit set).
3. min_purchase <= subtotal and min_quantity <= total quantity (if set).
4. Scope matches: product-scoped applies only to matching product lines; subscription-scoped applies to subtotal.
Amount: fixed = value, percent = net * value / 100. Capped so line/subtotal never negative. Best eligible discount per scope wins. Records DiscountUsage and increments times_used atomically.

### 5.6 Billing Engine
- Run billing for active, unpaused subscriptions where next_billing_date <= as_of.
- Idempotency via unique constraint on (subscription, period_start) and get_or_create.
- Missed periods catch-up: loop period_start advancing by billing_period until next_billing_date > as_of.
- add_period handles month ends (clamping e.g. 31 Jan -> 28/29 Feb).
- If plan.auto_close and next_billing_date > expiry_date, close subscription.
- Row-level lock: select_for_update(skip_locked=True) and transaction.atomic per subscription.
- Summary return: {created, skipped, failed: [{subscription, reason}]}.

### 5.7 Payments and Overdue
- Record payment against invoice. Update amount_paid = sum(payments).
- If amount_paid >= total, flip to Paid; otherwise stays Confirmed.
- Reject payments exceeding outstanding balance (overpayment error).
- Reject payments on Draft or Cancelled invoices.
- Payment methods: card, bank_transfer, upi, cash, cheque.
- Overdue: Confirmed status, due_date < today, balance > 0.
- Due date = issue_date + subscription.payment_terms days.

### 5.8 Plan Availability and Lifecycle
- Available only if available_from <= today <= available_to.
- Enforce min_quantity on subscription lines.

### 5.9 Dashboard Metrics
- MRR: sum over active subscriptions normalized to monthly:
  - yearly / 12, weekly * 52 / 12, daily * 365 / 12, monthly * 1.
- ARR = MRR * 12.
- Revenue collected = sum of payments in range.
- Outstanding = sum(total - amount_paid) over Confirmed invoices.

## 6. API Endpoints
All under `/api/`, JSON response, paginated at 25:
- Auth: `/api/auth/signup/`, `/api/auth/login/`, `/api/auth/forgot/`, `/api/auth/reset/`, `/api/auth/me/`
- Staff: `/api/staff/`
- Products: CRUD `/api/products/`, `/api/products/{id}/variants/`
- Taxes: CRUD `/api/taxes/`
- Plans: CRUD `/api/plans/`
- Quotation Templates: CRUD `/api/quotation-templates/`, `/{id}/create-subscription/`
- Subscriptions: CRUD `/api/subscriptions/`, actions `/{id}/send-quote/`, `/confirm/`, `/activate/`, `/close/`, `/pause/`, `/resume/`, `/renew/`
- Discounts: CRUD `/api/discounts/` (Admin only)
- Invoices: GET `/api/invoices/`, GET `/{id}/`, POST `/{id}/confirm/`, `/cancel/`, `/send/`, GET `/{id}/print/`
- Billing: POST `/api/billing/run/`
- Payments: POST `/api/invoices/{id}/payments/`, GET `/api/payments/`
- Reports: `/api/reports/summary/`, `/active-subscriptions/`, `/revenue/`, `/overdue/`, `/export.csv/`
- Portal: `/api/portal/subscriptions/`, `/api/portal/invoices/`
