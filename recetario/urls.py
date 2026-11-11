from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('recetas/', include('recetas.urls')),
    path('', RedirectView.as_view(pattern_name='recetas:lista_recetas', permanent=False)),
]
