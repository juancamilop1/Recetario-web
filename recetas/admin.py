from django.contrib import admin

from .models import Opcion, Receta


class OpcionInline(admin.TabularInline):
    model = Opcion
    extra = 1


@admin.register(Receta)
class RecetaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'categoria', 'usuario')
    list_filter = ('categoria', 'usuario')
    search_fields = ('nombre', 'categoria')
    inlines = [OpcionInline]


@admin.register(Opcion)
class OpcionAdmin(admin.ModelAdmin):
    list_display = ('opcion_texto', 'receta', 'votos')
    list_filter = ('receta',)
