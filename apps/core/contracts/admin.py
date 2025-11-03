from django.contrib import admin, messages

from .models import Contract
from .services import ContractPDFService


@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = ("title", "contract_type", "status", "amount", "start_date", "tenant")
    list_filter = ("status", "contract_type", "tenant")
    search_fields = ("title",)
    exclude = ("tenant",)
    actions = ("generar_pdf",)

    def has_module_permission(self, request):
        return getattr(request.user, "is_active", False) and getattr(request.user, "is_staff", False)

    def get_model_perms(self, request):
        perms = super().get_model_perms(request)
        if getattr(request.user, "is_superuser", False) or getattr(request.user, "is_staff", False):
            perms["view"] = True
        return perms

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        tenant = getattr(request, "tenant", None) or getattr(request.user, "tenant", None)
        if tenant and not getattr(request.user, "is_superuser", False):
            qs = qs.filter(tenant=tenant)
        return qs.select_related("tenant")

    def save_model(self, request, obj, form, change):
        tenant = getattr(request, "tenant", None) or getattr(request.user, "tenant", None)
        if tenant and not obj.tenant_id:
            obj.tenant = tenant
        super().save_model(request, obj, form, change)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "client":
            tenant = getattr(request, "tenant", None) or getattr(request.user, "tenant", None)
            if tenant:
                try:
                    from apps.crm.models import Client

                    kwargs["queryset"] = Client.objects.filter(tenant=tenant)
                except Exception:
                    # Si CRM no está instalado, no filtrar
                    pass
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def generar_pdf(self, request, queryset):
        ok = 0
        for contract in queryset:
            try:
                service = ContractPDFService(contract.tenant, request.user)
                service.generate_contract(contract)
                ok += 1
            except Exception as e:
                self.message_user(
                    request,
                    f"Error generando PDF: {e}",
                    level=messages.ERROR,
                )
        if ok:
            self.message_user(
                request,
                f"Se generaron {ok} PDF(s).",
                level=messages.SUCCESS,
            )
    generar_pdf.short_description = "Generar PDF"