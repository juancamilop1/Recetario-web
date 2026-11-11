from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.contrib.auth.views import LoginView, LogoutView
from django.db.models import F
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy

from .forms import RecetaForm, RegistroForm
from .models import Opcion, Receta


def _es_admin(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser)


def _puede_gestionar(user, receta):
    if not user.is_authenticated:
        return False
    if _es_admin(user):
        return True
    return receta.usuario_id == user.id


def lista_recetas(request):
    recetas = Receta.objects.select_related('usuario').all()
    return render(request, 'recetas/lista.html', {'recetas': recetas})


def detalle_receta(request, receta_id):
    receta = get_object_or_404(Receta.objects.select_related('usuario'), pk=receta_id)
    return render(request, 'recetas/detalle.html', {
        'receta': receta,
        'puede_gestionar': _puede_gestionar(request.user, receta),
    })


@login_required
def crear_receta(request):
    if request.method == 'POST':
        form = RecetaForm(request.POST)
        if form.is_valid():
            receta = form.save(commit=False)
            receta.usuario = request.user
            receta.save()
            messages.success(request, 'Receta creada correctamente.')
            return redirect('recetas:lista_recetas')
    else:
        form = RecetaForm()
    return render(request, 'recetas/formulario.html', {'form': form, 'titulo': 'Nueva receta'})


@login_required
def editar_receta(request, receta_id):
    receta = get_object_or_404(Receta, pk=receta_id)
    if not _puede_gestionar(request.user, receta):
        return HttpResponseForbidden('No tienes permiso para editar esta receta.')
    if request.method == 'POST':
        form = RecetaForm(request.POST, instance=receta)
        if form.is_valid():
            form.save()
            messages.success(request, 'Receta actualizada.')
            return redirect('recetas:detalle_receta', receta_id=receta.id)
    else:
        form = RecetaForm(instance=receta)
    return render(request, 'recetas/formulario.html', {
        'form': form,
        'titulo': 'Editar receta',
        'receta': receta,
    })


@login_required
def eliminar_receta(request, receta_id):
    receta = get_object_or_404(Receta, pk=receta_id)
    if not _puede_gestionar(request.user, receta):
        return HttpResponseForbidden('No tienes permiso para eliminar esta receta.')
    if request.method == 'POST':
        receta.delete()
        messages.success(request, 'Receta eliminada.')
        return redirect('recetas:lista_recetas')
    return render(request, 'recetas/eliminar.html', {'receta': receta})


def resultados(request, receta_id):
    receta = get_object_or_404(Receta, pk=receta_id)
    return render(request, 'recetas/resultados.html', {'receta': receta})


@login_required
def votar(request, receta_id):
    receta = get_object_or_404(Receta, pk=receta_id)
    try:
        selected_choice = receta.opcion_set.get(pk=request.POST['opcion'])
    except (KeyError, Opcion.DoesNotExist):
        return render(request, 'recetas/detalle.html', {
            'receta': receta,
            'puede_gestionar': _puede_gestionar(request.user, receta),
            'error_message': 'No elegiste una opción.',
        })
    selected_choice.votos = F('votos') + 1
    selected_choice.save()
    return redirect('recetas:resultados', receta_id=receta.id)


def registro(request):
    if request.user.is_authenticated:
        return redirect('recetas:lista_recetas')
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            grupo, _ = Group.objects.get_or_create(name='Usuario')
            user.groups.add(grupo)
            login(request, user)
            messages.success(request, 'Cuenta creada. Ya iniciaste sesión.')
            return redirect('recetas:lista_recetas')
    else:
        form = RegistroForm()
    return render(request, 'recetas/registro.html', {'form': form})


class RecetarioLoginView(LoginView):
    template_name = 'recetas/login.html'
    redirect_authenticated_user = True


class RecetarioLogoutView(LogoutView):
    next_page = reverse_lazy('recetas:lista_recetas')
