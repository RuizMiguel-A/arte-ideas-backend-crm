from io import BytesIO
from django.test import SimpleTestCase
from rest_framework.test import APIRequestFactory
from unittest.mock import patch

from apps.crm.views import ContractViewSet
from apps.crm.services import ContractPDFService


class DummyDocument:
    def __init__(self, content: bytes, name: str = 'dummy.pdf'):
        self._content = content
        self.name = name
        self._opened = False

    def open(self, mode='rb'):
        self._opened = True

    def read(self):
        if not self._opened:
            raise RuntimeError('File not opened')
        return self._content

    def close(self):
        self._opened = False


class DummyTenant:
    def __init__(self, name='Arte Ideas'):
        self.id = 1
        self.name = name


class DummyClient:
    def __init__(self, nombre='Cliente Prueba', email='cliente@example.com', contacto='123456789'):
        self.nombre = nombre
        self.email = email
        self.contacto = contacto


class DummyContract:
    def __init__(self, contract_id=1):
        self.id = contract_id
        self.title = 'Contrato Prueba'
        self.contract_type = 'Servicio'
        self.amount = 100
        self.status = 'Activo'
        self.start_date = '2025-01-01'
        self.end_date = None
        self.client = DummyClient()
        self.tenant = DummyTenant()
        self.document = DummyDocument(b'%PDF-1.4\n% dummy content')


class ContractDownloadActionTest(SimpleTestCase):
    def setUp(self):
        self.factory = APIRequestFactory()

    def test_download_returns_pdf_attachment(self):
        # Preparar request y vista
        request = self.factory.get('/api/crm/contracts/1/download/')
        request.tenant = DummyTenant()
        # Definir usuario con rol y tenant válidos para permisos
        class DummyUser:
            def __init__(self, role='admin', tenant=None):
                self.role = role
                self.tenant = tenant
                self.is_active = True

            @property
            def is_authenticated(self):
                return True

        request.user = DummyUser(role='admin', tenant=request.tenant)

        view = ContractViewSet.as_view({'get': 'download'})

        # Parchar get_object para devolver un contrato dummy
        with patch.object(ContractViewSet, 'get_object', return_value=DummyContract()):
            # Parchar el servicio para devolver nombre de archivo sin tocar storage real
            with patch.object(ContractPDFService, 'generate_contract', return_value='contrato_1_test.pdf'):
                response = view(request, pk=1)

        assert response.status_code == 200
        assert response['Content-Type'] == 'application/pdf'
        assert 'attachment; filename="contrato_1_test.pdf"' in response['Content-Disposition']
        # Contenido comienza con cabecera PDF
        assert response.content.startswith(b'%PDF')