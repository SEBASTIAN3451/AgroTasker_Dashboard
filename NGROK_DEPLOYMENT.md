# 🌍 Deployment con ngrok - AgroTasker

## Acceso Remoto Seguro a tu Dashboard

Con ngrok, puedes acceder a tu dashboard desde cualquier lugar del mundo con tu teléfono, tablet o computadora.

## Requisitos Previos

✓ Python 3.11 instalado
✓ AgroTasker descargado
✓ Cuenta gratuita en ngrok (https://ngrok.com)
✓ Token de ngrok: `34OVLY528y5Bxo9hAUjhPZ5rE0m_5PNiZHZbqTSbsF4d6qeRP`

## Instalación de ngrok

### Windows (PowerShell)

```powershell
# Instalar con winget
winget install ngrok.ngrok

# O descargar manualmente desde https://ngrok.com/download
```

### Configurar Token de Autenticación

```powershell
# Una sola vez
ngrok config add-authtoken 34OVLY528y5Bxo9hAUjhPZ5rE0m_5PNiZHZbqTSbsF4d6qeRP
```

## Inicio del Servidor + ngrok

### Opción 1: Manual (Dos ventanas separadas)

**Terminal 1 - Servidor Python:**
```powershell
cd c:\Users\SEBASTIAN\AgroTasker_Dashboard
python server_production.py
```

**Terminal 2 - ngrok:**
```powershell
ngrok http 8080 --region us
```

### Opción 2: Automático (Script PowerShell)

Crea un archivo `start_with_ngrok.ps1`:

```powershell
# Detener procesos previos
Stop-Process -Name python, ngrok -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2

# Cambiar a directorio
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath

Write-Host "🚀 Iniciando AgroTasker con ngrok..." -ForegroundColor Green

# Iniciar servidor Python
Start-Process python -ArgumentList "server_production.py" -WindowStyle Hidden

# Esperar a que el servidor inicie
Start-Sleep -Seconds 3

# Iniciar ngrok
Start-Process ngrok -ArgumentList "http 8080 --region us"

Start-Sleep -Seconds 2

Write-Host "✓ Servidor iniciado" -ForegroundColor Green
Write-Host "✓ ngrok activo - ve a la ventana ngrok para ver la URL pública" -ForegroundColor Green
```

Ejecutar:
```powershell
.\start_with_ngrok.ps1
```

## Acceso a tu Dashboard

### Localmente (Misma red)
```
http://localhost:8080/index-menu.html
```

### Desde cualquier lugar (Con ngrok)

1. Abre la ventana de ngrok
2. Verás algo como:
```
Session Status                online
Account                       ...
Version                       3.5.0
Region                        United States (us)
Latency                        35ms
Web Interface                  http://127.0.0.1:4040
Forwarding                     https://stripeless-thoroughgoingly-landyn.ngrok-free.dev -> http://localhost:8080
```

3. Tu URL pública es:
```
https://stripeless-thoroughgoingly-landyn.ngrok-free.dev/index-menu.html
```

4. Accede desde tu móvil o cualquier navegador

## URLs Disponibles

```
Menú Principal:
https://[TU_NGROK_URL]/index-menu.html

Dashboard Simple:
https://[TU_NGROK_URL]/dashboard_simple.html

Dashboard Avanzado:
https://[TU_NGROK_URL]/dashboard_advanced.html

Dashboard Original:
https://[TU_NGROK_URL]/dashboard.html

API de Suelo:
https://[TU_NGROK_URL]/api/thingspeak/soil

API Meteorológica:
https://[TU_NGROK_URL]/api/thingspeak/weather

API Mátrica/UV:
https://[TU_NGROK_URL]/api/thingspeak/matric_uv
```

## Trucos y Consejos

### URL Estable con Dominio Personalizado

Si tienes plan de pago de ngrok, puedes usar un dominio personalizado:

```powershell
ngrok http 8080 --region us --hostname tudominio.ngrok.io
```

### QR Code

ngrok genera un QR automáticamente. En la consola:
```
Web Interface: http://127.0.0.1:4040
```

Accede a esa URL local para ver un QR escaneable.

### Seguridad

Tu URL de ngrok es **pública pero única**. Para mayor seguridad:

1. Usa HTTPS (ngrok lo proporciona automáticamente)
2. Con plan pro, agrega autenticación
3. Registra la URL en bookmarks seguros
4. No la compartas públicamente

### Inspeccionar Tráfico

Abre en tu navegador:
```
http://127.0.0.1:4040
```

Verás todo el tráfico entre tu app y ngrok (útil para debugging).

## Troubleshooting

### "ERR_NGROK_B012 - ERR_NGROK_3200"
```powershell
# Solución: Actualizar ngrok
ngrok update

# O instalar versión específica
winget uninstall ngrok.ngrok
winget install ngrok.ngrok
```

### Puerto 8080 en uso
```powershell
# Ver qué está usando el puerto
netstat -ano | findstr ":8080"

# Liberar el puerto
taskkill /PID [ID_PROCESO] /F

# O cambiar puerto en el código
# Edita server_production.py y cambia port=9090
```

### Conexión lenta
```powershell
# Cambiar región (ej: eu, in, au)
ngrok http 8080 --region eu
```

Regiones disponibles: us, eu, au, jp, in, sa

## Mantenimiento

### Reiniciar sin perder datos

```powershell
# Los datos en localStorage se mantienen
# Solo reinicia los procesos
Stop-Process -Name python, ngrok -Force
Start-Sleep -Seconds 1
# Ejecuta start_with_ngrok.ps1 nuevamente
```

### Backup de Tareas e Historia

```powershell
# Exportar desde Dashboard → Descargar CSV
# O acceder a navegador DevTools (F12) → Application → localStorage
```

### Limpiar datos viejos

```javascript
// En consola del navegador (F12)
localStorage.clear()
// Recarga la página
location.reload()
```

## Casos de Uso

### Monitoreo desde el Campo
1. Abre la URL de ngrok en tu móvil
2. Dashboard responsivo se adapta a pantalla pequeña
3. Ver alertas en tiempo real

### Compartir Estado con Consultor
1. Envía la URL por WhatsApp
2. Consultor agrónomo ve datos en vivo
3. Da recomendaciones basadas en datos reales

### Integración con Sistema de Riego Automático
1. API de ngrok disponible para otras apps
2. Puedes conectar sistemas inteligentes
3. Automatizar riego con webhook

## API Documentación

### Obtener datos de suelo

```bash
curl https://[TU_NGROK_URL]/api/thingspeak/soil
```

Respuesta:
```json
{
  "channel": {
    "id": 2791076,
    "name": "Sensores del Suelo"
  },
  "feeds": [
    {
      "created_at": "2024-01-15T10:30:00Z",
      "field1": "45.2",
      "field2": "28.5",
      "field3": "6.8",
      "field4": "1200",
      "field5": "250",
      "field6": "45",
      "field7": "200"
    }
  ]
}
```

### Campos:
- field1: Humedad Suelo (%)
- field2: Temperatura Suelo (°C)
- field3: pH
- field4: Conductividad (µS/cm)
- field5: Nitrógeno (mg/kg)
- field6: Fósforo (mg/kg)
- field7: Potasio (mg/kg)

## Próximos Pasos

1. ✓ Instalar ngrok
2. ✓ Configurar token
3. ✓ Iniciar servidor + ngrok
4. ✓ Compartir URL con tu equipo
5. ✓ Monitorear desde donde estés

---

¿Preguntas? Revisa los logs en la consola de ngrok o en la DevTools del navegador (F12 → Console).
