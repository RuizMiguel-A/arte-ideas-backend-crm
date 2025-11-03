# Guía de Integración — Módulo CRM Contratos

## Requisitos previos
- Django 4.2+ y Django REST Framework.
- `drf-spectacular` instalado para anotaciones OpenAPI (opcional pero recomendado).
- `WeasyPrint` instalado con librerías externas requeridas para generación de PDF.
- Base de datos con migraciones aplicadas para `apps.core` (Tenant) y `apps.crm`.

## Estructura del módulo
- Modelos: `Client`, `Contract` con índices y `ordering` por `start_date`.
- Servicios: `ContractPDFService` para render y guardado de PDFs.
- Permisos: `ContractPermission` con mapa rol → acción (view/add/change/delete) y aislamiento por tenant.
- Señales: `contract_created`, `contract_updated`, `contract_deleted` emitidas por receptores `post_save` y `pre_delete`.
- Vistas: `ContractViewSet` con `get_queryset` aislado por `request.tenant`, `perform_create` asignando tenant y acción `download`.
- Rutas: router DRF en `apps/crm/urls.py` (`/contracts/`, `/contracts/{id}/download/`).

## Pasos de integración
1. Añadir `apps.crm` a `INSTALLED_APPS` (si no está) y asegurarse de `apps.crm.apps.CrmConfig` como AppConfig.
2. Configurar inyección de `request.tenant` en middleware o gateway API según tu multi‑tenancy.
3. Asegurar que los usuarios tengan un atributo `role` compatible con `ContractPermission` (p. ej., `admin`, `manager`, `employee`).
4. Exponer rutas del router: `path('api/crm/', include('apps.crm.urls'))` en `config/urls.py`.
5. (Opcional) Activar esquema de OpenAPI con `drf-spectacular` y revisar anotaciones del endpoint `download`.
6. Preparar entorno de `WeasyPrint` para que la generación de PDF funcione en producción.

## Interfaces y compatibilidad
- Entradas CRUD: `ContractSerializer` valida coherencia de fechas y monto; asegura que `client` pertenezca al mismo `tenant` del request.
- Descarga PDF: `GET /api/crm/contracts/{id}/download/` genera y retorna `application/pdf` con nombre dinámico.
- Permisos: acciones mapeadas por método HTTP; `download` tratado como `view`.
- Señales: oyentes externos pueden suscribirse a las señales del módulo sin acoplarse a otras apps.

## Consideraciones especiales
- `tenant` es de solo lectura en el serializer y se asigna en `perform_create`.
- Evitar regeneraciones de PDF masivas: el endpoint genera y guarda al vuelo; cachear si aplica.
- Asegurar `Client` y `Contract` pertenezcan al mismo tenant; el serializer valida y la view aísla queryset.

## Posibles conflictos y resolución
- Falta de `request.tenant`: las vistas retornan queryset vacío o validaciones fallan; configurar middleware de tenancy.
- Roles no mapeados: `ContractPermission` denegará acciones; añadir roles al mapa si es necesario.
- `WeasyPrint` sin dependencias: se lanzará error en generación; seguir documentación oficial para dependencias nativas.
- `STATICFILES_DIRS` inválido: ajustar ruta existente o remover directorio no usado.

## Ejemplos de configuración
- URLS: `path('api/crm/', include('apps.crm.urls'))`
- AppConfig: `default_app_config = 'apps.crm.apps.CrmConfig'` (si usas configuración antigua; en nuevas, basta con incluir `apps.crm`).
- Permisos: `permission_classes = [ContractPermission]` ya aplicado en la vista.