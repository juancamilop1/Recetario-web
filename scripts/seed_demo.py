"""Carga recetas de demostración de forma idempotente si la BD está vacía."""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import django
from django.apps import apps

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'recetario.settings')
if not apps.ready:
    django.setup()

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

from recetas.models import Opcion, Receta


RECETAS_DEMO = [
    {
        'nombre': 'Arroz con pollo casero',
        'categoria': 'Almuerzo',
        'ingredientes': (
            '- 2 tazas de arroz\n'
            '- 500 g de pechuga de pollo desmechada\n'
            '- 1 cebolla cabezona picada\n'
            '- 1 pimentón rojo en cubos\n'
            '- 1 zanahoria en cubos y 1/2 taza de arvejas\n'
            '- 4 tazas de caldo de pollo, sal, comino y color al gusto'
        ),
        'preparacion': (
            '1. Cocina la pechuga en agua con sal y especias; reserva el caldo y desmecha el pollo.\n'
            '2. Sofríe la cebolla, el pimentón y la zanahoria durante 5 minutos.\n'
            '3. Agrega el arroz, el pollo, las arvejas y el caldo caliente.\n'
            '4. Cocina a fuego medio hasta que seque, tapa y deja 15 minutos a fuego bajo.'
        ),
        'opciones': [
            ('Favorita familiar', 5),
            ('Ideal para el fin de semana', 3),
            ('Fácil de preparar', 2),
        ],
    },
    {
        'nombre': 'Arepas rellenas de queso',
        'categoria': 'Desayuno',
        'ingredientes': (
            '- 2 tazas de harina de maíz precocida\n'
            '- 2 1/2 tazas de agua tibia\n'
            '- 1 cucharada de mantequilla\n'
            '- 1 pizca de sal\n'
            '- 200 g de queso campesino o mozzarella rallado'
        ),
        'preparacion': (
            '1. Mezcla el agua tibia, la sal y la mantequilla derretida.\n'
            '2. Incorpora la harina poco a poco y amasa hasta obtener una masa suave.\n'
            '3. Forma discos, coloca queso en el centro y sella formando arepas.\n'
            '4. Asa en sartén o plancha engrasada 5 minutos por cada lado hasta dorar.'
        ),
        'opciones': [
            ('Rápida y económica', 4),
            ('Desayuno clásico', 6),
            ('Para compartir', 2),
        ],
    },
    {
        'nombre': 'Pasta al pesto rápido',
        'categoria': 'Cena',
        'ingredientes': (
            '- 250 g de espagueti o penne\n'
            '- 2 tazas de hojas frescas de albahaca\n'
            '- 1 diente de ajo\n'
            '- 50 g de queso parmesano rallado\n'
            '- 1/3 taza de aceite de oliva y un puñado de nueces o maní'
        ),
        'preparacion': (
            '1. Cocina la pasta en agua hirviendo con sal hasta que quede al dente.\n'
            '2. Licúa la albahaca, ajo, queso parmesano, nueces y aceite de oliva.\n'
            '3. Escurre la pasta reservando un poco del agua de cocción.\n'
            '4. Mezcla la pasta caliente con el pesto y sirve con parmesano extra.'
        ),
        'opciones': [
            ('Lista en 20 minutos', 7),
            ('Vegetariana', 4),
            ('Cena ligera', 3),
        ],
    },
    {
        'nombre': 'Ajiaco santafereño',
        'categoria': 'Sopa',
        'ingredientes': (
            '- 1 pechuga de pollo con hueso\n'
            '- 500 g de papa criolla, 500 g de papa sabanera y 500 g de papa pastusa\n'
            '- 2 mazorcas cortadas en trozos\n'
            '- 1 ramo de guascas frescas\n'
            '- Crema de leche, alcaparras y aguacate para acompañar'
        ),
        'preparacion': (
            '1. Hierve el pollo con cebolla larga, ajo y mazorca durante 30 minutos.\n'
            '2. Retira el pollo para desmechar y agrega las papas pastusa y sabanera en rodajas.\n'
            '3. Cuando espesen, añade la papa criolla y las guascas; cocina 20 minutos más.\n'
            '4. Sirve caliente con pollo desmechado, crema de leche, alcaparras y aguacate.'
        ),
        'opciones': [
            ('Tradicional colombiana', 8),
            ('Para día frío', 5),
            ('Almuerzo completo', 4),
        ],
    },
]


def seed_demo():
    Group.objects.get_or_create(name='Usuario')

    if os.environ.get('DJANGO_SKIP_SEED', '').lower() in ('1', 'true', 'yes'):
        print('seed_demo: skipped (DJANGO_SKIP_SEED)')
        return 0

    if Receta.objects.exists():
        print(f'seed_demo: skipped ({Receta.objects.count()} recetas ya existen)')
        return 0

    User = get_user_model()
    autor = User.objects.filter(is_staff=True).order_by('id').first()

    creadas = 0
    for item in RECETAS_DEMO:
        receta = Receta.objects.create(
            nombre=item['nombre'],
            categoria=item['categoria'],
            ingredientes=item['ingredientes'],
            preparacion=item['preparacion'],
            usuario=autor,
        )
        for texto, votos in item['opciones']:
            Opcion.objects.create(receta=receta, opcion_texto=texto, votos=votos)
        creadas += 1

    print(f'seed_demo: created {creadas} recetas demo (autor={autor.username if autor else "None"})')
    return creadas


if __name__ == '__main__':
    seed_demo()
