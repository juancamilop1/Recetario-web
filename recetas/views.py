from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.contrib.auth.views import LoginView, LogoutView
from django.db.models import F, Q
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST

from . import node_client
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
    q = request.GET.get('q', '').strip()
    categoria_activa = request.GET.get('categoria', '').strip()

    recetas = Receta.objects.select_related('usuario').all().order_by('-id')
    if q:
        recetas = recetas.filter(
            Q(nombre__icontains=q)
            | Q(categoria__icontains=q)
            | Q(ingredientes__icontains=q)
        )
    if categoria_activa:
        recetas = recetas.filter(categoria__iexact=categoria_activa)

    categorias = sorted(
        {
            c.strip()
            for c in Receta.objects.values_list('categoria', flat=True)
            if c and c.strip()
        },
        key=str.lower,
    )
    return render(request, 'recetas/lista.html', {
        'recetas': recetas,
        'q': q,
        'categoria_activa': categoria_activa,
        'categorias': categorias,
    })


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
    opciones = list(receta.opcion_set.all())
    total_votos = sum(op.votos for op in opciones)
    opciones_detalle = [
        {
            'opcion': op,
            'porcentaje': round((op.votos / total_votos) * 100) if total_votos else 0,
        }
        for op in opciones
    ]
    return render(request, 'recetas/resultados.html', {
        'receta': receta,
        'opciones_detalle': opciones_detalle,
        'total_votos': total_votos,
    })


@login_required
@require_POST
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


@login_required
def asistente_ia(request):
    """Formulario que pide una sugerencia al microservicio Node (Gemini)."""
    resultado = None
    error = None
    form_data = {
        'ingredientes': request.POST.get('ingredientes', ''),
        'categoria': request.POST.get('categoria', ''),
        'preferencias': request.POST.get('preferencias', ''),
    }
    if request.method == 'POST':
        status, payload = node_client.sugerir_receta(
            ingredientes=form_data['ingredientes'],
            categoria=form_data['categoria'],
            preferencias=form_data['preferencias'],
        )
        if status == 200 and payload.get('ok'):
            resultado = payload.get('data') or {}
            messages.success(request, 'Sugerencia generada vía microservicio Node + Gemini.')
        else:
            error = payload.get('error') or f'Error del microservicio (HTTP {status}).'
    health_status, health_payload = node_client.health()
    return render(request, 'recetas/asistente_ia.html', {
        'form_data': form_data,
        'resultado': resultado,
        'error': error,
        'node_url': node_client.node_base_url(),
        'node_ok': health_status == 200,
        'node_health': health_payload,
        'swagger_url': f'{node_client.node_base_url()}/api-docs',
    })


@login_required
@require_POST
def generar_preparacion_ia(request, receta_id):
    """Django → Node: genera preparación para una receta existente."""
    receta = get_object_or_404(Receta, pk=receta_id)
    if not _puede_gestionar(request.user, receta):
        return HttpResponseForbidden('No tienes permiso para modificar esta receta.')

    status, payload = node_client.generar_preparacion(
        nombre=receta.nombre,
        ingredientes=receta.ingredientes,
        categoria=receta.categoria,
    )
    if status == 200 and payload.get('ok'):
        data = payload.get('data') or {}
        preparacion = data.get('preparacion')
        if preparacion:
            receta.preparacion = preparacion
            tips = data.get('tips')
            if tips:
                receta.preparacion = f'{preparacion}\n\nTips: {tips}'
            receta.save()
            messages.success(request, 'Preparación actualizada con IA (Django → Node → Gemini).')
        else:
            messages.warning(request, 'El microservicio respondió sin campo preparación.')
    else:
        messages.error(
            request,
            payload.get('error') or f'No se pudo generar la preparación (HTTP {status}).',
        )
    return redirect('recetas:detalle_receta', receta_id=receta.id)


@login_required
def guardar_sugerencia_ia(request):
    """Guarda en BD una sugerencia IA enviada por POST."""
    if request.method != 'POST':
        return redirect('recetas:asistente_ia')
    receta = Receta.objects.create(
        nombre=request.POST.get('nombre', 'Receta IA')[:200],
        categoria=request.POST.get('categoria', 'IA')[:100],
        ingredientes=request.POST.get('ingredientes', ''),
        preparacion=request.POST.get('preparacion', ''),
        usuario=request.user,
    )
    messages.success(request, 'Receta sugerida por IA guardada en tu recetario.')
    return redirect('recetas:detalle_receta', receta_id=receta.id)
