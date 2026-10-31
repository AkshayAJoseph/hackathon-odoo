from rest_framework import serializers
from plans.models import Plan, QuotationTemplate, TemplateLine

class PlanSerializer(serializers.ModelSerializer):
    price = serializers.DecimalField(max_digits=12, decimal_places=2, coerce_to_string=True)

    class Meta:
        model = Plan
        fields = [
            'id', 'name', 'price', 'billing_period', 'min_quantity',
            'available_from', 'available_to', 'auto_close', 'closable',
            'pausable', 'renewable', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate(self, attrs):
        available_from = attrs.get('available_from', getattr(self.instance, 'available_from', None))
        available_to = attrs.get('available_to', getattr(self.instance, 'available_to', None))
        if available_from and available_to and available_to < available_from:
            raise serializers.ValidationError({
                'available_to': ["available_to date must be greater than or equal to available_from date."]
            })
        return attrs


class TemplateLineSerializer(serializers.ModelSerializer):
    class Meta:
        model = TemplateLine
        fields = ['id', 'product', 'variant', 'quantity']


class QuotationTemplateSerializer(serializers.ModelSerializer):
    lines = TemplateLineSerializer(many=True, required=False)

    class Meta:
        model = QuotationTemplate
        fields = ['id', 'name', 'plan', 'validity_days', 'notes', 'lines', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def create(self, validated_data):
        lines_data = validated_data.pop('lines', [])
        template = QuotationTemplate.objects.create(**validated_data)
        for line_data in lines_data:
            TemplateLine.objects.create(template=template, **line_data)
        return template

    def update(self, instance, validated_data):
        lines_data = validated_data.pop('lines', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if lines_data is not None:
            instance.lines.all().delete()
            for line_data in lines_data:
                TemplateLine.objects.create(template=instance, **line_data)
        return instance

