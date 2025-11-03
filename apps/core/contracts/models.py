from django.db import models
from django.core.exceptions import ValidationError

from apps.core.models import Tenant


CONTRACT_TYPES = [
    ("PHOTO", "Servicio Fotografía"),
    ("FRAME", "Enmarcado"),
    ("GRAD", "Graduaciones"),
    ("LASER", "Corte Láser"),
    ("EVENT", "Evento"),
    ("CUSTOM", "Personalizado"),
]

CONTRACT_STATUS = [
    ("DRAFT", "Borrador"),
    ("PENDING", "Pendiente Aprobación"),
    ("ACTIVE", "Activo"),
    ("SUSPENDED", "Suspendido"),
    ("COMPLETED", "Completado"),
    ("CANCELED", "Cancelado"),
]


class Contract(models.Model):
    tenant = models.ForeignKey(
        Tenant, on_delete=models.PROTECT, db_index=True, related_name="core_contracts"
    )
    # Integración con CRM si está instalado: FK opcional a crm.Client
    client = models.ForeignKey(
        "crm.Client",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="core_contracts",
    )
    # Snapshot defensivo si CRM no está activo o no se desea vincular
    client_name = models.CharField(max_length=120, blank=True)

    title = models.CharField(max_length=160)
    contract_type = models.CharField(max_length=12, choices=CONTRACT_TYPES)
    status = models.CharField(
        max_length=12, choices=CONTRACT_STATUS, default="DRAFT", db_index=True
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    details = models.TextField(blank=True)
    document = models.FileField(upload_to="contracts/", blank=True)
    external_ref = models.CharField(max_length=64, blank=True)

    class Meta:
        db_table = "core_contract"
        indexes = [
            models.Index(fields=["tenant", "status"]),
            models.Index(fields=["tenant", "contract_type"]),
        ]
        ordering = ["-start_date"]

    def clean(self):
        errors = {}
        if self.end_date and self.start_date and self.end_date < self.start_date:
            errors["end_date"] = "La fecha de fin no puede ser menor que la de inicio"
        if self.amount is None or self.amount < 0:
            errors["amount"] = "El monto debe ser 0 o mayor"
        # Requiere al menos una referencia de cliente
        if not self.client and not self.client_name:
            errors["client"] = "Debe especificarse un cliente (FK) o client_name"
        if errors:
            raise ValidationError(errors)

    def __str__(self):
        return f"{self.title} ({self.status})"