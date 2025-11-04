"""
URL configuration for activos_web project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from gestion_activos import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('nuevo-activo', views.nuevo_activo, name='nuevo_activo'),
    path('editar-activo/<int:id>/', views.editar_activo, name='editar_activo'),
    path('eliminar-activo/<int:id>/', views.eliminar_activo, name='eliminar_activo'),
    path('nuevo-financiamiento', views.nuevo_financiamiento, name='nuevo_financiamiento'),
    path('editar-financiamiento/<int:id>/', views.editar_financiamiento, name='editar_financiamiento'),
    path('eliminar-financiamiento/<int:id>/', views.eliminar_financiamiento, name='eliminar_financiamiento'),
    path('nuevo-mantenimiento', views.nuevo_mantenimiento, name='nuevo_mantenimiento'),
    path('editar-mantenimiento/<int:id>/', views.editar_mantenimiento, name='editar_mantenimiento'),
    path('eliminar-mantenimiento/<int:id>/', views.eliminar_mantenimiento, name='eliminar_mantenimiento'),
    path('nuevo-repuesto', views.nuevo_repuesto, name='nuevo_repuesto'),
    path('editar-repuesto/<int:id>/', views.editar_repuesto, name='editar_repuesto'),
    path('eliminar-repuesto/<int:id>/', views.eliminar_repuesto, name='eliminar_repuesto'),
]
