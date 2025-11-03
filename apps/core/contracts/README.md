# Core • Contratos

Este módulo implementa la gestión de contratos dentro de `apps/core/contracts`, alineado con la guía de arquitectura (Guía-Core.md).

## Estructura
- `apps.py`: configuración de la app.
- `models.py`: modelo `Contract` con aislamiento multi-tenant y compatibilidad opcional con `crm.Client`.
- `admin.py`: registro en el admin, autoasignación de `tenant`, filtrado por `tenant`, acción de generación de PDF.
- `services.py`: `ContractPDFService` con import perezoso de WeasyPrint.
- `signals.py`: placeholders para integraciones (analytics/operations/finance).
- `migrations/`: migraciones de la app.
- `templates/export/contract.html`: plantilla para render del PDF.
- `tests/test_admin.py`: pruebas básicas de admin.

## Compatibilidad
- No se modifica `apps/crm` ni sus modelos. Para evitar colisiones de reverse accessor, `Contract.tenant` y `Contract.client` usan `related_name="core_contracts"`.
- Si `apps.crm` está instalado, el campo `client` (FK a `crm.Client`) está disponible; en su ausencia puede usarse `client_name` como snapshot.
- `TenantMiddleware` se usa para autoasignación y filtros de `tenant`.

## Configuración
- Añadir en `INSTALLED_APPS`: `apps.core.contracts`.
- Las dependencias de WeasyPrint en Windows pueden generar advertencias; el servicio usa import perezoso para no romper migraciones/arranque.

## Pruebas
- Ejecutar: `python manage.py test apps.core.contracts`.

## Pendientes futuros
- Endpoints DRF (`serializers.py`, `views.py`, `urls.py`) si se requiere API.
- Señales y hooks a `finance`, `operations`, `analytics`.