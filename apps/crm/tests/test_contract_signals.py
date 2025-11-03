from django.test import TestCase
from django.dispatch import receiver

from apps.core.models import Tenant
from apps.crm.models import Client, Contract
from apps.crm import signals as crm_signals


class ContractSignalsTest(TestCase):
    def setUp(self):
        self.tenant = Tenant.objects.create(name='Tenant Test', subdomain='tenant-test')
        self.client = Client.objects.create(
            tenant=self.tenant,
            nombre='Cliente Señales',
            tipo='Empresa',
            contacto='123456789',
            email='cliente@senales.com',
        )

        # Contadores para eventos
        self.created_events = []
        self.updated_events = []
        self.deleted_events = []

        # Conectar listeners temporales
        crm_signals.contract_created.connect(self._on_created, dispatch_uid='test_contract_created')
        crm_signals.contract_updated.connect(self._on_updated, dispatch_uid='test_contract_updated')
        crm_signals.contract_deleted.connect(self._on_deleted, dispatch_uid='test_contract_deleted')

    def tearDown(self):
        crm_signals.contract_created.disconnect(self._on_created, dispatch_uid='test_contract_created')
        crm_signals.contract_updated.disconnect(self._on_updated, dispatch_uid='test_contract_updated')
        crm_signals.contract_deleted.disconnect(self._on_deleted, dispatch_uid='test_contract_deleted')

    def _on_created(self, sender, **kwargs):
        self.created_events.append(kwargs)

    def _on_updated(self, sender, **kwargs):
        self.updated_events.append(kwargs)

    def _on_deleted(self, sender, **kwargs):
        self.deleted_events.append(kwargs)

    def test_signals_emitted_on_create_update_delete(self):
        # Crear contrato -> debe emitir contract_created
        contract = Contract.objects.create(
            tenant=self.tenant,
            client=self.client,
            title='Contrato Señales',
            contract_type='Servicio',
            start_date='2025-01-01',
            amount=100,
            status='Activo',
        )
        assert len(self.created_events) == 1
        assert self.created_events[0]['contract'].id == contract.id
        assert self.created_events[0]['tenant'].id == self.tenant.id

        # Actualizar contrato -> debe emitir contract_updated
        contract.title = 'Contrato Señales Editado'
        contract.save(update_fields=['title'])
        assert len(self.updated_events) == 1
        assert self.updated_events[0]['contract'].title == 'Contrato Señales Editado'
        assert self.updated_events[0]['tenant'].id == self.tenant.id
        update_fields = self.updated_events[0].get('update_fields')
        assert update_fields is not None and ('title' in update_fields)

        # Eliminar contrato -> debe emitir contract_deleted
        contract.delete()
        assert len(self.deleted_events) == 1
        assert self.deleted_events[0]['contract'].title == 'Contrato Señales Editado'
        assert self.deleted_events[0]['tenant'].id == self.tenant.id