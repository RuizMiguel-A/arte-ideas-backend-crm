from django.db import models


class Tenant(models.Model):
    name = models.CharField(max_length=100)
    subdomain = models.CharField(max_length=50, unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    settings = models.JSONField(default=dict)

    # Configuración específica por tenant
    max_users = models.IntegerField(default=10)
    max_storage_mb = models.IntegerField(default=1000)
    features_enabled = models.JSONField(default=dict)

    def __str__(self):
        return f"{self.name} ({self.subdomain})"

    class Meta:
        indexes = [
            models.Index(fields=["subdomain"]),
            models.Index(fields=["is_active"]),
        ]