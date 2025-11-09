"""
URLs del Analytics App - Arte Ideas
"""
from django.urls import path, include

app_name = 'analytics'

urlpatterns = [
    # Incluir URLs de Reportes
    path('', include('apps.analytics.Reportes.urls')),
]

