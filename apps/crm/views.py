from rest_framework import viewsets, status
from rest_framework.decorators import action
from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from drf_spectacular.utils import (
    extend_schema,
    OpenApiResponse,
    OpenApiParameter,
)
from drf_spectacular.types import OpenApiTypes

from .models import Contract
from .serializers import ContractSerializer
from .services import ContractPDFService
from .permissions import ContractPermission


class ContractPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class ContractViewSet(viewsets.ModelViewSet):
    serializer_class = ContractSerializer
    pagination_class = ContractPagination
    permission_classes = [ContractPermission]

    def get_queryset(self):
        tenant = getattr(self.request, 'tenant', None)
        if not tenant:
            return Contract.objects.none()

        queryset = Contract.objects.filter(tenant=tenant)

        # Filtro por estado
        status_param = self.request.query_params.get('status')
        if status_param:
            queryset = queryset.filter(status=status_param)

        # Búsqueda por título
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(title__icontains=search)

        return queryset.order_by('-start_date')

    def perform_create(self, serializer):
        tenant = getattr(self.request, 'tenant', None)
        serializer.save(tenant=tenant)

    @extend_schema(
        operation_id='ContractDownload',
        description='Descarga el PDF generado del contrato.',
        parameters=[
            OpenApiParameter(name='id', description='ID de contrato', required=True, location=OpenApiParameter.PATH),
        ],
        responses={
            200: OpenApiResponse(response=OpenApiTypes.BINARY, description='PDF del contrato (application/pdf)'),
            500: OpenApiResponse(description='Error generando/descargando contrato'),
        },
        tags=['Contratos']
    )
    @action(detail=True, methods=['get'], url_path='download')
    def download(self, request, pk=None):
        """Genera y descarga el PDF del contrato en `contracts/`."""
        contract = self.get_object()
        service = ContractPDFService(request.tenant, request.user)
        try:
            filename = service.generate_contract(contract)
            # Entregar el archivo
            contract.document.open('rb')
            pdf_bytes = contract.document.read()
            contract.document.close()

            response = HttpResponse(pdf_bytes, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
        except Exception as e:
            return Response({'error': f'Error generando/descargando contrato: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)