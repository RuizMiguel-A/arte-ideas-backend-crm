from django.shortcuts import redirect, get_object_or_404
from .models import Activo, Financiamiento, Mantenimiento, Repuesto
from .forms import ActivoForm, FinanciamientoForm, MantenimientoForm, RepuestoForm

# Create your views here.
    


def nuevo_activo(request):
    if request.method == 'POST':
        form = ActivoForm(request.POST)
        if form.is_valid():
            form.save()
    return redirect('/?seccion=activos')


def editar_activo(request, id):
    activo = get_object_or_404(Activo, id=id)
    if request.method == 'POST':
        form = ActivoForm(request.POST, instance=activo)
        if form.is_valid():
            form.save()
            return redirect('/?seccion=activos')
    return redirect('/?seccion=activos')

def eliminar_activo(request, id):
    activo = get_object_or_404(Activo, id=id)
    if request.method == 'POST':
        activo.delete()
    return redirect('/?seccion=activos')


def nuevo_financiamiento(request):
    if request.method == 'POST':
        form = FinanciamientoForm(request.POST)
        if form.is_valid():
            financiamiento = form.save(commit=False)
            # Asegurar que el monto financiado jale el costo total del activo seleccionado
            if financiamiento.activo and financiamiento.activo.costo_total is not None:
                financiamiento.monto_financiado = financiamiento.activo.costo_total
            financiamiento.save()
    return redirect('/?seccion=financiamientos')


def editar_financiamiento(request, id):
    financiamiento = get_object_or_404(Financiamiento, id=id)
    if request.method == 'POST':
        form = FinanciamientoForm(request.POST, instance=financiamiento)
        if form.is_valid():
            form.save()
            return redirect('/?seccion=financiamientos')
    return redirect('/?seccion=financiamientos')


def eliminar_financiamiento(request, id):
    financiamiento = get_object_or_404(Financiamiento, id=id)
    if request.method == 'POST':
        financiamiento.delete()
    return redirect('/?seccion=financiamientos')


def nuevo_mantenimiento(request):
    if request.method == 'POST':
        form = MantenimientoForm(request.POST)
        if form.is_valid():
            form.save()
    return redirect('/?seccion=mantenimientos')


def editar_mantenimiento(request, id):
    mantenimiento = get_object_or_404(Mantenimiento, id=id)
    if request.method == 'POST':
        form = MantenimientoForm(request.POST, instance=mantenimiento)
        if form.is_valid():
            form.save()
            return redirect('/?seccion=mantenimientos')
    return redirect('/?seccion=mantenimientos')


def eliminar_mantenimiento(request, id):
    mantenimiento = get_object_or_404(Mantenimiento, id=id)
    if request.method == 'POST':
        mantenimiento.delete()
    return redirect('/?seccion=mantenimientos')


def nuevo_repuesto(request):
    if request.method == 'POST':
        form = RepuestoForm(request.POST)
        if form.is_valid():
            form.save()
    return redirect('/?seccion=repuestos')


def editar_repuesto(request, id):
    repuesto = get_object_or_404(Repuesto, id=id)
    if request.method == 'POST':
        form = RepuestoForm(request.POST, instance=repuesto)
        if form.is_valid():
            form.save()
            return redirect('/?seccion=repuestos')
    return redirect('/?seccion=repuestos')


def eliminar_repuesto(request, id):
    repuesto = get_object_or_404(Repuesto, id=id)
    if request.method == 'POST':
        repuesto.delete()
    return redirect('/?seccion=repuestos')
