from django.urls import path

from . import views

app_name = 'recetas'

urlpatterns = [
    path('', views.lista_recetas, name='lista_recetas'),
    path('registro/', views.registro, name='registro'),
    path('login/', views.RecetarioLoginView.as_view(), name='login'),
    path('logout/', views.RecetarioLogoutView.as_view(), name='logout'),
    path('crear/', views.crear_receta, name='crear_receta'),
    path('asistente-ia/', views.asistente_ia, name='asistente_ia'),
    path('asistente-ia/guardar/', views.guardar_sugerencia_ia, name='guardar_sugerencia_ia'),
    path('<int:receta_id>/', views.detalle_receta, name='detalle_receta'),
    path('<int:receta_id>/editar/', views.editar_receta, name='editar_receta'),
    path('<int:receta_id>/eliminar/', views.eliminar_receta, name='eliminar_receta'),
    path('<int:receta_id>/ia-preparacion/', views.generar_preparacion_ia, name='generar_preparacion_ia'),
    path('<int:receta_id>/resultados/', views.resultados, name='resultados'),
    path('<int:receta_id>/votar/', views.votar, name='votar'),
]
