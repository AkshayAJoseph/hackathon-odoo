import random
import time
from datetime import date, timedelta
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from django.db import transaction

from accounts.models import User
from catalog.models import Product, ProductVariant, Tax
from plans.models import Plan, QuotationTemplate, TemplateLine
from subscriptions.models import Subscription, SubscriptionLine
from discounts.models import Discount, DiscountUsage
from billing.models import Invoice, InvoiceLine, InvoiceSequence
from payments.models import Payment
from core.models import AuditLog

class Command(BaseCommand):
    help = "Seeds demo data: 5,000 subscriptions, 12 months history, products, plans, taxes, discounts, and users."

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Delete all existing demo data before seeding'
        )

    def handle(self, *args, **options):
        start_time = time.time()
        today = date.today()

        if options['reset']:
            self.stdout.write("Resetting existing data...")
            Payment.objects.all().delete()
            DiscountUsage.objects.all().delete()
            InvoiceLine.objects.all().delete()
            Invoice.objects.all().delete()
            InvoiceSequence.objects.all().delete()
            SubscriptionLine.objects.all().delete()
            Subscription.objects.all().delete()
            TemplateLine.objects.all().delete()
            QuotationTemplate.objects.all().delete()
            Discount.objects.all().delete()
            Plan.objects.all().delete()
            Tax.objects.all().delete()
            ProductVariant.objects.all().delete()
            Product.objects.all().delete()
            User.objects.all().delete()
            AuditLog.objects.all().delete()
            self.stdout.write(self.style.SUCCESS("Database wiped clean."))

        self.stdout.write("Starting high-performance seed...")

        # 1. Users
        hashed_password = make_password('Brightloop@123')
        users_to_create = []

        # 1 admin
        users_to_create.append(User(
            email='admin@brightloop.test',
            password=hashed_password,
            name='Alice Admin',
            role='admin',
            is_staff=True,
            is_superuser=True
        ))

        # 3 staff
        for i in range(1, 4):
            users_to_create.append(User(
                email=f'staff{i}@brightloop.test',
                password=hashed_password,
                name=f'Staff Member {i}',
                role='staff',
                is_staff=True
            ))

        # 200 customers
        for i in range(1, 201):
            users_to_create.append(User(
                email=f'customer{i}@brightloop.test',
                password=hashed_password,
                name=f'Customer {i}',
                role='customer',
                company=f'Enterprise {i} Ltd',
                phone=f'+1-555-01{i:02d}',
                address=f'{i} Innovation Blvd'
            ))

        User.objects.bulk_create(users_to_create, batch_size=500)
        all_customers = list(User.objects.filter(role='customer'))
        admin_user = User.objects.get(email='admin@brightloop.test')
        self.stdout.write(f"Created {len(users_to_create)} users.")

        # 2. Products & Variants
        product_configs = [
            ("Core ERP Platform", "software", Decimal("250.00"), Decimal("50.00")),
            ("CRM Suite", "software", Decimal("150.00"), Decimal("30.00")),
            ("Inventory & Supply Chain", "software", Decimal("180.00"), Decimal("35.00")),
            ("Accounting & Invoicing", "software", Decimal("120.00"), Decimal("20.00")),
            ("HR & Payroll", "software", Decimal("90.00"), Decimal("15.00")),
            ("Dedicated Support SLA", "service", Decimal("500.00"), Decimal("100.00")),
            ("Custom Implementation", "service", Decimal("1200.00"), Decimal("400.00")),
            ("Cloud Migration Consulting", "service", Decimal("800.00"), Decimal("250.00")),
            ("Extra 500GB Storage", "addon", Decimal("40.00"), Decimal("5.00")),
            ("API High-Volume Tier", "addon", Decimal("75.00"), Decimal("10.00")),
            ("Advanced Security & SSO", "addon", Decimal("60.00"), Decimal("8.00")),
            ("Analytics & BI Dashboard", "software", Decimal("110.00"), Decimal("25.00")),
        ]

        products = []
        for name, p_type, s_price, c_price in product_configs:
            products.append(Product(name=name, type=p_type, sales_price=s_price, cost_price=c_price))
        Product.objects.bulk_create(products)
        products = list(Product.objects.all())

        # Variants, specifically Brand=Odoo with extra_price 560
        core_erp = products[0]
        crm_suite = products[1]
        variants = [
            ProductVariant(product=core_erp, attribute="Brand", value="Odoo", extra_price=Decimal("560.00")),
            ProductVariant(product=core_erp, attribute="Deployment", value="Multi-Region", extra_price=Decimal("200.00")),
            ProductVariant(product=crm_suite, attribute="Edition", value="Pro AI", extra_price=Decimal("80.00")),
        ]
        ProductVariant.objects.bulk_create(variants)
        self.stdout.write(f"Created 12 products and variants (including Brand=Odoo +$560).")

        # 3. Taxes
        taxes = [
            Tax(name="GST 18%", rate_percent=Decimal("18.00"), type="percent", is_active=True, applies_to=None),
            Tax(name="GST 5%", rate_percent=Decimal("5.00"), type="percent", is_active=True, applies_to=None),
            Tax(name="Zero Rated", rate_percent=Decimal("0.00"), type="percent", is_active=True, applies_to=None),
        ]
        Tax.objects.bulk_create(taxes)
        taxes = list(Tax.objects.all())
        tax_18 = taxes[0]

        # 4. Plans
        plans = [
            Plan(name="Daily Flex", price=Decimal("15.00"), billing_period="daily", min_quantity=1,
                 available_from=today - timedelta(days=365), available_to=today + timedelta(days=365),
                 auto_close=False, closable=True, pausable=True, renewable=True),
            Plan(name="Weekly Sprint", price=Decimal("75.00"), billing_period="weekly", min_quantity=1,
                 available_from=today - timedelta(days=365), available_to=today + timedelta(days=365),
                 auto_close=False, closable=True, pausable=True, renewable=True),
            Plan(name="Monthly Pro", price=Decimal("250.00"), billing_period="monthly", min_quantity=1,
                 available_from=today - timedelta(days=365), available_to=today + timedelta(days=365),
                 auto_close=False, closable=True, pausable=True, renewable=True),
            Plan(name="Yearly Enterprise", price=Decimal("2500.00"), billing_period="yearly", min_quantity=5,
                 available_from=today - timedelta(days=365), available_to=today + timedelta(days=365),
                 auto_close=True, closable=False, pausable=False, renewable=True),
        ]
        Plan.objects.bulk_create(plans)
        plans = list(Plan.objects.all())
        monthly_plan = plans[2]

        # 5. Discounts (4 specified in guide)
        discounts = [
            # 1. 10% for 5+ seats (active)
            Discount(name="10% off 5+ seats", kind="percent", value=Decimal("10.00"), min_quantity=5,
                     scope="subscription", is_active=True),
            # 2. Fixed 500 off over 5,000 purchase (active)
            Discount(name="Fixed 500 off >$5k", kind="fixed", value=Decimal("500.00"), min_purchase=Decimal("5000.00"),
                     scope="subscription", is_active=True),
            # 3. EXPIRED
            Discount(name="Black Friday Expired", kind="percent", value=Decimal("25.00"),
                     start_date=today - timedelta(days=120), end_date=today - timedelta(days=60),
                     scope="subscription", is_active=True),
            # 4. usage_limit=2 already used 2 times
            Discount(name="VIP Limited 2", kind="fixed", value=Decimal("200.00"), usage_limit=2, times_used=2,
                     scope="subscription", is_active=True),
        ]
        Discount.objects.bulk_create(discounts)

        # 6. Quotation Templates
        templates = [
            QuotationTemplate(name="Standard SaaS Starter", plan=monthly_plan, validity_days=30, notes="Starter package"),
            QuotationTemplate(name="Enterprise Odoo Bundle", plan=monthly_plan, validity_days=45, notes="Full ERP with Odoo variant"),
            QuotationTemplate(name="Annual Consulting Pack", plan=plans[3], validity_days=60, notes="Yearly consulting SLA"),
        ]
        QuotationTemplate.objects.bulk_create(templates)
        templates = list(QuotationTemplate.objects.all())

        template_lines = [
            TemplateLine(template=templates[0], product=products[0], quantity=2),
            TemplateLine(template=templates[0], product=products[1], quantity=2),
            TemplateLine(template=templates[1], product=products[0], quantity=10),
            TemplateLine(template=templates[1], product=products[5], quantity=1),
            TemplateLine(template=templates[2], product=products[6], quantity=1),
        ]
        TemplateLine.objects.bulk_create(template_lines)

        # 7. 5,000 Subscriptions across statuses:
        # About 3,500 Active, 600 Closed, 400 Confirmed, 300 Quotation/Draft
        # Leave exactly 40 Active subscriptions with next_billing_date <= today and no invoice!
        self.stdout.write("Generating 5,000 subscriptions...")

        status_distribution = (
            ['active'] * 3460 +         # General active
            ['active_due_demo'] * 40 +  # Exactly 40 due today with NO invoice for demo
            ['closed'] * 600 +
            ['confirmed'] * 400 +
            ['quotation'] * 200 +
            ['draft'] * 300
        )
        random.seed(42) # Reproducible seed data
        random.shuffle(status_distribution)

        subscriptions = []
        for i, sub_status in enumerate(status_distribution, start=1):
            cust = all_customers[i % len(all_customers)]
            plan = monthly_plan if i % 10 != 0 else plans[i % len(plans)]
            start_offset = random.randint(30, 360)
            start_d = today - timedelta(days=start_offset)

            if sub_status == 'active_due_demo':
                actual_status = 'active'
                next_bill = today # Due today!
                exp_date = today + timedelta(days=365)
            elif sub_status == 'active':
                actual_status = 'active'
                next_bill = today + timedelta(days=random.randint(2, 28))
                exp_date = today + timedelta(days=365)
            elif sub_status == 'closed':
                actual_status = 'closed'
                next_bill = None
                exp_date = today - timedelta(days=random.randint(10, 60))
            elif sub_status == 'confirmed':
                actual_status = 'confirmed'
                next_bill = today + timedelta(days=random.randint(5, 30))
                exp_date = None
            else: # draft or quotation
                actual_status = sub_status
                next_bill = None
                exp_date = None

            subscriptions.append(Subscription(
                id=i,
                number=f"SUB-{i:05d}",
                customer=cust,
                plan=plan,
                start_date=start_d,
                expiry_date=exp_date,
                payment_terms=15,
                status=actual_status,
                is_paused=False,
                next_billing_date=next_bill,
                created_by=admin_user
            ))

        Subscription.objects.bulk_create(subscriptions, batch_size=1000)
        self.stdout.write("Subscriptions created. Generating subscription lines...")

        # Subscription lines (1 to 4 lines per subscription)
        # Ensure at least one due-today subscription has 5+ seats of product[0] for the discount demo!
        sub_lines = []
        for s in subscriptions:
            # Check if this is the discount demo candidate
            if s.next_billing_date == today and s.status == 'active' and s.id % 40 == 0:
                # 5 seats at 250 -> 1250, qualifies for 10% discount!
                sub_lines.append(SubscriptionLine(
                    subscription=s,
                    product=products[0],
                    quantity=6,
                    unit_price=products[0].sales_price,
                    tax=tax_18,
                    line_total=products[0].sales_price * 6
                ))
            else:
                num_lines = random.randint(1, 3)
                selected_prods = random.sample(products, num_lines)
                for prod in selected_prods:
                    qty = random.randint(1, 4)
                    sub_lines.append(SubscriptionLine(
                        subscription=s,
                        product=prod,
                        quantity=qty,
                        unit_price=prod.sales_price,
                        tax=tax_18,
                        line_total=prod.sales_price * qty
                    ))

        SubscriptionLine.objects.bulk_create(sub_lines, batch_size=1000)
        self.stdout.write(f"Created {len(sub_lines)} subscription lines.")

        # 8. Invoices and Payments for past 12 months:
        # For active (non-due) and closed subscriptions, create historical invoices
        self.stdout.write("Generating invoices and payments history over 12 months...")

        invoices = []
        inv_lines = []
        payments = []

        inv_counter = 1
        payment_counter = 1

        # We will create invoices for a representative sample of active and closed subscriptions
        # to achieve thousands of invoices quickly and efficiently
        billed_subs = [s for s in subscriptions if s.status in ['active', 'closed'] and s.next_billing_date != today]

        for s in billed_subs:
            # 1 to 3 historical invoices per sub
            months_active = min(12, max(1, (today - s.start_date).days // 30))
            num_invoices = min(months_active, random.randint(1, 3))

            for m in range(num_invoices, 0, -1):
                p_start = today - timedelta(days=m * 30)
                p_end = p_start + timedelta(days=29)
                issue_d = p_start
                due_d = issue_d + timedelta(days=15)

                subtotal = Decimal("250.00")
                tax_amt = Decimal("45.00")
                total = Decimal("295.00")

                inv_num = f"INV-{inv_counter:05d}"
                inv_counter += 1

                # Realistic distribution:
                # 70% Paid, 15% Confirmed not yet due, 8-10% Confirmed and OVERDUE, few Cancelled
                rnd = random.random()
                if rnd < 0.70:
                    inv_status = 'paid'
                    amt_paid = total
                elif rnd < 0.85:
                    inv_status = 'confirmed'
                    amt_paid = Decimal("0.00")
                    due_d = today + timedelta(days=random.randint(1, 15)) # Not yet due
                elif rnd < 0.95:
                    inv_status = 'confirmed'
                    amt_paid = Decimal("0.00")
                    due_d = today - timedelta(days=random.randint(1, 30)) # OVERDUE!
                else:
                    inv_status = 'cancelled'
                    amt_paid = Decimal("0.00")

                inv = Invoice(
                    id=inv_counter - 1,
                    number=inv_num,
                    subscription=s,
                    customer=s.customer,
                    period_start=p_start,
                    period_end=p_end,
                    issue_date=issue_d,
                    due_date=due_d,
                    status=inv_status,
                    subtotal=subtotal,
                    discount_total=Decimal("0.00"),
                    tax_total=tax_amt,
                    total=total,
                    amount_paid=amt_paid
                )
                invoices.append(inv)

                # Invoice line
                inv_lines.append(InvoiceLine(
                    invoice=inv,
                    product=products[0],
                    description="Core ERP Platform Monthly",
                    quantity=1,
                    unit_price=Decimal("250.00"),
                    discount=Decimal("0.00"),
                    tax_rate=Decimal("18.00"),
                    tax_amount=tax_amt,
                    line_total=total
                ))

                # If paid, generate payment record
                if inv_status == 'paid':
                    pay_method = random.choice(['card', 'bank_transfer', 'upi', 'cash', 'cheque'])
                    payments.append(Payment(
                        id=payment_counter,
                        invoice=inv,
                        method=pay_method,
                        amount=total,
                        payment_date=issue_d + timedelta(days=random.randint(1, 10)),
                        note="Automatic recurring payment",
                        recorded_by=admin_user
                    ))
                    payment_counter += 1

        Invoice.objects.bulk_create(invoices, batch_size=1000)
        InvoiceLine.objects.bulk_create(inv_lines, batch_size=1000)
        Payment.objects.bulk_create(payments, batch_size=1000)

        # Update InvoiceSequence to continue sequentially
        InvoiceSequence.objects.update_or_create(
            name='invoice',
            defaults={'last_number': inv_counter}
        )

        elapsed = time.time() - start_time

        # Target verification
        active_count = Subscription.objects.filter(status='active').count()
        due_today_count = Subscription.objects.filter(status='active', next_billing_date__lte=today).count()
        invoice_count = Invoice.objects.count()
        overdue_count = sum(1 for inv in Invoice.objects.filter(status='confirmed') if inv.is_overdue())

        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(self.style.SUCCESS(f"SEED DATA COMPLETED in {elapsed:.2f} seconds!"))
        self.stdout.write("=" * 60)
        self.stdout.write(f"Total Subscriptions : {Subscription.objects.count()} (Active: {active_count})")
        self.stdout.write(f"Due-Today (for demo): {due_today_count} (Expected: 40)")
        self.stdout.write(f"Total Invoices      : {invoice_count}")
        self.stdout.write(f"Overdue Invoices    : {overdue_count}")
        self.stdout.write(f"Total Payments      : {Payment.objects.count()}")
        self.stdout.write("\nDemo Credentials:")
        self.stdout.write("  Admin   : admin@brightloop.test    | Password: Brightloop@123")
        self.stdout.write("  Staff   : staff1@brightloop.test   | Password: Brightloop@123")
        self.stdout.write("  Customer: customer1@brightloop.test| Password: Brightloop@123")
        self.stdout.write("=" * 60 + "\n")
