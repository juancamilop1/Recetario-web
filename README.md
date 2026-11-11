# Recetario Web

Aplicación web para organizar recetas de cocina: CRUD, votación de opciones, autenticación, roles y panel de administración.

**Curso:** Proyecto de Desarrollo Web — Grupo 500  
**Integrantes:** Angely Liced Herrera Roldán · Juan Camilo Barragán Pottes  
**Entrega:** 2 (núcleo funcional)

## Documentación

- Entrega 1: [`docs/Recetario Web.pdf`](docs/Recetario%20Web.pdf)
- Entrega 2: [`docs/Recetario Web - Entrega 2.pdf`](docs/Recetario%20Web%20-%20Entrega%202.pdf)
- Video Entrega 1: https://youtu.be/FFmJFL3By50
- Repositorio: https://github.com/juancamilop1/Recetario-web
- Aplicación publicada: https://recetario-web-pilj.onrender.com/recetas/

## Requisitos

- Python 3.12+
- Docker (opcional, para contenedor)

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

- App: http://127.0.0.1:8000/recetas/
- Registro: http://127.0.0.1:8000/recetas/registro/
- Admin: http://127.0.0.1:8000/admin/

## Docker

El repositorio incluye un `Dockerfile` (Python 3.12-slim, dependencias, `collectstatic`, migraciones al iniciar y Gunicorn en el puerto 8000).

Variables de entorno: `DJANGO_SECRET_KEY`, `DJANGO_DEBUG`, `DJANGO_ALLOWED_HOSTS`, `DJANGO_CSRF_TRUSTED_ORIGINS`.

```bash
docker build -t recetario-web .
docker run --rm -p 8000:8000 ^
  -e DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1 ^
  -e DJANGO_DEBUG=True ^
  recetario-web
```

Luego: http://127.0.0.1:8000/recetas/

## Roles

| Rol | Capacidad |
|---|---|
| Anónimo | Listar y ver detalle / resultados |
| Usuario | Registro/login; CRUD de sus recetas; votar |
| Administrador | Django Admin; gestiona cualquier receta |

## Estructura

```
recetario/     # configuración Django
recetas/       # dominio, auth de pantallas, plantillas
docs/          # documentos de entrega
Dockerfile     # imagen de la aplicación
```
