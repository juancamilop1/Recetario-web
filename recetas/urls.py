from django.urls import path
app_name = 'recetas'
from . import views
urlpatterns = [
    path('', views.lista_recetas, name='lista_recetas'),
    path('crear/', views.crear_receta, name='crear_receta'),
    path('<int:receta_id>/', views.detalle_receta, name='detalle_receta'),
    path('<int:receta_id>/editar/', views.editar_receta, name='editar_receta'),
    path('<int:receta_id>/eliminar/', views.eliminar_receta, name='eliminar_receta'),
    path('<int:receta_id>/resultados/', views.resultados, name='resultados'),
    path('<int:receta_id>/votar/', views.votar, name='votar'),
]
