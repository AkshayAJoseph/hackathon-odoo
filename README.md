# Brightloop Subscription Management System

Brightloop is a unified subscription management and recurring billing platform built for the Odoo Hackathon.

## 🚀 Quick Start

### 1. Requirements & Setup
- Python 3.12+ (tested on Python 3.13)
- Dependencies: `django`, `djangorestframework`, `djangorestframework-simplejwt`, `django-cors-headers`, `pytest`, `pytest-django`, `factory_boy`

```bash
cd backend
python manage.py migrate
python manage.py seed_demo --reset
```

### 2. Demo Logins
All accounts share the password: `Brightloop@123`
- **Admin**: `admin@brightloop.test`
- **Staff**: `staff1@brightloop.test`, `staff2@brightloop.test`, `staff3@brightloop.test`
- **Customer**: `customer1@brightloop.test` ... `customer200@brightloop.test`

---

## 🏛️ Billing Architecture & Design Decisions (Amrutha / P2)

### 1. Money & Numerical Precision
- **Decimal Everywhere**: All currency and pricing calculations use Python's `Decimal` with `ROUND_HALF_UP` rounded to 2 decimal places (`Decimal('0.01')`). Floats are never used to eliminate binary floating point drift.
- **Snapshot Pricing**: Subscription lines snapshot unit prices at creation time. Invoice lines snapshot unit price, applicable tax rate, and computed discount amount at billing run time. Future price or tax rate modifications never mutate historical invoices.

### 2. Idempotent Billing Engine (`run_billing`)
- **Database Unique Constraint**: `UniqueConstraint(fields=['subscription', 'period_start'])` enforces at the database level that no period can ever be billed twice.
- **Atomic Operations & Row Locking**: Each subscription is evaluated in an isolated `transaction.atomic()` block with `select_for_update(skip_locked=True)` (or `select_for_update()` in SQLite). If an unexpected exception occurs on one subscription, it rolls back that subscription only and does not impact others.
- **Sequential Numbering**: `next_invoice_number()` uses a locked counter table (`InvoiceSequence`) with `select_for_update` to guarantee gapless, concurrency-safe sequential identifiers (`INV-00001`, `INV-00002`).
- **Catch-up Billing**: If a cron job or scheduled execution runs late and misses multiple billing periods, the engine catches up each missed period in chronological order until `next_billing_date > as_of`.
- **Month-End Clamping**: `add_period` automatically clamps to the last valid calendar day (e.g. 31 Jan + 1 month -> 28/29 Feb, preserving consistent billing cycles).
- **Auto-Close Expiry**: Subscriptions on plans with `auto_close=True` are automatically transitioned to `closed` when `next_billing_date > expiry_date`, creating no invoices beyond expiry.

### 3. Smart Discounts Engine
- **Admin-Governed**: Discount configuration endpoints (`/api/discounts/`) are strictly restricted to Admin users (`403` for staff and customers).
- **Automatic Auto-Apply**: At invoice generation, `find_eligible_discounts` evaluates validity date windows, minimum purchase amounts, minimum quantities, remaining usage limits (`times_used < usage_limit`), and product/subscription scopes.
- **Single Best Discount**: Applies the single best discount that maximizes customer savings.
- **Atomic Usage Tracking**: `DiscountUsage` records and `times_used` increments are committed in the same database transaction as invoice creation.

### 4. Payments, Overdue & Security
- **Concurrency Protection**: Payment processing locks the invoice row with `select_for_update` to prevent race conditions from duplicate simultaneous payments.
- **Overpayment Prevention**: Payments exceeding the current outstanding balance (`total - amount_paid`) are rejected with a clear validation error.
- **State Machine Integrity**: Status transitions are strictly enforced (`draft` -> `confirmed` -> `paid`). Invoices can only move to `paid` when sum of recorded payments matches or exceeds `total`. Paid invoices cannot be cancelled.
- **Customer Query Isolation**: Customers can only view and access their own subscriptions and invoices (enforced via database querysets at `/api/invoices/`, returning `404` for unauthorized IDs).

---

## 🎯 2-Minute Demo Script

1. **Admin Discount & Tax Rule**:
   - Admin creates a 10% discount for 5+ seats and an active 18% GST rule.
2. **Click "Run Billing"**:
   - Summary displays **40 created**.
   - Click "Run Billing" immediately again: summary displays **0 created**, demonstrating live idempotency.
3. **Open Fresh Invoice**:
   - Verify line items, 18% GST tax calculation, and the 10% discount prefilled automatically.
   - Click **Confirm**, **Send**, and **Print** (clean print stylesheet preview).
4. **Record Payment**:
   - Record a partial payment: balance decreases, status remains `confirmed`.
   - Record the remainder: balance hits `0.00`, status flips automatically to `paid`.
5. **Overdue Invoices**:
   - View overdue invoices table (highlighted in red with days overdue computed).
6. **Discount Safety**:
   - Show that expired discounts and limit-reached discounts were automatically skipped.

---

## 🎤 Q&A Answers Reference

| Question | Answer |
|---|---|
| **How do you prevent double billing?** | Database unique constraint on `(subscription, period_start)` plus `get_or_create`. The billing date advances only after invoice creation in the same transaction. Demo: click Run Billing twice. |
| **What if the job runs late or fails halfway?** | Each subscription bills in its own atomic transaction so failures affect only that row. A late run catches up all missed periods chronologically. |
| **How is tax calculated and stored?** | Per line from admin rules, applied after discount, rounded half-up to 2 places. The rate and amount are snapshotted on the invoice line so future rate adjustments never alter historical invoices. |
| **Why Decimal and not float?** | Floats cause binary rounding drift (such as `0.1 + 0.2 != 0.3`). Money operations require exact base-10 `Decimal` arithmetic with `ROUND_HALF_UP`. |
| **What stops overpayment?** | The invoice row is locked with `select_for_update` and the proposed amount is checked against `balance` inside the transaction. |
| **What is overdue?** | An invoice with `status='confirmed'`, `due_date < today`, and `balance > 0`. |
| **How would this scale to millions of subscriptions?** | Decouple `run_billing` into Celery background workers partitioned by customer ID ranges; the DB unique constraint ensures idempotency even during worker retries. |

---

## 🧪 Testing & Verification

Run the entire test suite:
```bash
cd backend
python -m pytest
```

All 27 must-pass tests from Section 5 of the build guide pass with 100% coverage.
