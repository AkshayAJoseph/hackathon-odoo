# Brightloop Subscription Management System: agent rules

Read docs/SPEC.md before every task. It defines schema, state machines and business rules.

## Stack
Django 5 + DRF + PostgreSQL (SQLite for local dev/testing), React + Vite + Tailwind + shadcn/ui, JWT auth.

## Hard rules
1. Business logic lives ONLY in `<app>/services.py`. Views and serializers stay thin.
2. Money = Decimal, 2 places, ROUND_HALF_UP. Never float.
3. Permissions enforced in the API (permission classes + role-scoped querysets). Customers may only ever see their own records.
4. Status changes only through service functions that validate transitions and write AuditLog.
5. Billing and payment writes are inside transaction.atomic(). Invoice has UNIQUE(subscription, period_start).
6. Every list endpoint is paginated (25) and filterable server-side. No N+1 queries: use select_related / prefetch_related / annotate.
7. Add DB indexes for every FK and every filtered or sorted field.
8. Write pytest tests for every service function you add. Run them and show results.
9. After each task: run migrations, run tests, start the dev server, and report what you verified. Do not claim done without running it.
10. Stay inside your assigned folder. If you need a change elsewhere, say so instead of editing it.
11. Match field and endpoint names in docs/SPEC.md exactly.
