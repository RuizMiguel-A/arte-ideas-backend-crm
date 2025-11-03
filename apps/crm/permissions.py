from rest_framework.permissions import BasePermission


# Mapa mínimo de permisos por rol para el módulo contracts (CRM)
# Alineado a la documentación, permite ajustar en el futuro a MODULE_PERMISSIONS.
ROLE_PERMISSIONS_CONTRACTS = {
    # Roles del frontend (compatibilidad): admin tiene todo
    'admin': ['view', 'add', 'change', 'delete'],
    'manager': ['view', 'add', 'change'],
    'employee': ['view'],
    'photographer': ['view'],
    'assistant': ['view'],

    # Roles técnicos (documentación de SYSTEM_ROLES) en caso de usarse
    'ADMIN': ['view', 'add', 'change', 'delete'],
    'SALES': ['view', 'add', 'change'],
    'PRODUCTION': ['view'],
    'OPERATOR': ['view', 'change'],
}


HTTP_METHOD_TO_ACTION = {
    'GET': 'view',
    'HEAD': 'view',
    'OPTIONS': 'view',
    'POST': 'add',
    'PUT': 'change',
    'PATCH': 'change',
    'DELETE': 'delete',
}


class ContractPermission(BasePermission):
    """Permiso para el módulo de contratos.

    - Valida acceso por rol a acciones CRUD.
    - Aplica aislamiento por tenant en permisos de objeto.
    - Considera acciones custom como `download` como `view`.
    """

    message = 'No tienes permisos para realizar esta acción en contratos.'

    def has_permission(self, request, view):
        user = getattr(request, 'user', None)
        tenant = getattr(request, 'tenant', None)
        if user is None or tenant is None:
            return False

        # Determinar acción por método/acción de la vista
        action = HTTP_METHOD_TO_ACTION.get(request.method, 'view')
        # Acciones custom: download -> view
        if getattr(view, 'action', None) == 'download':
            action = 'view'

        # Determinar permisos por rol
        role = getattr(user, 'role', None)
        allowed = ROLE_PERMISSIONS_CONTRACTS.get(role, [])
        return action in allowed

    def has_object_permission(self, request, view, obj):
        # Verificar pertenencia de tenant
        tenant = getattr(request, 'tenant', None)
        return getattr(obj, 'tenant', None) == tenant