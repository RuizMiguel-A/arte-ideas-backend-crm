# 🗂️ Plan de Desarrollo del Módulo de Contratos (CRM) – Arte Ideas

Este plan define, en un máximo de 5 pasos, la implementación del módulo de contratos del backend de Arte Ideas, alineado estrictamente con la documentación ubicada en `docs/` y con la arquitectura definida (multi-tenancy, permisos por módulo, compatibilidad con frontend React). El alcance se limita exclusivamente al módulo de contratos en la app CRM, sin modificar otras carpetas ni funcionalidades de otros módulos.

---

## Alcance y Alineación
- Módulo: `CRM` → Entidad `Contract` y sus APIs relacionadas.
- Estructura objetivo (según documentación):
  - `apps/crm/models.py`
  - `apps/crm/serializers.py`
  - `apps/crm/views.py`
  - `apps/crm/urls.py`
  - `apps/crm/permissions.py`
  - `apps/crm/services.py` (incluye `ContractPDFService`)
- Endpoints esperados (compatibles con frontend):
  - `GET/POST /api/contracts/`
  - `GET/PUT/DELETE /api/contracts/{id}/`
  - `GET /api/contracts/{id}/download/`
- Alineación con documentación relevante:
  - Modelos y endpoints: `docs/aplicaciones-backend.md`
  - Compatibilidad frontend: `docs/compatibilidad-frontend.md`
  - Permisos y roles: `docs/especificaciones-tecnicas.md` (SYSTEM_ROLES, MODULE_PERMISSIONS)
  - Multi-tenancy: `docs/sistema-multi-tenancy.md` (TenantMiddleware, `tenant` por recurso)
  - Exportación/PDF: `docs/sistema-exportacion.md` (`generate_contract`, rutas y guardado en `contracts/`)

---

## Dependencias y Consideraciones
- Dependencias mínimas: `apps.core` (Tenant, User, TenantMiddleware). Se asume el `request.tenant` provisto por middleware.
- Integración futura (sin modificar otros módulos ahora):
  - `Commerce.Order` usa `contrato_id` (véase compatibilidad frontend). El contrato debe exponer un identificador estable.
  - `Analytics` contempla el tipo `contract` en notificaciones; se dejarán hooks internos sin activar integración externa.
- Convenciones: Django + DRF, ViewSets, filtros/paginación estándar, nombres de campos conforme a documentación (`title`, `contract_type`, `start_date`, `end_date`, `amount`, `status`, `document`).

---

## Plan Secuencial (5 pasos)

### Paso 1 — Modelo y Esquema de Datos
- Objetivos específicos
  - Definir el modelo `Contract` conforme a `docs/aplicaciones-backend.md` con soporte multi-tenant.
  - Establecer `CONTRACT_STATUS_CHOICES` según las necesidades del frontend (documentación y estados de negocio).
  - Asegurar integridad relacional con `crm.Client` y aislamiento por `tenant`.
- Tareas técnicas detalladas
  - Crear `apps/crm/models.py` con `Contract(tenant, client, title, contract_type, start_date, end_date, amount, status, document)`.
  - Declarar `CONTRACT_STATUS_CHOICES` en `apps/crm/constants.py` o dentro del modelo (según convenciones internas).
  - Definir validaciones: rango de fechas (`start_date <= end_date` si aplica), `amount >= 0`, obligatoriedad de `client` y `tenant`.
  - Añadir `Meta` con índices por `tenant` y campos de consulta frecuentes (`status`, `client`).
  - Generar migraciones de `crm` (sin cambios fuera de la app `crm`).
- Entregables esperados
  - `apps/crm/models.py` con `Contract` y constantes de estado.
  - Migraciones creadas para `crm`.
- Criterios de validación
  - `makemigrations` y `migrate` aplican sin errores para la app `crm`.
  - Creación/lectura de instancias `Contract` respetando `tenant`.

### Paso 2 — Serializadores y API CRUD
- Objetivos específicos
  - Exponer CRUD de contratos vía DRF con `ModelViewSet` y serializer validando reglas de negocio.
  - Filtrar automáticamente por `tenant` en consultas y escritura.
- Tareas técnicas detalladas
  - Crear `apps/crm/serializers.py` con `ContractSerializer` (validaciones de fechas y montos, campos requeridos).
  - Crear `apps/crm/views.py` con `ContractViewSet` (filtro por `request.tenant`, búsqueda por `title`, filtrado por `status`, paginación).
  - Crear `apps/crm/urls.py` registrando el router `contracts` y dejando listo el `include` para `config/urls.py` (sin modificar `config`).
- Entregables esperados
  - `ContractSerializer`, `ContractViewSet`, rutas internas en `crm/urls.py`.
- Criterios de validación
  - `GET/POST /api/contracts/` y `GET/PUT/DELETE /api/contracts/{id}/` responden según esquema de datos documentado.
  - Paginación, filtros y búsqueda operativos; resultados siempre limitados al `tenant` activo.

### Paso 3 — Servicio de PDF y Descarga
- Objetivos específicos
  - Implementar generación de PDF del contrato y endpoint de descarga, alineados con `docs/sistema-exportacion.md`.
- Tareas técnicas detalladas
  - Crear `apps/crm/services.py` con `ContractPDFService.generate_contract(contract)` que use plantilla `contract` y guarde archivo en `contracts/`.
  - Extender `apps/crm/views.py` con `ContractDownloadView` (`GET /api/contracts/{id}/download/`) que entregue el PDF.
  - Plantilla HTML base en `apps/crm/templates/export/contract.html` (ubicación interna a `crm`; sin modificar otras apps).
- Entregables esperados
  - Servicio de exportación de contrato y vista de descarga.
- Criterios de validación
  - Descargar PDF retorna `200 OK`, tipo `application/pdf` y archivo guardado en `contracts/`.
  - Re-generación/actualización del documento funciona según modificaciones del contrato.

### Paso 4 — Permisos y Multi‑tenancy
- Objetivos específicos
  - Aplicar permisos granulares del módulo `contracts` y garantizar aislamiento por `tenant`.
- Tareas técnicas detalladas
  - Crear `apps/crm/permissions.py` con permiso `ContractPermission` apoyado en `MODULE_PERMISSIONS['contracts']` y roles definidos en `SYSTEM_ROLES`.
  - Configurar `permission_classes` en vistas para respetar `view/add/change/delete` por rol.
  - Implementar `get_queryset()` con filtro por `request.tenant`; en creación, setear `tenant` automáticamente.
- Entregables esperados
  - Permisos operativos a nivel de módulo y vistas con enforcement.
- Criterios de validación
  - Usuarios sin permiso no acceden al recurso ni a acciones restringidas.
  - Un usuario de un `tenant` no ve/edita contratos de otro `tenant`.

### Paso 5 — Integración y Extensibilidad (sin modificar otras apps)
- Objetivos específicos
  - Diseñar el módulo listo para integrarse con `Commerce` (uso de `contrato_id`) y `Analytics` (eventos `contract`) sin cambios externos por ahora.
- Tareas técnicas detalladas
  - Exponer identificadores y campos necesarios para referencia externa (`id`, `client`, `status`, `amount`).
  - Definir hooks internos (p.ej. señales `post_save` en `apps/crm/signals.py`) documentados, sin activar integraciones fuera de `crm`.
  - Documentar contratos de API y esquemas para `drf-spectacular` (dentro de `crm`).
- Entregables esperados
  - Señales internas documentadas, endpoints y esquemas listos para consumo.
- Criterios de validación
  - El módulo publica información suficiente para que otras apps se integren en fases posteriores.
  - No se han tocado carpetas ni funcionalidades fuera de `crm`.

---

## Criterios Globales de Calidad
- Cumplimiento estricto de documentación: modelos, endpoints, permisos y multi‑tenancy.
- Compatibilidad con frontend React: rutas y campos esperados, descarga de contrato.
- Aislamiento por módulo: ningún cambio fuera de `apps/crm/` y su documentación.
- Tests mínimos del módulo: serializer, viewset CRUD, descarga PDF, permisos y tenant scoping.

## Entregables Finales del Módulo
- Código: `apps/crm/*.py` (models, serializers, views, urls, permissions, services, signals) y plantilla `templates/export/contract.html` bajo `crm`.
- Documentación: este plan y comentarios de API para generación de OpenAPI dentro del módulo.
- Artefactos: contratos PDF generados en `contracts/`.

---

## Validación del Plan
- Revisión formal contra: `aplicaciones-backend.md`, `compatibilidad-frontend.md`, `especificaciones-tecnicas.md`, `sistema-exportacion.md`, `sistema-multi-tenancy.md`.
- Check de que el plan no afecta otras apps ni `config/`.
- Verificación de que los endpoints y estructuras coinciden con las expectativas del frontend y permisos definidos.