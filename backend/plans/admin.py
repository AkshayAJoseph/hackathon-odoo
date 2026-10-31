from django.contrib import admin
from plans.models import Plan, QuotationTemplate, TemplateLine

class TemplateLineInline(admin.TabularInline):
    model = TemplateLine
    extra = 1

@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'billing_period', 'price', 'min_quantity', 'available_from', 'available_to', 'pausable', 'closable', 'renewable', 'auto_close')
    list_filter = ('billing_period', 'pausable', 'closable', 'renewable', 'auto_close')
    search_fields = ('name',)

@admin.register(QuotationTemplate)
class QuotationTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'plan', 'validity_days')
    search_fields = ('name', 'plan__name')
    inlines = [TemplateLineInline]
