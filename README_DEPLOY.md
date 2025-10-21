# AgroTasker Dashboard — Despliegue rápido

Este dashboard sirve `dashboard.html` y expone un proxy `/api/thingspeak/*` para consultar ThingSpeak sin CORS.

## Ejecutar localmente

```powershell
cd C:\Users\sebas\Documents\PlatformIO\Projects\AgroTasker_ESP32_MQTT\dashboard
$env:HOST="0.0.0.0"; $env:PORT="8080"; python server_simple.py
```

- Abre: `http://localhost:8080` o `http://<tu-ip-local>:8080`
- La raíz `/` redirige a `dashboard.html`.

## Despliegue con Docker (local o nube)

1. Construir imagen:
```powershell
docker build -t agrotasker-dashboard .
```
2. Ejecutar contenedor:
```powershell
docker run -e HOST=0.0.0.0 -e PORT=8080 -p 8080:8080 agrotasker-dashboard
```
3. Abre: `http://localhost:8080`

## Render (Web Service con Docker)
1. Sube esta carpeta `dashboard/` a un repositorio en GitHub.
2. En Render, crea un “Web Service” desde el repo y elige “Deploy an existing Dockerfile”.
3. No necesitas build command (Render usará el Dockerfile). Puerto interno 8080.
4. Variables de entorno (opcional):
   - `HOST=0.0.0.0`
   - `PORT=8080`
5. Al terminar, Render te dará una URL pública: `https://<tu-servicio>.onrender.com`
   - Comparte: `https://<tu-servicio>.onrender.com/dashboard.html`

## Railway (sin Docker)
1. Crea un nuevo proyecto → “Deploy from GitHub”.
2. Configura el servicio para ejecutar: `python server_simple.py`
3. Variables de entorno:
   - `HOST=0.0.0.0`
   - `PORT=8080`
4. Railway asigna una URL pública. Comparte `/dashboard.html`.

## Incrustar en otra web (iframe)
Si el dashboard está en `https://mi-dashboard.example.com/dashboard.html`, inserta:

```html
<iframe src="https://mi-dashboard.example.com/dashboard.html"
        style="width:100%;height:900px;border:0;"
        loading="lazy" allowfullscreen></iframe>
```

## Notas
- Este servidor usa solo librerías estándar de Python (no requiere requirements).
- Si cambias IDs/keys de ThingSpeak, edita `server_simple.py` en el diccionario `channels`.
- Actualiza el intervalo en `dashboard.html` si necesitas otra frecuencia.
