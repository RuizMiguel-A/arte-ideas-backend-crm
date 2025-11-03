from django.test import SimpleTestCase
from rest_framework.test import APIRequestFactory
from unittest.mock import patch

from apps.crm.views import ContractViewSet


class DummyTenant:
    def __init__(self, id=1, name='Tenant Perms'):
        self.id = id
        self.name = name


class DummyUser:
    def __init__(self, role='employee', tenant=None):
        self.role = role
        self.tenant = tenant
        self.is_active = True

    @property
    def is_authenticated(self):
        return True


class DummyContract:
    def __init__(self, tenant=None):
        self.tenant = tenant or DummyTenant()


class ContractPermissionsTest(SimpleTestCase):
    def setUp(self):
        self.factory = APIRequestFactory()

    def test_employee_role_cannot_delete_contract(self):
        request = self.factory.delete('/api/crm/contracts/1/')
        request.tenant = DummyTenant()
        request.user = DummyUser(role='employee', tenant=request.tenant)

        view = ContractViewSet.as_view({'delete': 'destroy'})

        with patch.object(ContractViewSet, 'get_object', return_value=DummyContract(tenant=request.tenant)):
            response = view(request, pk=1)

        # DRF debe responder 403 Forbidden por falta de permiso 'delete'
        assert response.status_code == 403