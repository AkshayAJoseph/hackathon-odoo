from django.db import models
from django.conf import settings

class AuditLog(models.Model):
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs'
    )
    action = models.CharField(max_length=100, blank=True, default='')
    entity = models.CharField(max_length=100, db_index=True)
    entity_id = models.CharField(max_length=100, db_index=True)
    from_status = models.CharField(max_length=50, blank=True)
    to_status = models.CharField(max_length=50, blank=True)
    note = models.TextField(blank=True, default='')
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['entity', 'entity_id']),
            models.Index(fields=['timestamp']),
        ]

    def __str__(self):
        actor_name = getattr(self.actor, 'email', str(self.actor)) if self.actor else 'system'
        action_str = f" - {self.action}" if self.action else ""
        return f"{self.entity} ({self.entity_id}){action_str}: {self.from_status} -> {self.to_status} by {actor_name}"
