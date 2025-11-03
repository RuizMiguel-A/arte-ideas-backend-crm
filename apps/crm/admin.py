from django.contrib import admin, messages
from django.http import HttpResponse

from .models import Client, Contract
from .services import ContractPDFService


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'tipo', 'contacto', 'email', 'tenant')
    list_filter = ('tipo', 'tenant')
    search_fields = ('nombre', 'email', 'contacto')
    readonly_fields = ()
    exclude = ('tenant',)

    # Asegura que el módulo CRM sea visible en el índice del admin
    def has_module_permission(self, request):
        return getattr(request.user, 'is_active', False) and getattr(request.user, 'is_staff', False)

    def get_model_perms(self, request):
        perms = super().get_model_perms(request)
        # Para superusuarios y staff, permitir al menos vista para mostrar el módulo
        if getattr(request.user, 'is_superuser', False) or getattr(request.user, 'is_staff', False):
            perms['view'] = True
        return perms

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        tenant = getattr(request.user, 'tenant', None)
        if not getattr(request.user, 'is_superuser', False) and tenant:
            qs = qs.filter(tenant=tenant)
        return qs.select_related('tenant')

    def save_model(self, request, obj, form, change):
        if not change and getattr(request.user, 'tenant', None) and not obj.tenant_id:
            obj.tenant = request.user.tenant
        super().save_model(request, obj, form, change)


@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = ('title', 'client', 'status', 'amount', 'start_date', 'tenant')
    list_filter = ('status', 'contract_type', 'tenant')
    search_fields = ('title', 'client__nombre')
    actions = ('generar_pdf', 'descargar_pdf')
    exclude = ('tenant',)

    # Asegura que el módulo CRM sea visible en el índice del admin
    def has_module_permission(self, request):
        return getattr(request.user, 'is_active', False) and getattr(request.user, 'is_staff', False)

    def get_model_perms(self, request):
        perms = super().get_model_perms(request)
        # Para superusuarios y staff, permitir al menos vista para mostrar el módulo
        if getattr(request.user, 'is_superuser', False) or getattr(request.user, 'is_staff', False):
            perms['view'] = True
        return perms

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        tenant = getattr(request.user, 'tenant', None)
        if not getattr(request.user, 'is_superuser', False) and tenant:
            qs = qs.filter(tenant=tenant)
        return qs.select_related('tenant', 'client')

    def save_model(self, request, obj, form, change):
        if not change and getattr(request.user, 'tenant', None) and not obj.tenant_id:
            obj.tenant = request.user.tenant
        super().save_model(request, obj, form, change)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'client':
            tenant = getattr(request.user, 'tenant', None)
            if tenant:
                kwargs['queryset'] = Client.objects.filter(tenant=tenant)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def generar_pdf(self, request, queryset):
        count = 0
        for contract in queryset:
            try:
                service = ContractPDFService(contract.tenant, request.user)
                service.generate_contract(contract)
                count += 1
            except Exception as e:
                self.message_user(request, f'Error generando PDF para contrato {contract.id}: {e}', level=messages.ERROR)
        if count:
            self.message_user(request, f'Se generaron {count} PDF(s) de contrato.', level=messages.SUCCESS)
    generar_pdf.short_description = 'Generar PDF del contrato'

    def descargar_pdf(self, request, queryset):
        if queryset.count() != 1:
            self.message_user(request, 'Selecciona un único contrato para descargar el PDF.', level=messages.WARNING)
            return None
        contract = queryset.first()

        filename = None
        try:
            if not contract.document:
                service = ContractPDFService(contract.tenant, request.user)
                filename = service.generate_contract(contract)
            else:
                # Usar el nombre existente del archivo
                filename = contract.document.name.split('/')[-1]

            contract.document.open('rb')
            pdf_bytes = contract.document.read()
            contract.document.close()

            response = HttpResponse(pdf_bytes, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
        except Exception as e:
            self.message_user(request, f'Error descargando PDF: {e}', level=messages.ERROR)
            return None
    descargar_pdf.short_description = 'Descargar PDF del contrato'