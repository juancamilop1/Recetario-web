"""Cliente HTTP hacia el microservicio Node.js (servicio-ia)."""
import os
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
import json


def node_base_url():
    return os.environ.get('NODE_SERVICE_URL', 'http://127.0.0.1:3000').rstrip('/')


def _post(path, payload, timeout=60):
    url = f'{node_base_url()}{path}'
    data = json.dumps(payload).encode('utf-8')
    req = Request(
        url,
        data=data,
        headers={'Content-Type': 'application/json', 'Accept': 'application/json'},
        method='POST',
    )
    try:
        with urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode('utf-8')
            return resp.status, json.loads(body) if body else {}
    except HTTPError as exc:
        raw = exc.read().decode('utf-8', errors='replace')
        try:
            detail = json.loads(raw)
        except json.JSONDecodeError:
            detail = {'error': raw or str(exc)}
        return exc.code, detail
    except URLError as exc:
        return 503, {
            'ok': False,
            'error': f'No se pudo contactar el microservicio Node ({node_base_url()}): {exc.reason}',
        }


def sugerir_receta(ingredientes='', categoria='', preferencias=''):
    return _post('/api/sugerir-receta', {
        'ingredientes': ingredientes,
        'categoria': categoria,
        'preferencias': preferencias,
    })


def generar_preparacion(nombre, ingredientes, categoria=''):
    return _post('/api/generar-preparacion', {
        'nombre': nombre,
        'ingredientes': ingredientes,
        'categoria': categoria,
    })


def health():
    url = f'{node_base_url()}/health'
    try:
        with urlopen(url, timeout=10) as resp:
            return resp.status, json.loads(resp.read().decode('utf-8'))
    except Exception as exc:  # noqa: BLE001
        return 503, {'ok': False, 'error': str(exc)}
