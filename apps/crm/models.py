from django.db import models
from django.core.exceptions import ValidationError

from .constants import CONTRACT_STATUS_CHOICES


class Client(models.Model):
    tenant = models.ForeignKey('core.Tenant', on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100)
    tipo = models.CharField(max_length=20, choices=[
        ('Particular', 'Particular'),
        ('Colegio', 'Colegio'),
        ('Empresa', 'Empresa'),
    ])
    contacto = models.CharField(max_length=15)
    email = models.EmailField(blank=True)
    ie = models.CharField(max_length=100, blank=True)
    direccion = models.TextField(blank=True)
    detalles = models.TextField(blank=True)
    documento = models.CharField(max_length=20, blank=True)
    fecha_registro = models.DateField(auto_now_add=True)
    ultimo_pedido = models.DateField(null=True, blank=True)
    total_pedidos = models.IntegerField(default=0)
    monto_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        indexes = [
            models.Index(fields=['tenant']),
            models.Index(fields=['tenant', 'nombre']),
        ]
        unique_together = [('tenant', 'documento')]

    def __str__(self):
        return self.nombre


class Contract(models.Model):
    tenant = models.ForeignKey('core.Tenant', on_delete=models.CASCADE)
    client = models.ForeignKey('crm.Client', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    contract_type = models.CharField(max_length=50)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=CONTRACT_STATUS_CHOICES)
    document = models.FileField(upload_to='contracts/', blank=True)

    def clean(self):
        errors = {}
        if self.end_date and self.start_date and self.end_date < self.start_date:
            errors['end_date'] = 'La fecha de término no puede ser anterior a la fecha de inicio.'
        if self.amount is not None and self.amount < 0:
            errors['amount'] = 'El monto no puede ser negativo.'
        if errors:
            raise ValidationError(errors)

    class Meta:
        indexes = [
            models.Index(fields=['tenant']),
            models.Index(fields=['client']),
            models.Index(fields=['status']),
            models.Index(fields=['tenant', 'status']),
        ]
        ordering = ['-start_date']

    def __str__(self):
        return f"{self.title} ({self.status})"