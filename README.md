# Huanguelén Dona Vida — versión Python

## Qué incluye
- `app.py`: servidor Flask, página principal y API `/api/chat`.
- `templates/index.html`: interfaz original (HTML, CSS y JavaScript) servida por Python.
- `requirements.txt`: dependencias.

## Ejecutar en Windows
1. Instalar Python 3.10 o superior.
2. Abrir una terminal en esta carpeta.
3. Ejecutar `py -m venv .venv`
4. Activar el entorno: `.venv\\Scripts\\activate`
5. Instalar: `pip install -r requirements.txt`
6. Iniciar: `py app.py`
7. Abrir `http://127.0.0.1:5000` en el navegador.

## Nota
Python gestiona el servidor y el endpoint del asistente. El navegador sigue necesitando HTML, CSS y JavaScript para dibujar la página y ejecutar las actividades interactivas. El asistente incluido usa respuestas informativas locales; no es un modelo de IA ni ofrece orientación médica personalizada.

Copiá `logo.png` dentro de `static/` y las imágenes `donacion.jpg`, `tablero.png`, `galeria-1.jpg`, `galeria-2.jpg` y `galeria-3.jpg` dentro de `static/assets/`. Las referencias del HTML ya están preparadas para esas rutas. Si tus archivos tienen otros nombres, habrá que actualizar las rutas.
