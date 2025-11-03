from django.utils.deprecation import MiddlewareMixin


class TenantMiddleware(MiddlewareMixin):
    """Asigna un tenant a la petición.

    - Si no hay resolución por subdominio, usa el tenant por defecto ('default').
    - Adjunta `request.tenant` para uso general.
    - Para usuarios autenticados sin atributo `tenant`, asigna el tenant por defecto en memoria
      (no persistente) para que el admin pueda autoasignar en `save_model`.
    """

    def process_request(self, request):
        from apps.core.models import Tenant

        # Intento de resolución básica por host/subdominio (simple).
        host = request.get_host().split(':')[0]
        subdomain = None
        if '.' in host:
            subdomain = host.split('.')[0]

        tenant = None
        if subdomain:
            tenant = Tenant.objects.filter(subdomain=subdomain, is_active=True).first()

        if tenant is None:
            tenant = Tenant.objects.filter(subdomain='default').first() or Tenant.objects.filter(is_active=True).first()

        request.tenant = tenant

        user = getattr(request, 'user', None)
        if user and getattr(user, 'is_authenticated', False) and not hasattr(user, 'tenant'):
            # Atributo en memoria para uso del admin y vistas; no persistente.
            setattr(user, 'tenant', tenant)