from rest_framework import serializers
from catalog.models import Tax

class TaxSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tax
        fields = ['id', 'name', 'rate_percent', 'type', 'is_active', 'applies_to']
