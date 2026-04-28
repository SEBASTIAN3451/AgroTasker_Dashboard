# 🌱 AgroTasker - Dashboard Inteligente de Cultivo de Mango

Sistema avanzado de monitoreo en tiempo real para cultivos de mango con predicciones inteligentes, control automático de riego y gestión de tareas agrícolas.

## 🚀 Características Principales

### 📊 Monitoreo en Tiempo Real
- **Sensores del Suelo**: Humedad, temperatura, pH, conductividad, nutrientes (N, P, K)
- **Sensores Meteorológicos**: Temperatura, humedad, viento, precipitación, presión
- **Sensores Especializados**: Potencial mátrico a diferentes profundidades, índice UV
- Actualización cada 20 segundos
- Caché de datos para optimizar uso de API (60 segundos)

### 🔮 Predicciones Inteligentes
- **Cosecha**: Estimación automática basada en ciclo de floración (210 días)
- **Necesidades de Riego**: Cálculo dinámico según humedad y temperatura
- **Detección de Enfermedades**: Identificación de riesgos (Antracnosis, Oídio, estrés por calor)
- **Recomendaciones de Nutrientes**: Análisis de N, P, K en el suelo
- Actualizaciones en tiempo real basadas en datos de sensores

### 💧 Control de Riego Automático
- **Riego Manual**: Toggle para activar/desactivar inmediatamente
- **Riego Programado**: Configuración de horarios (diario, cada 2 días, semanal)
- **Riego Inteligente**: Activación automática según niveles de humedad
- **Historial Completo**: Registro de todas las operaciones de riego
- **Recomendaciones Dinámicas**: Sugerencias basadas en condiciones actuales

### ✅ Gestión de Tareas Agrícolas
- **5 Tipos de Tareas**: Riego, Fertilización, Poda, Fumigación, Cosecha
- **Prioridades**: Baja, Normal, Alta
- **Calendario**: Visualización de próximas tareas (7 días)
- **Estadísticas**: Seguimiento de completadas, pendientes, porcentaje de avance
- **Persistencia**: Almacenamiento en localStorage
- **Alertas de Urgencia**: Resalte para tareas cercanas al vencimiento

### 🚨 Sistema de Alertas
- **Alertas Automáticas**: Condiciones críticas detalladas en tiempo real
- **Configuración Personalizada**: Ajusta umbrales de temperatura, humedad, pH
- **Niveles de Severidad**: Crítico, Advertencia, Información
- **Historial de Alertas**: Registro de eventos

### 📄 Reportes y Exportación
- **PDF**: Descarga de reportes en formato PDF
- **CSV**: Exportación de datos históricos para análisis
- **Impresión**: Opción de imprimir dashboard directamente

## 🎯 Valores Óptimos por Defecto (Ajustables)

```
🌡️ Temperatura:     24-32°C
💧 Humedad Aire:    50-75%
⚗️ pH Suelo:        5.5-7.0
🌿 Humedad Suelo:   35-60%
```

## 📱 Versiones Disponibles

### 1. Dashboard Simple (`dashboard_simple.html`)
- Ligero y rápido
- Interfaz minimalista
- Ideal para conexiones lentas
- Tamaño: ~1KB

### 2. Dashboard Avanzado (`dashboard_advanced.html`)
- Todas las características
- Interfaz completa con tabs
- Gráficos y predicciones
- Tamaño: ~100KB

### 3. Dashboard Original (`dashboard.html`)
- Versión original completa
- Múltiples vistas
- Compatible con todos los navegadores
- Tamaño: ~928 líneas

### 4. Menú de Selección (`index-menu.html`)
- Pantalla inicial
- Selecciona tu versión preferida
- Información de estado

## 🔧 Instalación y Configuración

### Requisitos
- Python 3.11+
- ngrok (para acceso remoto)
- Navegador web moderno

### Pasos de Instalación

1. **Instalar Python**
   ```powershell
   winget install Python.Python.3.11
   ```

2. **Instalar ngrok**
   ```powershell
   winget install ngrok.ngrok
   ```

3. **Configurar ngrok**
   ```powershell
   ngrok config add-authtoken 34OVLY528y5Bxo9hAUjhPZ5rE0m_5PNiZHZbqTSbsF4d6qeRP
   ```

4. **Iniciar el servidor**
   ```powershell
   python server_simple.py
   ```

5. **En otra terminal, iniciar ngrok**
   ```powershell
   ngrok http 8080 --region us
   ```

6. **Acceder al dashboard**
   - Local: `http://localhost:8080/dashboard_advanced.html`
   - Remoto: Tu URL de ngrok + `/dashboard_advanced.html`

## 📡 APIs Conectadas

### ThingSpeak Channels
- **Canal de Suelo** (2791076): Humedad, temperatura, pH, conductividad, N, P, K
- **Canal Meteorológico** (2791069): Viento, precipitación, temperatura aire, humedad, presión
- **Canal Mátrico/UV** (2906294): Potencial mátrico 30/60cm, índice UV

### Proxy Server
- `http://localhost:8080/api/thingspeak/soil`
- `http://localhost:8080/api/thingspeak/weather`
- `http://localhost:8080/api/thingspeak/matric_uv`

## 💾 Almacenamiento Local

Las siguientes características usan `localStorage` (datos persistentes en el navegador):

```javascript
agrotasker_tasks              // Tareas agrícolas
irrigation_active             // Estado de riego
irrigation_schedule          // Programación de riego
irrigation_history           // Historial de riego
agrotasker_alert_settings    // Configuración de alertas
sensorHistory                // Histórico de sensores
```

## 🎨 Personalización

### Cambiar Colores
Edita los valores CSS en la sección `<style>`:
```css
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
```

### Ajustar Intervalo de Actualización
En el archivo HTML principal:
```javascript
setInterval(fetchData, 20000); // 20 segundos
```

### Modificar Rangos Óptimos
En el código JavaScript:
```javascript
alertSettings = {
    tempMin: 24, tempMax: 32,
    humidityMin: 50, humidityMax: 75,
    phMin: 5.5, phMax: 7.0
}
```

## 📊 Módulos JavaScript

### `js/tasks.js`
Clase `AgriculturalTasks` para gestión de tareas:
- `addTask(name, date, type, priority)`
- `getUpcoming(days)`
- `getStatistics()`
- `completeTask(id)`
- `deleteTask(id)`

### `js/irrigation.js`
Clase `IrrigationControl` para riego:
- `toggleIrrigation()`
- `scheduleIrrigation(startTime, duration, daysOfWeek)`
- `autoIrrigation(humidity)`
- `logEvent(type, description)`
- `getStatistics(days)`

### `js/predictions.js`
Clase `PredictionEngine` para predicciones:
- `predictHarvest(floweringDate)`
- `predictWaterNeeds(humidity, temperature)`
- `predictDiseases(humidity, temperature)`
- `predictNutrientNeeds(nitrogen, phosphorus, potassium)`

### `js/reports.js`
Objeto `ReportGenerator` para exportación:
- `generatePDF()`
- `exportToCSV()`

## 🐛 Solución de Problemas

### Dashboard muestra "Esperando datos..."
1. Verifica que el servidor esté corriendo: `Get-Process python`
2. Verifica que ngrok esté activo: `ngrok status`
3. Verifica conexión a ThingSpeak: Abre en navegador `/api/thingspeak/soil`

### Datos vacíos o nulos
- El servidor filtra automáticamente valores cero/null
- Verifica que los sensores estén activos en ThingSpeak
- Espera 20 segundos para la próxima actualización

### Errores CORS
- El servidor `server_simple.py` incluye headers CORS
- Si persiste, verifica que no hay múltiples instancias de Python

### ngrok URL cambió
- ngrok crea una URL temporal cuando se reinicia
- La URL autenticada es más estable (usa `--region us`)
- Guarda la URL en bookmarks

## 📈 Casos de Uso

### Monitoreo Diario
1. Revisa el dashboard por la mañana (6-7 AM)
2. Verifica alertas de humedad/temperatura
3. Revisa predicciones de riego
4. Marca tareas completadas

### Decisiones de Riego
1. Lee "Necesidades de Riego"
2. Verifica humedad actual
3. Activa riego manual o depende de automático
4. Registra tiempo en historial

### Prevención de Enfermedades
1. Monitorea "Predicción de Enfermedades"
2. Sigue recomendaciones antes de que ocurran
3. Ajusta estrategia de fumigación

### Planificación de Cosecha
1. Anota fecha de floración manualmente
2. Revisa estimación automática
3. Prepara recursos con 2 semanas de anticipación

## 📞 Soporte y Mantenimiento

### Backup de Datos
```powershell
# Exporta datos a CSV desde dashboard
# O accede directamente a localStorage
```

### Limpieza de Datos Antiguos
```javascript
// En consola del navegador
localStorage.removeItem('agrotasker_tasks');
localStorage.removeItem('irrigation_history');
```

### Actualización
1. Descarga nuevos archivos
2. Reemplaza en carpeta del proyecto
3. Reinicia servidor
4. Limpia caché del navegador (Ctrl+Shift+Del)

## 🎓 Mango Cultivation Reference

**Ciclo de Cultivo**
- Floración: Enero-Febrero
- Desarrollo de fruto: Marzo-Junio
- Cosecha: Julio-Septiembre
- Descanso: Octubre-Diciembre

**Rangos de Cultivo**
- Temperatura: 24-32°C (mínimo 15°C)
- Humedad: 50-75% (evita >80%)
- pH: 5.5-7.0 (preferible 5.5-6.5)
- Agua: 40-60mm por semana

**Nutrientes (mg/kg en suelo)**
- Nitrógeno (N): 200-300
- Fósforo (P): 40-60
- Potasio (K): 180-250

## 📝 Changelog

### Versión 2.0 (Actual)
- ✅ Dashboard avanzado con tabs
- ✅ Predicciones inteligentes
- ✅ Control de riego automático
- ✅ Gestión completa de tareas
- ✅ Sistema de alertas configurable
- ✅ Exportación PDF/CSV

### Versión 1.0
- Dashboard simple
- Monitoreo básico
- Alertas estáticas

## 📄 Licencia
Proyecto de código abierto para agricultura inteligente

## 👨‍🌾 Autor
Sebastian - AgroTasker Project

---

**¿Necesitas ayuda?** Revisa los registros en la consola del navegador (F12 → Console)
