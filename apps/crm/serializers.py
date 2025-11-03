from rest_framework import serializers

from .models import Contract, Client


class ContractSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contract
        fields = [
            'id', 'tenant', 'client', 'title', 'contract_type',
            'start_date', 'end_date', 'amount', 'status', 'document'
        ]
        read_only_fields = ['tenant']

    def validate(self, attrs):
        start_date = attrs.get('start_date', getattr(self.instance, 'start_date', None))
        end_date = attrs.get('end_date', getattr(self.instance, 'end_date', None))
        amount = attrs.get('amount', getattr(self.instance, 'amount', None))

        errors = {}
        if end_date and start_date and end_date < start_date:
            errors['end_date'] = 'La fecha de término no puede ser anterior a la fecha de inicio.'
        if amount is not None and amount < 0:
            errors['amount'] = 'El monto no puede ser negativo.'

        # Validar que el client pertenezca al mismo tenant del request
        request = self.context.get('request')
        client = attrs.get('client', getattr(self.instance, 'client', None))
        if request and client:
            tenant = getattr(request, 'tenant', None)
            if tenant and client.tenant_id != tenant.id:
                errors['client'] = 'El cliente debe pertenecer al mismo tenant.'

        if errors:
            raise serializers.ValidationError(errors)
        return attrs

    # La asignación de `tenant` se realiza en la vista (`perform_create`) para estandarizar el flujo

    def update(self, instance, validated_data):
        # Asegurar que el tenant permanece igual
        validated_data.pop('tenant', None)
        return super().update(instance, validated_data)