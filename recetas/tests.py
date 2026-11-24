from unittest.mock import patch

from django.contrib.auth.models import Group, User
from django.test import TestCase
from django.urls import reverse

from .models import Opcion, Receta


class RecetarioAuthAndCrudTests(TestCase):
    def setUp(self):
        self.user_a = User.objects.create_user(username='angely', password='Password123!')
        self.user_b = User.objects.create_user(username='otro', password='Password123!')
        self.admin = User.objects.create_user(
            username='admin_demo',
            password='Password123!',
            is_staff=True,
            is_superuser=True,
        )
        self.receta_a = Receta.objects.create(
            nombre='Arroz con pollo',
            categoria='Almuerzo',
            ingredientes='Arroz, pollo, cebolla',
            preparacion='Cocinar todo junto.',
            usuario=self.user_a,
        )
        self.receta_b = Receta.objects.create(
            nombre='Arepas con queso',
            categoria='Desayuno',
            ingredientes='Harina de maíz, queso',
            preparacion='Amasar y asar.',
            usuario=self.user_b,
        )
        self.op1 = Opcion.objects.create(receta=self.receta_a, opcion_texto='Muy buena', votos=2)
        self.op2 = Opcion.objects.create(receta=self.receta_a, opcion_texto='Rápida', votos=2)

    def test_lista_publica_y_filtros(self):
        resp = self.client.get(reverse('recetas:lista_recetas'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Arroz con pollo')
        self.assertContains(resp, 'Arepas con queso')

        resp_q = self.client.get(reverse('recetas:lista_recetas'), {'q': 'queso'})
        self.assertContains(resp_q, 'Arepas con queso')
        self.assertNotContains(resp_q, 'Arroz con pollo')

        resp_cat = self.client.get(reverse('recetas:lista_recetas'), {'categoria': 'Almuerzo'})
        self.assertContains(resp_cat, 'Arroz con pollo')
        self.assertNotContains(resp_cat, 'Arepas con queso')

    def test_registro_crea_usuario_en_grupo_e_inicia_sesion(self):
        resp = self.client.post(
            reverse('recetas:registro'),
            {
                'username': 'nuevo_user',
                'email': 'nuevo@example.com',
                'password1': 'ClaveSegura2026!',
                'password2': 'ClaveSegura2026!',
            },
        )
        self.assertRedirects(resp, reverse('recetas:lista_recetas'))
        nuevo = User.objects.get(username='nuevo_user')
        self.assertTrue(nuevo.groups.filter(name='Usuario').exists())
        self.assertEqual(int(self.client.session['_auth_user_id']), nuevo.id)

    def test_crear_receta_requiere_login_y_asigna_dueno(self):
        url = reverse('recetas:crear_receta')
        self.assertEqual(self.client.get(url).status_code, 302)

        self.client.login(username='angely', password='Password123!')
        resp = self.client.post(
            url,
            {
                'nombre': 'Sopa de verduras',
                'categoria': 'Sopa',
                'ingredientes': 'Papa, zanahoria, apio',
                'preparacion': 'Hervir 25 minutos.',
            },
        )
        self.assertRedirects(resp, reverse('recetas:lista_recetas'))
        creada = Receta.objects.get(nombre='Sopa de verduras')
        self.assertEqual(creada.usuario, self.user_a)

    def test_permisos_editar_y_eliminar_por_rol(self):
        edit_url = reverse('recetas:editar_receta', args=[self.receta_a.id])
        del_url = reverse('recetas:eliminar_receta', args=[self.receta_a.id])

        # Otro usuario no puede editar ni eliminar
        self.client.login(username='otro', password='Password123!')
        self.assertEqual(self.client.get(edit_url).status_code, 403)
        self.assertEqual(self.client.post(del_url).status_code, 403)

        # Dueño sí puede editar
        self.client.login(username='angely', password='Password123!')
        resp = self.client.post(
            edit_url,
            {
                'nombre': 'Arroz con pollo mejorado',
                'categoria': 'Almuerzo',
                'ingredientes': 'Arroz, pollo, cebolla',
                'preparacion': 'Paso 1, paso 2.',
            },
        )
        self.assertRedirects(resp, reverse('recetas:detalle_receta', args=[self.receta_a.id]))
        self.receta_a.refresh_from_db()
        self.assertEqual(self.receta_a.nombre, 'Arroz con pollo mejorado')

        # Admin sí puede eliminar receta de cualquier usuario
        self.client.login(username='admin_demo', password='Password123!')
        resp_del = self.client.post(del_url)
        self.assertRedirects(resp_del, reverse('recetas:lista_recetas'))
        self.assertFalse(Receta.objects.filter(pk=self.receta_a.id).exists())

    def test_votar_exige_post_y_suma_voto(self):
        url = reverse('recetas:votar', args=[self.receta_a.id])
        self.client.login(username='angely', password='Password123!')

        # GET rechazado (405)
        self.assertEqual(self.client.get(url).status_code, 405)

        # POST sin opción muestra error
        resp_err = self.client.post(url, {})
        self.assertEqual(resp_err.status_code, 200)
        self.assertContains(resp_err, 'No elegiste una opción.')

        # POST válido incrementa votos y muestra resultados con porcentaje
        resp_ok = self.client.post(url, {'opcion': self.op1.id})
        self.assertRedirects(resp_ok, reverse('recetas:resultados', args=[self.receta_a.id]))
        self.op1.refresh_from_db()
        self.assertEqual(self.op1.votos, 3)

        resp_res = self.client.get(reverse('recetas:resultados', args=[self.receta_a.id]))
        self.assertEqual(resp_res.status_code, 200)
        self.assertEqual(resp_res.context['total_votos'], 5)
        self.assertContains(resp_res, '60%')


class RecetarioMicroservicioIATests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username='dueno', password='Password123!')
        self.other = User.objects.create_user(username='ajeno', password='Password123!')
        self.receta = Receta.objects.create(
            nombre='Pasta rápida',
            categoria='Cena',
            ingredientes='Pasta, tomate, albahaca',
            preparacion='Pendiente',
            usuario=self.owner,
        )

    @patch('recetas.views.node_client.health', return_value=(200, {'status': 'ok', 'geminiModel': 'gemini-3.5-flash-lite'}))
    @patch('recetas.views.node_client.sugerir_receta')
    def test_asistente_ia_sugerir_y_guardar(self, mock_sugerir, _mock_health):
        mock_sugerir.return_value = (
            200,
            {
                'ok': True,
                'data': {
                    'nombre': 'Pollo al limón',
                    'categoria': 'Almuerzo',
                    'ingredientes': 'Pollo, limón, ajo',
                    'preparacion': '1. Sazonar. 2. Dorar.',
                },
            },
        )
        self.client.login(username='dueno', password='Password123!')
        resp = self.client.post(
            reverse('recetas:asistente_ia'),
            {'ingredientes': 'pollo, limón', 'categoria': 'Almuerzo', 'preferencias': 'rápido'},
        )
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Pollo al limón')
        self.assertContains(resp, 'Node conectado')

        save_resp = self.client.post(
            reverse('recetas:guardar_sugerencia_ia'),
            {
                'nombre': 'Pollo al limón',
                'categoria': 'Almuerzo',
                'ingredientes': 'Pollo, limón, ajo',
                'preparacion': '1. Sazonar. 2. Dorar.',
            },
        )
        guardada = Receta.objects.get(nombre='Pollo al limón')
        self.assertEqual(guardada.usuario, self.owner)
        self.assertRedirects(save_resp, reverse('recetas:detalle_receta', args=[guardada.id]))

    @patch('recetas.views.node_client.generar_preparacion')
    def test_generar_preparacion_ia_post_y_permisos(self, mock_prep):
        mock_prep.return_value = (
            200,
            {'ok': True, 'data': {'preparacion': '1. Hervir pasta. 2. Mezclar salsa.', 'tips': 'Servir caliente.'}},
        )
        url = reverse('recetas:generar_preparacion_ia', args=[self.receta.id])

        # GET rechazado (exige POST con CSRF)
        self.client.login(username='dueno', password='Password123!')
        self.assertEqual(self.client.get(url).status_code, 405)

        # Usuario ajeno recibe 403
        self.client.login(username='ajeno', password='Password123!')
        self.assertEqual(self.client.post(url).status_code, 403)

        # Dueño actualiza preparación con IA
        self.client.login(username='dueno', password='Password123!')
        resp = self.client.post(url)
        self.assertRedirects(resp, reverse('recetas:detalle_receta', args=[self.receta.id]))
        self.receta.refresh_from_db()
        self.assertIn('Hervir pasta', self.receta.preparacion)
        self.assertIn('Tips: Servir caliente.', self.receta.preparacion)


class SeedDemoTests(TestCase):
    def test_seed_demo_es_idempotente(self):
        from scripts.seed_demo import seed_demo

        User.objects.create_user(username='admin_seed', password='Password123!', is_staff=True)
        creadas_1 = seed_demo()
        self.assertGreaterEqual(creadas_1, 4)
        self.assertTrue(Group.objects.filter(name='Usuario').exists())
        self.assertGreater(Opcion.objects.count(), 0)

        # Segunda ejecución no duplica
        creadas_2 = seed_demo()
        self.assertEqual(creadas_2, 0)
        self.assertEqual(Receta.objects.count(), creadas_1)
