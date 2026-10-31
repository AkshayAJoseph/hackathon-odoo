from django.contrib import admin
from subscriptions.models import Subscription, SubscriptionLine, SubscriptionSequence

class SubscriptionLineInline(admin.TabularInline):
    model = SubscriptionLine
    extra = 0
    fields = ('product', 'variant', 'quantity', 'unit_price', 'discount_amount', 'line_total', 'tax')

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('number', 'customer', 'plan', 'status', 'is_paused', 'next_billing_date', 'expiry_date', 'payment_terms', 'created_at')
    list_filter = ('status', 'is_paused', 'plan')
    search_fields = ('number', 'customer__email', 'customer__name')
    date_hierarchy = 'created_at'
    inlines = [SubscriptionLineInline]

@admin.register(SubscriptionSequence)
class SubscriptionSequenceAdmin(admin.ModelAdmin):
    list_display = ('name', 'last_number')
