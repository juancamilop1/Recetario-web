# Recetario Web

Aplicación web para organizar recetas de cocina: CRUD, autenticación, roles, microservicio Node.js con Swagger e integración con IA (Gemini).

**Curso:** Proyecto de Desarrollo Web — Grupo 500  
**Integrantes:** Angely Liced Herrera Roldán · Juan Camilo Barragán Pottes  
**Entrega:** 3 (microservicios e IA)

## Documentación

- Entrega 1: [`docs/Recetario Web.pdf`](docs/Recetario%20Web.pdf)
- Entrega 2: [`docs/Recetario Web - Entrega 2.pdf`](docs/Recetario%20Web%20-%20Entrega%202.pdf)
- Entrega 3: [`docs/Recetario Web - Entrega 3.pdf`](docs/Recetario%20Web%20-%20Entrega%203.pdf)
- Video Entrega 1: https://youtu.be/FFmJFL3By50
- Video Entrega 2: https://www.youtube.com/watch?v=C73CEqm2jwM
- Video Entrega 3: https://www.youtube.com/watch?v=IKS0ypaqq8Q
- Repositorio: https://github.com/juancamilop1/Recetario-web
- App Django (Render): https://recetario-web-pilj.onrender.com/recetas/
- Microservicio Node (Render): https://recetario-servicio-ia.onrender.com
- Health Node: https://recetario-servicio-ia.onrender.com/health
- Swagger Node (público): https://recetario-servicio-ia.onrender.com/api-docs

## Arquitectura (Entrega 3)

```
Navegador → Django (8000) → Node.js servicio-ia (3000) → Google Gemini
                              └─ Swagger /api-docs
```

## Requisitos

- Python 3.12+
- Node.js 18+
- Docker / Docker Compose (recomendado)

### 1) Microservicio Node

```bash
cd servicio-ia
copy .env.example .env
# Edita .env y pega GEMINI_API_KEY=...
npm install
npm start
```

- Health: http://127.0.0.1:3000/health  
- Swagger: http://127.0.0.1:3000/api-docs  

### 2) Django

```bash
cd ..
copy .env.example .env
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

- App: http://127.0.0.1:8000/recetas/  
- Asistente IA: http://127.0.0.1:8000/recetas/asistente-ia/  

`NODE_SERVICE_URL` por defecto: `http://127.0.0.1:3000`

## Docker Compose

Con la key en el entorno (o en un `.env` en la raíz):

```bash
# PowerShell
$env:GEMINI_API_KEY="TU_API_KEY_AQUI"
docker compose up --build
```

Servicios:
- `web` → http://localhost:8000  
- `servicio-ia` → http://localhost:3000/api-docs  

## Roles

| Rol | Capacidad |
|---|---|
| Anónimo | Listar y ver detalle / resultados |
| Usuario | CRUD propio, votar, asistente IA |
| Administrador | Django Admin; gestiona cualquier receta |

## Estructura

```
recetario/       # proyecto Django
recetas/         # app de dominio + cliente Node
servicio-ia/     # microservicio Node + Swagger + Gemini
docker-compose.yml
docs/            # PDFs de entrega
```
