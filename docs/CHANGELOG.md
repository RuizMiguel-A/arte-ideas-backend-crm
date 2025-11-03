# CHANGELOG — Módulo CRM Contratos

## [Unreleased]
- Estándar de creación: delegación de `tenant` a `perform_create` en vista.
- Señales internas para `Contract`: `contract_created`, `contract_updated`, `contract_deleted`.
- Anotación OpenAPI del endpoint de descarga con `drf-spectacular`.
- Pruebas de integración de señales y permisos negativos.

## [Day 5] - Señales y documentación OpenAPI
- Añadido `apps/crm/signals.py` con señales internas y receptores `post_save`/`pre_delete`.
- Registradas señales en `apps/crm/apps.py::CrmConfig.ready()` para evitar `AppRegistryNotReady`.
- Documentado endpoint `GET /api/crm/contracts/{id}/download/` usando `extend_schema`.
- Instalado `drf-spectacular` (documentación binaria en respuestas).
- Corregida redundancia: eliminado `create()` en serializer; `tenant` se asigna en la vista.
- Añadidas pruebas: `test_contract_signals.py` (create/update/delete) y `test_contract_permissions.py` (403 al eliminar con rol `employee`).

## [Day 4] - Permisos y aislamiento por tenant
- `apps/crm/permissions.py` con `ContractPermission` (roles → acciones y aislamiento por tenant).
- Integración en `ContractViewSet.permission_classes`.
- Ajuste de test de descarga con usuario/tenant válidos.

## [Day 3] - Exportación y descarga de contratos
- `ContractPDFService` (WeasyPrint) para generación y guardado de PDFs.
- Plantilla `templates/export/contract.html` con formato A4 y contenido del contrato.
- Acción `download` en `ContractViewSet`.
- Test de descarga creado y validado.

## Advertencias conocidas
- `WeasyPrint` requiere librerías externas en entorno local.
- `staticfiles.W004`: revisar ruta inexistente en `STATICFILES_DIRS`.