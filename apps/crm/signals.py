from django.dispatch import Signal, receiver
from django.db.models.signals import post_save, pre_delete
import logging

from .models import Contract


logger = logging.getLogger(__name__)

# Señales internas del módulo CRM (contratos)
# No acoplan otras apps; sirven para extender integraciones sin modificar este módulo.
contract_created = Signal()
contract_updated = Signal()
contract_deleted = Signal()


@receiver(post_save, sender=Contract)
def emit_contract_events(sender, instance: Contract, created: bool, **kwargs):
    """Emite señales internas al crear/actualizar contratos.

    - Aísla por tenant porque el `instance` ya contiene `tenant`.
    - No realiza efectos secundarios; solo notifica.
    """
    try:
        if created:
            logger.info("Contrato creado: id=%s tenant=%s", instance.id, getattr(instance.tenant, 'id', None))
            contract_created.send(sender=sender, contract=instance, tenant=instance.tenant)
        else:
            logger.info("Contrato actualizado: id=%s tenant=%s", instance.id, getattr(instance.tenant, 'id', None))
            contract_updated.send(sender=sender, contract=instance, tenant=instance.tenant, update_fields=kwargs.get('update_fields'))
    except Exception as e:
        # Nunca bloquear flujo de guardado por fallos de listeners
        logger.warning("Fallo emitiendo señal de contrato: %s", e)


@receiver(pre_delete, sender=Contract)
def emit_contract_deleted(sender, instance: Contract, **kwargs):
    try:
        logger.info("Contrato eliminado: id=%s tenant=%s", instance.id, getattr(instance.tenant, 'id', None))
        contract_deleted.send(sender=sender, contract=instance, tenant=instance.tenant)
    except Exception as e:
        logger.warning("Fallo emitiendo señal de contrato eliminado: %s", e)