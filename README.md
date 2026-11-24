# Huanguelén Dona Vida - Sitio web

Sitio estático (HTML/CSS/JS en un solo archivo principal) para la campaña **Huanguelén Dona Vida**.

## Archivos principales

- `index.html`: página principal, estilos y lógica JS.
- `logo.png`: logo de Huanguelén Dona Vida.
- `assets/`: imágenes del tablero y fichas del Camino del donante.
- `style.css`: hoja de estilos heredada/no vinculada actualmente. Revisar antes de reutilizar para evitar conflictos con los estilos inline de `index.html`.

## Cómo actualizar contenido

### 1. Calendario de Google
En `index.html`, buscar la configuración:

```js
const GOOGLE_CALENDAR_URL = "https://calendar.google.com/calendar/embed?src=REEMPLAZAR_ID_CALENDARIO&ctz=America%2FArgentina%2FBuenos_Aires";
```

Reemplazar `REEMPLAZAR_ID_CALENDARIO` por el ID público del calendario.

### 2. Galería de Google Drive
En `index.html`, buscar la configuración de galería:

```js
const DRIVE_GALERIA_ID = "15sCK3t3Np5V8XJommeBpXkQNeiOTUfco";
const DRIVE_GALERIA_URL = `https://drive.google.com/embeddedfolderview?id=${DRIVE_GALERIA_ID}#grid`;
const DRIVE_GALERIA_CARPETA_URL = `https://drive.google.com/drive/folders/${DRIVE_GALERIA_ID}?usp=sharing`;
```

Para cambiar la carpeta, reemplazar `DRIVE_GALERIA_ID` por el ID de la carpeta de Drive compartida públicamente.

### 3. Asistente virtual (Medulín)
La lógica del asistente está en la función `responder(texto)` dentro de `index.html`.

- Mantener la aclaración: los requisitos/edades informados corresponden principalmente a la Provincia de Buenos Aires y pueden variar según la jurisdicción.
- Incluir fuentes oficiales cuando se agreguen requisitos/edades.
- Para actualizar preguntas frecuentes, conviene convertir la base a un arreglo de objetos FAQ (pregunta, variantes, respuesta, fuente, jurisdicción, fecha de verificación).

### 4. Camino del donante
- Fichas usadas: arreglo `fichas` en `index.html`.
- Descripciones por etapa: objeto `descripcionesFichas` en `index.html`.
- Imágenes: `assets/ficha-N.png` y `assets/tablero.png`.

### 5. Memotest
El memotest acepta pares con texto y opcionalmente imagen:

```js
{ id: "sangre", texto: "Sangre", img: "assets/memo-sangre.png", alt: "Gota de sangre" }
```

### 6. Trivia
Las preguntas están en el arreglo `preguntas` dentro de `index.html`. Cada pregunta tiene `pregunta`, `opciones` e índice `correcta`.

## Pendientes que dependen del equipo

- Confirmar el nombre definitivo del bot (actualmente: Medulín).
- Recibir y cargar FAQ validadas (Puchi), especialmente requisitos/edades de sangre y CPH en PBA.
- Conectar carpeta real de Google Drive para la galería.
- Conectar calendario real de Google Calendar.
- Recibir imágenes para el memotest.
- Validar secuencia y textos pedagógicos del Camino del donante.
- Revisar paleta/identidad visual final con el equipo de HDV.

## Verificación rápida

Como es un sitio estático, se puede abrir `index.html` en el navegador. Para una prueba local simple:

```bash
python -m http.server 8000
```

Luego abrir `http://localhost:8000`.
