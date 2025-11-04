from django.contrib import admin
from .models import Activo, Financiamiento, Mantenimiento, Repuesto

# Register your models here.

@admin.register(Activo)
class ActivoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'costo_total', 'categoria', 'proveedor', 'fecha_compra', 'tipo_pago', 'vida_util', 'depreciacion_mensual', 'estado')

@admin.register(Financiamiento)
class FinanciamientoAdmin(admin.ModelAdmin):
    list_display = ('activo', 'monto_financiado' , 'entidad_financiera', 'tipo_pago', 'estado')

@admin.register(Mantenimiento)
class MantenimientoAdmin(admin.ModelAdmin):
    list_display = ('activo', 'proxima_fecha_mantenimiento', 'tipo_mantenimiento', 'fecha_mantenimiento', 'proveedor', 'costo', 'descripcion', 'estado_del_mantenimiento','estado_del_activo')

@admin.register(Repuesto)
class RepuestoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'categoria', 'ubicacion', 'proveedor', 'stock_actual', 'stock_minimo', 'costo_unitario', 'descripcion')
