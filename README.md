# Recetario Web

Aplicación web para organizar y administrar recetas de cocina: registro, consulta, edición, eliminación y módulo de votación sobre opciones asociadas a cada receta.

**Curso:** Proyecto de Desarrollo Web — Grupo 500  
**Integrantes:** Angely Liced Herrera Roldán · Juan Camilo Barragán Pottes  
**Entrega:** 1 (definición de la solución y la arquitectura)

## Documentación

Documento de la Entrega 1 (SRS, UML, backlog): [`docs/Recetario Web.pdf`](docs/Recetario%20Web.pdf)

- Video de presentación: _(enlace)_  
- Repositorio: https://github.com/juancamilop1/Recetario-web

## Requisitos

- Python 3.12+
- Django 5.1.x

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

- Aplicación: http://127.0.0.1:8000/recetas/  
- Admin: http://127.0.0.1:8000/admin/

## Estructura

```
recetario/     # configuración del proyecto Django
recetas/       # app de dominio (modelos, vistas, plantillas)
docs/          # documento de entrega (PDF)
```

## Stack (Entrega 1)

| Componente | Tecnología |
|---|---|
| Lenguaje | Python 3.x |
| Framework | Django 5.1 |
| Base de datos | SQLite |
| Interfaz | HTML + Django Templates |
| Administración | Django Admin |
| Versionado | Git + GitHub |
