# Brightloop Subscription Management System

Brightloop is an end-to-end subscription management, recurring billing, and customer portal platform built for the Odoo Hackathon. It couples a Django REST Framework backend with a React (Vite + Tailwind) frontend to manage the entire lifecycle of SaaS plans, contracts, automated billing runs, payments, taxes, and customer self-service.

---

## Quick Start

### 1. Backend Setup

Prerequisites: Python 3.12+ (tested on Python 3.13) and SQLite / PostgreSQL.

```bash
cd backend
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt   # or django djangorestframework djangorestframework-simplejwt django-cors-headers pytest pytest-django factory_boy
python manage.py migrate
python manage.py seed_demo --reset
python manage.py runserver 8000
```

> **Note on Seeding**: `python manage.py seed_demo --reset` populates:
> - Tiered plans, products, taxes (GST 18%, VAT 5%), and discount rules
> - 5,000 subscriptions and 12 months of historical billing/payment records
> - Exactly 40 subscriptions due for billing today, ready for the live demo run.

### 2. Frontend Setup

Prerequisites: Node.js 18+ and npm / pnpm.

```bash
cd frontend
npm install
npm run dev
```

The frontend will run on `http://localhost:5173` (configured to proxy requests to `http://localhost:8000`).

### 3. Docker (Optional DB)

To spin up a local PostgreSQL 16 container instead of SQLite:
```bash
docker compose up -d db
```

---

## Demo Accounts

All seeded demo accounts share the password: `Brightloop@123`

| Role | Username / Email | Access Scope |
|---|---|---|
| **Admin** | `admin@brightloop.test` | System settings, tax configuration, discounts management, staff & plan admin |
| **Staff** | `staff1@brightloop.test`<br>`staff2@brightloop.test`<br>`staff3@brightloop.test` | Operations, customer management, manual/cron billing runs, invoice issuance, recording payments |
| **Customer** | `customer1@brightloop.test`<br>... `customer200@brightloop.test` | Customer Portal: viewing active subscriptions, downloading invoice PDFs/HTML, reviewing payment history |

---

## Core System Architecture

```
                  ┌──────────────────────────────────────────────┐
                  │          React Frontend (Vite + TS)          │
                  │  Staff Console  │  Admin Ops  │ Cust Portal  │
                  └───────────────────────┬──────────────────────┘
                                          │ JWT Authenticated REST
                                          ▼
┌────────────────────────────────────────────────────────────────────────┐
│                        Django REST Framework Core                      │
├─────────────────┬───────────────────┬─────────────────┬────────────────┤
│    accounts     │   subscriptions   │     billing     │    payments    │
│  Custom User    │  Plans, Products  │ Invoicing Engine│  Transactions  │
│  RBAC & Tokens  │  Contract Cycles  │ Tax & Discounts │  Row Locks     │
└─────────────────┴───────────────────┴─────────────────┴────────────────┘
```

### Module Breakdown

- **`accounts`**: Role-based authentication (`admin`, `staff`, `customer`) using JWTs, registration, password reset flows, and tenant/customer profile associations.
- **`plans` & `catalog`**: Configurable billing cadences (monthly, quarterly, annual), line items, base pricing, and automated tax rule resolution (`resolve_tax`).
- **`subscriptions`**: Subscription lifecycles (`draft`, `active`, `paused`, `closed`), auto-close rules on plan expiry, and automated next-billing-date calculators with month-end date clamping.
- **`discounts`**: Rule-based discount engine supporting percent/fixed amounts, validity windows, min spend/quantity checks, usage thresholds, and auto-apply priority logic.
- **`billing`**: Idempotent billing run engine (`run_billing`), line-level price/tax/discount snapshots, chronological catch-up billing, sequential numbering (`INV-00001`), and printable invoice previews.
- **`payments`**: Concurrency-safe payment recording with database row locking (`select_for_update`), overpayment guards, overdue tracking, and automated invoice status transitions (`paid`, `partially_paid`).
- **`reports`**: MRR (Monthly Recurring Revenue), ARR, churn metrics, and revenue analytics.

---

## Key Engineering Decisions

### 1. Decimal Precision Throughout
All currency, prices, taxes, and discounts use Python's `Decimal` with `ROUND_HALF_UP` quantized to 2 decimal places. Floating-point numbers are strictly prohibited across models and business logic to eliminate rounding drift.

### 2. Snapshot Pricing
When an invoice is generated, the line items snapshot the product unit price, applied tax rate, and computed discount amount at that exact moment. Modifying a product's price or changing a tax rate in the admin panel later will never alter previously issued invoices.

### 3. Idempotent Billing Engine
The billing generator is completely safe to run multiple times:
- Enforced at the database level using a `UniqueConstraint(fields=['subscription', 'period_start'])`.
- Each subscription is processed inside an isolated transaction with row locking (`select_for_update`).
- Sequential invoice numbering uses a dedicated atomic counter table (`InvoiceSequence`) to ensure no numbers are skipped during concurrency.
- If a scheduler skips a cycle or runs late, the engine calculates each missed period sequentially in chronological order.

### 4. Overpayment & Concurrency Defense
When recording a payment:
- The target invoice is locked with `select_for_update` to prevent concurrent race conditions.
- Incoming payments are validated against `total - amount_paid`. Any attempt to record an amount exceeding the remaining balance is rejected.
- Invoice states advance strictly based on ledger math: full payment flips the invoice to `paid`, while partial payments leave it in `confirmed` with an updated balance.

---

## 2-Minute Judge Walkthrough

1. **Admin Configurations (`/admin/taxes`, `/admin/discounts`)**:
   - Log in as `admin@brightloop.test`.
   - Show the active GST tax rule (18%) and an auto-apply discount rule (10% off for subscriptions with 5+ seats).
2. **Execute Billing Run (`/staff/billing-run`)**:
   - Log in as `staff1@brightloop.test`.
   - Select today's date and click **Run Billing**.
   - Notice the toast / summary: **40 invoices created**.
   - Click **Run Billing** a second time immediately: **0 invoices created**, proving idempotency.
3. **Inspect Generated Invoice (`/staff/invoices`)**:
   - Open any newly generated invoice.
   - Show the snapshotted line items, applied discount, tax breakdown, and status (`confirmed`).
   - Click **Print / Preview** to see the clean, printable HTML view.
4. **Record Payment (`/staff/invoices/:id`)**:
   - Open a confirmed invoice with an open balance.
   - Record a partial payment: see the remaining balance decrease while the status remains `confirmed`.
   - Record the exact remaining balance: watch the invoice status switch to `paid`.
   - Try entering an amount greater than the balance to show the built-in overpayment prevention.
5. **Customer Self-Service Portal (`/portal/invoices`)**:
   - Log in as `customer1@brightloop.test`.
   - Demonstrate that customer isolation is enforced: customers can only view and download their own subscription invoices.

---

## Test Suite

The test suite covers unit, integration, permission, and concurrency test cases across all modules.

```bash
cd backend
python -m pytest
```

All 156 tests run against the SQLite test database (or PostgreSQL if configured), verifying:
- All 27 core billing engine specifications (tax snapshoting, month-end date math, overpayment protection, auto-apply discounts).
- RBAC permissions on admin, staff, and customer portal endpoints.
- High-volume demo seeding and query performance.
