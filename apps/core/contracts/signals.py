# Señales del módulo de contratos (placeholder para futuras integraciones)
from django.dispatch import receiver
from django.db.models.signals import post_save, pre_delete

from .models import Contract


@receiver(post_save, sender=Contract)
def contract_post_save(sender, instance, created, **kwargs):
    # Aquí se podrían emitir eventos a analytics/operations/finance
    # Mantener como placeholder para no romper compatibilidad
    return


@receiver(pre_delete, sender=Contract)
def contract_pre_delete(sender, instance, **kwargs):
    # Placeholder para limpieza previa a borrado
    return