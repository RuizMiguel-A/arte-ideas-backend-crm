# Documento Técnico: Módulo de Contratos en apps/core
Este documento define requerimientos, arquitectura y un plan de implementación para un módulo de Contratos ubicado dentro de apps/core , manteniendo consistencia con el estilo y convenciones del proyecto actual (Django 4.2, multi‑tenant con TenantMiddleware , admin y DRF cuando aplique).

## 1. Requisitos Funcionales
- Tipos de contratos a manejar
  
  - Servicio Fotografía ( PHOTO )
  - Enmarcado ( FRAME )
  - Graduaciones ( GRAD )
  - Corte Láser ( LASER )
  - Evento ( EVENT )
  - Personalizado ( CUSTOM )
  - Extensibles mediante configuración ( features_enabled del Tenant ).
- Campos obligatorios y opcionales por contrato
  
  - Obligatorios:
    - tenant (aislamiento multi‑tenant)
    - title (título descriptivo)
    - contract_type (uno de los tipos definidos)
    - client (si apps.crm está instalado, FK a crm.Client ; si no, almacenar referencia textual)
    - status ( DRAFT , PENDING , ACTIVE , SUSPENDED , COMPLETED , CANCELED )
    - start_date (fecha inicio)
    - amount (monto total, >= 0 )
  - Opcionales:
    - end_date (fecha fin)
    - details (texto libre o JSON para cláusulas)
    - document (archivo PDF generado)
    - external_ref (referencia a sistemas externos, p. ej. commerce.Order )
- Flujos de aprobación y estados del contrato
  
  - Flujo base:
    - DRAFT → edición libre.
    - PENDING → requiere aprobación (rol ADMIN / MANAGER ).
    - ACTIVE → contrato vigente.
    - SUSPENDED → contrato en pausa por incidencia.
    - COMPLETED → finalizado, bloquea edición de campos críticos.
    - CANCELED → cancelado, bloquea edición completa salvo anotaciones internas.
  - Reglas:
    - Solo usuarios con permisos de change pueden transicionar a PENDING y aprobar a ACTIVE .
    - Generación/descarga de PDF permitida en PENDING , ACTIVE , COMPLETED .
- Integración con otros módulos existentes
  
  - crm.Client : asociación de contrato a cliente; filtrado por tenant .
  - finance : futura contabilización del contrato (hooks internos documentados).
  - operations : avance de trabajo relacionado (eventos/ señales internas).
  - commerce : pedidos vinculados ( external_ref o campo dedicado).
  - analytics : eventos de ciclo de vida (señales post_save y pre_delete ).
## 2. Requisitos Técnicos
- Arquitectura del módulo dentro de apps/core
  
  - Sub‑módulo apps/core/contracts como “app” de Django (con AppConfig propio) para permitir migraciones aisladas y activación en INSTALLED_APPS .
  - Aislamiento por tenant :
    - TenantMiddleware (ya activo) inyecta request.tenant .
    - Índices por tenant , status y client para rendimiento.
  - Permisos:
    - Mapa rol → acción compatible con SYSTEM_ROLES / MODULE_PERMISSIONS , aplicado en admin y vistas.
- Tecnologías y frameworks a utilizar
  
  - Django 4.2 (Modelos, Admin, Migraciones).
  - Django REST Framework (opcional, si se exponen API internas): ModelViewSet , filtros/paginación.
  - WeasyPrint para generación de PDF (consistencia con el entorno actual).
  - Plantillas Django para render de contrato ( templates/export/contract.html ).
- Estructura de carpetas y archivos
  
  - apps/core/contracts/
    - apps.py ( CoreContractsConfig )
    - models.py ( Contract , constantes de estado/tipo)
    - admin.py (registro y acciones de PDF)
    - services.py ( ContractPDFService , utilidades)
    - permissions.py (mapa rol → permisos contrato)
    - serializers.py (si se usa DRF)
    - views.py (si se expone API)
    - urls.py (router DRF opcional)
    - signals.py (eventos internos post‑save/pre‑delete)
    - migrations/ (migraciones de la app)
    - templates/export/contract.html (plantilla PDF)
  - Ajustes en config/settings.py :
    - Activar apps.core.contracts en INSTALLED_APPS .
    - Mantener apps.core.middleware.TenantMiddleware en MIDDLEWARE .
- Requisitos de compatibilidad con la rama actual
  
  - Respetar autoasignación de tenant desde admin/requests.
  - Preservar warnings conocidos (WeasyPrint y staticfiles.W004 ) sin impactar funcionamiento.
  - No romper dependencias existentes; crm integración condicional (detectar app instalada).
## 3. Pasos de Implementación
- Configuración inicial del módulo
  
  - Crear paquete apps/core/contracts con AppConfig :
    ```
    # apps/core/contracts/apps.py
    from django.apps import 
    AppConfig
    
    class CoreContractsConfig
    (AppConfig):
        default_auto_field = 
        'django.db.models.
        BigAutoField'
        name = 'apps.core.
        contracts'
        verbose_name = 'Core • 
        Contratos'
    
        def ready(self):
            from . import signals  
            # registra señales
    ```
  - Añadir a INSTALLED_APPS :
    ```
    INSTALLED_APPS = [
      # ...
      'apps.core.contracts',
    ]
    ```
- Desarrollo de entidades y modelos
  
  ```
  # apps/core/contracts/models.py
  from django.db import models
  from apps.core.models import 
  Tenant
  
  CONTRACT_TYPES = [
      ('PHOTO', 'Servicio 
      Fotografía'),
      ('FRAME', 'Enmarcado'),
      ('GRAD', 'Graduaciones'),
      ('LASER', 'Corte Láser'),
      ('EVENT', 'Evento'),
      ('CUSTOM', 'Personalizado'),
  ]
  
  CONTRACT_STATUS = [
      ('DRAFT', 'Borrador'),
      ('PENDING', 'Pendiente 
      Aprobación'),
      ('ACTIVE', 'Activo'),
      ('SUSPENDED', 'Suspendido'),
      ('COMPLETED', 'Completado'),
      ('CANCELED', 'Cancelado'),
  ]
  
  class Contract(models.Model):
      tenant = models.ForeignKey
      (Tenant, on_delete=models.
      PROTECT, db_index=True)
      # Si crm.Client está 
      disponible:
      # from apps.crm.models 
      import Client
      # client = models.ForeignKey
      (Client, on_delete=models.
      PROTECT)
      # Alternativa defensiva si 
      CRM no está activo:
      client_name = models.
      CharField(max_length=120, 
      blank=True)  # snapshot
      title = models.CharField
      (max_length=160)
      contract_type = models.
      CharField(max_length=12, 
      choices=CONTRACT_TYPES)
      status = models.CharField
      (max_length=12, 
      choices=CONTRACT_STATUS, 
      default='DRAFT', 
      db_index=True)
      amount = models.DecimalField
      (max_digits=12, 
      decimal_places=2)
      start_date = models.DateField
      ()
      end_date = models.DateField
      (null=True, blank=True)
      details = models.TextField
      (blank=True)
      document = models.FileField
      (upload_to='contracts/', 
      blank=True)
  
      external_ref = models.
      CharField(max_length=64, 
      blank=True)
  
      class Meta:
          db_table = 
          'core_contract'
          indexes = [models.Index
          (fields=['tenant', 
          'status']), models.Index
          (fields=['tenant', 
          'contract_type'])]
          ordering = 
          ['-start_date']
  
      def clean(self):
          if self.end_date and 
          self.end_date < self.
          start_date:
              raise ValueError('La 
              fecha de fin no 
              puede ser menor que 
              la de inicio')
          if self.amount is None 
          or self.amount < 0:
              raise ValueError('El 
              monto debe ser 0 o 
              mayor')
  ```
- Implementación de servicios y controladores
  
  ```
  # apps/core/contracts/services.py
  from django.template.loader 
  import render_to_string
  from weasyprint import HTML
  
  class ContractPDFService:
      def __init__(self, tenant, 
      user):
          self.tenant = tenant
          self.user = user
  
      def generate_contract(self, 
      contract):
          html = render_to_string
          ('export/contract.html', 
          {'contract': contract, 
          'tenant': self.tenant})
          pdf = HTML(string=html).
          write_pdf()
          filename = f'{contract.
          id}-{contract.title}.pdf'
          contract.document.save
          (filename, content=bytes
          (pdf))
          return filename
  ```
  ```
  # apps/core/contracts/admin.py
  from django.contrib import 
  admin, messages
  from .models import Contract
  from .services import 
  ContractPDFService
  
  @admin.register(Contract)
  class ContractAdmin(admin.
  ModelAdmin):
      list_display = ('title', 
      'contract_type', 'status', 
      'amount', 'start_date', 
      'tenant')
      list_filter = ('status', 
      'contract_type', 'tenant')
      search_fields = ('title',)
      exclude = ('tenant',)
  
      def save_model(self, 
      request, obj, form, change):
          tenant = getattr
          (request, 'tenant', 
          None) or getattr(request.
          user, 'tenant', None)
          if tenant and not obj.
          tenant_id:
              obj.tenant = tenant
          super().save_model
          (request, obj, form, 
          change)
  
      def get_queryset(self, 
      request):
          qs = super().get_queryset
          (request)
          tenant = getattr
          (request, 'tenant', 
          None) or getattr(request.
          user, 'tenant', None)
          if tenant and not getattr
          (request.user, 
          'is_superuser', False):
              qs = qs.filter
              (tenant=tenant)
          return qs.select_related
          ('tenant')
  
      def generar_pdf(self, 
      request, queryset):
          ok = 0
          for contract in queryset:
              try:
                  service = 
                  ContractPDFServic
                  e(contract.
                  tenant, request.
                  user)
                  service.
                  generate_contract
                  (contract)
                  ok += 1
              except Exception as 
              e:
                  self.message_user
                  (request, 
                  f'Error 
                  generando PDF: 
                  {e}', 
                  level=messages.
                  ERROR)
          if ok:
              self.message_user
              (request, f'Se 
              generaron {ok} PDF
              (s).', 
              level=messages.
              SUCCESS)
      generar_pdf.
      short_description = 'Generar 
      PDF'
  
      actions = ('generar_pdf',)
  ```
- Creación de migraciones de base de datos
  
  - python manage.py makemigrations core.contracts
  - python manage.py migrate
  - Orden recomendado:
    - core.0001_initial (Tenant)
    - core.contracts.0001_initial (Contract)
- Desarrollo de interfaces de usuario
  
  - Admin:
    - Formularios sin campo tenant visible (autoasignación).
    - Listados filtrados por tenant .
    - Acción de generar PDF.
  - API (opcional, si se requiere):
    - GET/POST /api/core/contracts/ (DRF ModelViewSet )
    - GET /api/core/contracts/{id}/download/ (descarga binaria)
    - Filtro por status , búsqueda por title , paginación estándar.
    - Aislamiento por request.tenant en get_queryset y perform_create .
## 4. Criterios de Aceptación
- Pruebas unitarias y de integración requeridas
  
  - Modelos:
    - Validación de fechas y montos.
    - Índices y ordering .
  - Admin:
    - Autoasignación de tenant en save_model .
    - Filtro de queryset por tenant .
    - Acción de PDF que guarda archivo.
  - API (si procede):
    - POST crea contrato con tenant del request.
    - GET lista únicamente contratos del tenant.
    - download retorna binario PDF.
  - Multi‑tenant:
    - Usuario de un tenant no ve/edita contratos de otro.
- Documentación técnica a entregar
  
  - Descripción de modelos, permisos, endpoints (si aplica DRF).
  - Guía de despliegue con dependencia de WeasyPrint (Windows).
  - Explicación de TenantMiddleware y uso de request.tenant .
- Requisitos de rendimiento y seguridad
  
  - Índices por tenant , status , contract_type .
  - select_related('tenant') para admin.
  - Validaciones en clean() y restricciones en transiciones de estado (hooks/señales).
  - Control de acceso por rol y módulo (mapa de permisos).
- Validación con stakeholders
  
  - Revisión de estados/flujo de aprobación.
  - Confirmación de campos y tipos de contrato.
  - Validación de interfaz admin y (si aplica) endpoints.
## 5. Entregables
- Código fuente del módulo
  
  - apps/core/contracts/* (models, admin, services, signals, migrations, templates).
  - Ajustes mínimos en config/settings.py ( INSTALLED_APPS ).
  - Opcional: serializers.py , views.py , urls.py si se expone API.
- Documentación técnica completa
  
  - Esquemas de datos, flujos de estado, permisos y endpoints.
  - Instrucciones de instalación de WeasyPrint y configuración de static .
- Scripts de implementación
  
  - Migraciones ( makemigrations , migrate ).
  - Script opcional para crear contratos de ejemplo por tenant.
- Manual de usuario básico
  
  - Uso del admin para crear/editar contratos.
  - Generación/descarga de PDFs.
  - Explicación de estados y flujo de aprobación.
### Notas de Compatibilidad con la Rama Actual
- TenantMiddleware ya está activado; el módulo usa request.tenant en admin/servicios.
- Se mantiene la convención de ocultar el campo tenant en formularios y autoasignar durante guardado.
- Persisten advertencias no bloqueantes ( WeasyPrint y staticfiles.W004 ), documentadas para tratar posteriormente.
- Integración con crm.Client puede activarse si apps.crm está en INSTALLED_APPS ; en su ausencia, se utilizan campos snapshot ( client_name ) para no romper el dominio core.

## 6. Adaptación Realizada (Resumen)

- Se creó la app `apps/core/contracts` con `apps.py`, `models.py`, `admin.py`, `services.py`, `signals.py`, `migrations/` y `templates/export/contract.html`.
- Se registró la app en `config/settings.py` (`INSTALLED_APPS` → `apps.core.contracts`).
- Modelo `Contract` con:
  - `tenant` (`related_name="core_contracts"`) para evitar colisiones con `crm.Contract`.
  - `client` opcional (FK a `crm.Client`, `related_name="core_contracts"`) y `client_name` como snapshot.
  - Validaciones de fechas y montos en `clean()`.
  - Índices por `tenant + status` y `tenant + contract_type`.
- Admin:
  - Campo `tenant` oculto y autoasignado desde `request.tenant`/`request.user.tenant`.
  - `get_queryset` filtrado por `tenant` y `select_related('tenant')`.
  - Acción `generar_pdf` usando `ContractPDFService`.
- Servicio:
  - `ContractPDFService` con import perezoso de WeasyPrint para evitar errores en Windows durante migraciones y arranque.
- Pruebas:
  - `apps/core/contracts/tests/test_admin.py` valida autoasignación de `tenant` y filtrado por `tenant`.
- Compatibilidad:
  - No se modifican los modelos de `apps/crm`. Se evita choque de reverse accessors con `related_name`.
  - Persisten advertencias conocidas de `staticfiles.W004` y entorno WeasyPrint en Windows, no bloqueantes.