from django.apps import AppConfig


class CoreContractsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.core.contracts"
    verbose_name = "Core • Contratos"

    def ready(self):
        # Registrar señales cuando existan
        try:
            from . import signals  # noqa: F401
        except Exception:
            # Evita fallos si aún no hay señales definidas
            pass