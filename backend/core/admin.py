from django.contrib import admin
from core.models import AuditLog

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'actor', 'action', 'entity', 'entity_id', 'from_status', 'to_status')
    list_filter = ('entity', 'action')
    search_fields = ('entity_id', 'actor__email', 'note')
    date_hierarchy = 'timestamp'
