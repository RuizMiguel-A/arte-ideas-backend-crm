from django.contrib import admin

from .models import Tenant


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ("name", "subdomain", "is_active", "created_at")
    search_fields = ("name", "subdomain")
    list_filter = ("is_active",)
    readonly_fields = ("created_at",)

##Pasos para resolverlo ahora

##- Entra a “Core” → “Tenants” y crea uno, por ejemplo:
##- name: Arte Ideas
##- subdomain: arteideas
##- is_active: marcado
    