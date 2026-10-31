from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AuditLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action', models.CharField(blank=True, default='', max_length=100)),
                ('entity', models.CharField(db_index=True, max_length=100)),
                ('entity_id', models.CharField(db_index=True, max_length=100)),
                ('from_status', models.CharField(blank=True, default='', max_length=50)),
                ('to_status', models.CharField(blank=True, default='', max_length=50)),
                ('note', models.TextField(blank=True, default='')),
                ('timestamp', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('actor', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='audit_logs', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-timestamp'],
                'indexes': [
                    models.Index(fields=['entity', 'entity_id'], name='core_auditl_entity_d1c59f_idx'),
                    models.Index(fields=['timestamp'], name='core_auditl_timesta_80074f_idx'),
                ],
            },
        ),
    ]
