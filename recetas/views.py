from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.db.models import F
from .models import Receta, Opcion


def lista_recetas(request):
    recetas = Receta.objects.all()
    return render(request, 'recetas/lista.html', {
        'recetas': recetas
    })


def detalle_receta(request, receta_id):
    receta = get_object_or_404(Receta, pk=receta_id)
    return render(request, 'recetas/detalle.html', {
        'receta': receta
    })


def crear_receta(request):
    if request.method == 'POST':
        Receta.objects.create(
            nombre=request.POST['nombre'],
            categoria=request.POST['categoria'],
            ingredientes=request.POST['ingredientes'],
            preparacion=request.POST['preparacion'],
        )
        return HttpResponseRedirect(reverse('recetas:lista_recetas'))
    return render(request, 'recetas/formulario.html')


def editar_receta(request, receta_id):
    receta = get_object_or_404(Receta, pk=receta_id)
    if request.method == 'POST':
        receta.nombre = request.POST['nombre']
        receta.categoria = request.POST['categoria']
        receta.ingredientes = request.POST['ingredientes']
        receta.preparacion = request.POST['preparacion']
        receta.save()
        return HttpResponseRedirect(reverse('recetas:detalle_receta', args=(receta.id,)))
    return render(request, 'recetas/formulario.html', {
        'receta': receta
    })


def eliminar_receta(request, receta_id):
    receta = get_object_or_404(Receta, pk=receta_id)
    if request.method == 'POST':
        receta.delete()
        return HttpResponseRedirect(reverse('recetas:lista_recetas'))
    return render(request, 'recetas/eliminar.html', {
        'receta': receta
    })


def resultados(request, receta_id):
    receta = get_object_or_404(Receta, pk=receta_id)
    return render(request, 'recetas/resultados.html', {
        'receta': receta
    })


def votar(request, receta_id):
    receta = get_object_or_404(Receta, pk=receta_id)
    try:
        selected_choice = receta.opcion_set.get(pk=request.POST['opcion'])
    except (KeyError, Opcion.DoesNotExist):
        return render(request, 'recetas/detalle.html', {
            'receta': receta,
            'error_message': "No elegiste una opción.",
        })
    else:
        selected_choice.votos = F("votos") + 1
        selected_choice.save()
        return HttpResponseRedirect(reverse('recetas:resultados', args=(receta.id,)))
