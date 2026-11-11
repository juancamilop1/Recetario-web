from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Receta


class RegistroForm(UserCreationForm):
    email = forms.EmailField(required=False, label='Correo')

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
        labels = {
            'username': 'Usuario',
        }


class RecetaForm(forms.ModelForm):
    class Meta:
        model = Receta
        fields = ('nombre', 'categoria', 'ingredientes', 'preparacion')
        labels = {
            'nombre': 'Nombre',
            'categoria': 'Categoría',
            'ingredientes': 'Ingredientes',
            'preparacion': 'Preparación',
        }
        widgets = {
            'ingredientes': forms.Textarea(attrs={'rows': 4}),
            'preparacion': forms.Textarea(attrs={'rows': 4}),
        }
