# ðŸŒ¾ AgroTasker - Sistema de IA con Predicciones Neuronales

**Profesor:** [Nombre del profesor]  
**Estudiante:** [Tu nombre]  
**Fecha:** Abril 2026  

## ðŸ“‹ Resumen del Proyecto

Sistema completo de monitoreo agrÃ­cola con:
- âœ… **Predicciones con Redes Neuronales Transformer** (Multi-Head Attention)
- âœ… **SemaforizaciÃ³n** (indicadores rojo/amarillo/verde)
- âœ… **Sistema de Alarmas** (tempranas y crÃ­ticas)
- âœ… **Dashboard interactivo** con grÃ¡ficos de pronÃ³stico
- âœ… **API REST** para integraciÃ³n

---

## ðŸ—ï¸ Arquitectura del Sistema

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚                    DASHBOARD HTML                       â”‚
â”‚  (SemaforizaciÃ³n + Alarmas + Predicciones Visuales)    â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                     â”‚ HTTP Requests
                     â–¼
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚          SERVIDOR DE PREDICCIONES (Flask)              â”‚
â”‚              Puerto: 5000                               â”‚
â”‚  /api/predictions  - Predicciones actuales              â”‚
â”‚  /api/alarms      - Alarmas del sistema                 â”‚
â”‚  /api/traffic-light - Estado de semÃ¡foros              â”‚
â”‚  /api/health      - Estado del servidor                 â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                     â”‚
                     â–¼
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚       MODELO TRANSFORMER (TensorFlow/Keras)            â”‚
â”‚                                                         â”‚
â”‚  Input â†’ MultiHeadAttention(4 heads) â†’ Dropout       â”‚
â”‚       â†’ LayerNorm â†’ FeedForward â†’ LayerNorm            â”‚
â”‚  (x2 bloques de Attention)                             â”‚
â”‚       â†’ Flatten â†’ Dense(64) â†’ Dense(32) â†’ Dense(6)    â”‚
â”‚                                                         â”‚
â”‚  PredicciÃ³n: 24 Ãºltimos valores â†’ 6 valores futuros   â”‚
â”‚  Arquitectura: Transformer con Attention Mechanism    â”‚
â”‚  Variables: Humedad, Temp, EC, pH                     â”‚
â”‚  Entrenamiento: ~480 registros histÃ³ricos (5 dÃ­as)    â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                     â”‚
                     â–¼
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚            DATOS DE THINGSPEAK                         â”‚
â”‚                                                         â”‚
â”‚  Canal Principal (2791076):                            â”‚
â”‚    â€¢ field1: Humedad Suelo (%)                         â”‚
â”‚    â€¢ field2: Temperatura (Â°C)                          â”‚
â”‚    â€¢ field3: EC (uS/cm)                                â”‚
â”‚    â€¢ field4: pH                                        â”‚
â”‚    â€¢ field5-7: NPK (N, P, K)                           â”‚
â”‚                                                         â”‚
â”‚  Frecuencia: 1 lectura cada 15 minutos                 â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

---

## ðŸš€ Inicio RÃ¡pido (3 Pasos)

### Paso 1: Abrir Terminal y Navegar
```bash
cd C:\Users\SEBASTIAN\AgroTasker_Dashboard
```

### Paso 2: Ejecutar Script de Inicio
```bash
START_IA.bat
```

Este script automÃ¡ticamente:
1. âœ“ Instala dependencias
2. âœ“ Verifica/entrena modelo
3. âœ“ Inicia servidor predicciones
4. âœ“ Abre dashboard en navegador

### Paso 3: Ver Dashboard
```
Abre en navegador: file:///c:/Users/SEBASTIAN/AgroTasker_Dashboard/dashboard_ia.html
```

---

## ðŸ“Š Componentes Principales

### 1. **predictions_model.py** - Modelo de Redes Neuronales Transformer

**CaracterÃ­sticas:**
- Arquitectura Transformer con Multi-Head Attention (4 heads)
- Dos bloques de Self-Attention con Feed Forward Networks
- Descarga automÃ¡tica de datos histÃ³ricos de ThingSpeak
- NormalizaciÃ³n MinMax (0-1)
- PredicciÃ³n multi-paso (6 pasos = ~1.5 horas)
- Early stopping y Learning Rate Reduction para optimizaciÃ³n

**Uso:**

```bash
# Entrenar nuevo modelo (primera vez o reentrenamiento)
python predictions_model.py train

# Ver predicciones actuales
python predictions_model.py

# Guardar modelos en: ./models/transformer_field1.h5, etc.
```

**Proceso de Entrenamiento:**
1. Descarga Ãºltimos ~480 registros (5 dÃ­as)
2. Normaliza cada variable independientemente
3. Crea secuencias de 24 pasos
4. Entrena Transformer con 100 Ã©pocas (early stopping)
5. Guarda 4 modelos (uno por variable)
6. Estima tiempo: 3-7 minutos

### 2. **predictions_server.py** - API REST con Alarmas

**Puerto:** 5000 (http://localhost:5000)

**Endpoints Disponibles:**

#### GET `/api/predictions`
Obtiene predicciones actuales con pronÃ³stico
```json
{
  "status": "success",
  "data": {
    "field1": {
      "field_name": "Humedad Suelo (%)",
      "current": 68.40,
      "forecast": [69.5, 70.2, 71.0, 70.8, 70.5, 69.8]
    },
    ...
  },
  "timestamp": "2026-04-28T17:06:49.123456"
}
```

#### GET `/api/alarms`
Obtiene estado de alarmas (crÃ­ticas, tempranas, normales)
```json
{
  "status": "success",
  "alarms": {
    "critical": [
      {
        "field": "field1",
        "message": "â›” CRÃTICO: Humedad fuera de rango",
        "status": "red"
      }
    ],
    "early_warning": [...],
    "normal": [...]
  }
}
```

#### GET `/api/traffic-light`
Estado de semÃ¡foro (rojo/amarillo/verde)
```json
{
  "lights": {
    "field1": "green",
    "field2": "yellow",
    "field3": "red",
    "field4": "green"
  }
}
```

#### GET `/api/health`
Estado general del servidor
```json
{
  "status": "ok",
  "models_loaded": 4,
  "has_predictions": true,
  "last_update": "2026-04-28T17:06:49.123456"
}
```

#### POST `/api/train`
Inicia entrenamiento en background (respuesta inmediata)
```bash
curl -X POST http://localhost:5000/api/train
```

#### GET/PUT `/api/config/alarms`
Obtiene/actualiza umbrales de alarmas

### 3. **dashboard_ia.html** - Panel de Control

**CaracterÃ­sticas Visuales:**

1. **Encabezado**
   - TÃ­tulo: "AgroTasker - Monitoreo Inteligente con IA"
   - Status en vivo de datos y predicciones
   - Ãšltima actualizaciÃ³n

2. **Centro de Alertas** (Panel amarillo)
   - Muestra alarmas crÃ­ticas (ðŸ”´ rojo)
   - Alertas tempranas (ðŸŸ¡ amarillo)
   - Variables normales (âœ“ verde)

3. **Mediciones en Vivo**
   - Tarjetas con valor actual
   - Indicador de semÃ¡foro (rojo/amarillo/verde)
   - Color de fondo segÃºn estado

4. **Predicciones IA**
   - Valor actual â†’ PrÃ³ximo valor
   - Tendencia (ðŸ“ˆ ðŸ“‰)
   - PronÃ³stico de 3 pasos

5. **GrÃ¡ficos de PronÃ³stico**
   - 6 barras para prÃ³ximas 1.5 horas
   - Altura proporcional al valor predicho
   - Uno por variable

---

## ðŸŽ¨ Sistema de SemaforizaciÃ³n

Tres estados visuales:

### ðŸŸ¢ VERDE - Normal
- Valor dentro de rango seguro
- No hay tendencias peligrosas
- AcciÃ³n: Monitoreo normal

### ðŸŸ¡ AMARILLO - Alerta Temprana
- Valor en rango pero cerca de lÃ­mite
- PredicciÃ³n muestra tendencia peligrosa
- AcciÃ³n: Revisar en 15-30 minutos

### ðŸ”´ ROJO - CrÃ­tico
- Valor fuera de rango seguro
- PredicciÃ³n predice superaciÃ³n de lÃ­mites
- AcciÃ³n: IntervenciÃ³n inmediata

**ConfiguraciÃ³n de Umbrales (en predictions_server.py):**

```python
ALARM_CONFIG = {
    'field1': {                        # Humedad
        'min': 30, 'max': 90,         # Rango crÃ­tico
        'early_min': 40, 'early_max': 80  # Rango amarillo
    },
    'field2': {                        # Temperatura
        'min': 10, 'max': 35,
        'early_min': 15, 'early_max': 30
    },
    'field3': {                        # EC
        'min': 200, 'max': 2000,
        'early_min': 300, 'early_max': 1800
    },
    'field4': {                        # pH
        'min': 5.5, 'max': 7.5,
        'early_min': 5.8, 'early_max': 7.2
    }
}
```

---

## ðŸ§  Arquitectura Neural: Transformer con Attention

**Â¿Por quÃ© Transformer?**

| Aspecto | ImplementaciÃ³n actual |
|--------|------------------------|
| Arquitectura | Transformer encoder-like |
| AtenciÃ³n | Multi-Head Attention con 4 heads |
| Entrada | 24 mediciones histÃ³ricas |
| Salida | 6 predicciones futuras |
| RegularizaciÃ³n | Dropout + LayerNormalization |
| OptimizaciÃ³n | Early stopping + ReduceLROnPlateau |

**Estructura Transformer Implementada:**
```
Entrada (24 valores histÃ³ricos)
    â†“
MultiHeadAttention(4 heads) [Self-Attention]
    â†“
Dropout(0.2) + LayerNormalization
    â†“
FeedForward Network (Dense layers)
    â†“
Dropout(0.2) + LayerNormalization
    â†“
MultiHeadAttention(4 heads) [Second Attention Block]
    â†“
Dropout(0.2) + LayerNormalization
    â†“
Flatten â†’ Dense(64) â†’ Dense(32) [CompresiÃ³n]
    â†“
Dense(6) [6 predicciones futuras]
    â†“
Salida (PronÃ³stico 1.5h)
```

**Ventajas del Transformer:**
- Mecanismo de Attention captura dependencias a largo plazo
- Procesamiento paralelo mucho mÃ¡s eficiente
- Mejor generalizaciÃ³n en series temporales
- Escalable a mÃ¡s capas y heads
- State-of-the-art en ML moderno

**Variables Predichas:**
- field1: Humedad Suelo (%)
- field2: Temperatura (Â°C)
- field3: EC (uS/cm)
- field4: pH

---

## ðŸ“ˆ Instrucciones Paso a Paso para el Profesor

### ðŸ“ PASO 1: Entorno (5 min)

```bash
# OpciÃ³n A: Con venv
cd C:\Users\SEBASTIAN\AgroTasker_Dashboard
python -m venv venv
venv\Scripts\activate.bat

# OpciÃ³n B: Con conda
conda create -n agrotasker python=3.11
conda activate agrotasker
```

### ðŸ“ PASO 2: Instalar Dependencias (2 min)

```bash
pip install -r requirements.txt
```

**Paquetes principales:**
- `tensorflow==2.14.0` - Redes neuronales
- `pandas==2.0.3` - Manejo datos
- `scikit-learn==1.3.0` - NormalizaciÃ³n
- `flask==3.0.0` - API REST
- `numpy==1.24.3` - CÃ¡lculos numÃ©ricos

### ðŸ“ PASO 3: Entrenar Modelo (3-5 min)

```bash
python predictions_model.py train
```

**Output esperado:**
```
==================================================
ENTRENAMIENTO DE MODELO TRANSFORMER
==================================================
âœ“ Descargados 480 registros de ThingSpeak

ðŸ”„ Entrenando modelos Transformer...
  ðŸ“Š Humedad Suelo (%): entrenando con 450 secuencias...
  âœ“ Modelo Transformer guardado: ./models/transformer_field1.h5
  [similares para field2, field3, field4]

âœ“ Entrenamiento Transformer completado exitosamente
```

**Archivos generados:**
```
models/
  â”œâ”€â”€ transformer_field1.h5      # Modelo humedad (Transformer)
  â”œâ”€â”€ transformer_field2.h5      # Modelo temperatura (Transformer)
  â”œâ”€â”€ transformer_field3.h5      # Modelo EC (Transformer)
  â”œâ”€â”€ transformer_field4.h5      # Modelo pH (Transformer)
  â””â”€â”€ metadata.json              # Metadatos entrenamiento
```

### ðŸ“ PASO 4: Iniciar Servidor (2 min)

```bash
python predictions_server.py
```

**Output esperado:**
```
[STARTUP] Cargando modelos entrenados...
[STARTUP] âœ“ 4 modelos cargados
[STARTUP] âœ“ Predicciones iniciales generadas

============================================================
SERVIDOR DE PREDICCIONES Y ALARMAS
============================================================
ðŸš€ Iniciando en http://0.0.0.0:5000
ðŸ“Š Predicciones: http://localhost:5000/api/predictions
ðŸš¨ Alarmas: http://localhost:5000/api/alarms
ðŸš¦ SemÃ¡foro: http://localhost:5000/api/traffic-light
============================================================
```

### ðŸ“ PASO 5: Abrir Dashboard (1 min)

```
OpciÃ³n A (con servidor):
  http://localhost:5000/api - Ve a cualquier endpoint

OpciÃ³n B (solo HTML):
  file:///c:/Users/SEBASTIAN/AgroTasker_Dashboard/dashboard_ia.html
```

---

## ðŸ”§ Troubleshooting

### âŒ Error: "ModuleNotFoundError: No module named 'tensorflow'"

```bash
pip install tensorflow==2.14.0
```

### âŒ Error: "Port 5000 already in use"

```bash
# Encontrar proceso usando puerto 5000
netstat -ano | findstr :5000

# Matar proceso (reemplazar PID)
taskkill /PID <PID> /F
```

### âŒ Error: "No data from ThingSpeak"

- Verificar conexiÃ³n a internet
- Verificar ID de canal (2791076)
- Esperar 15 minutos (tiempo de actualizaciÃ³n ThingSpeak)

### âŒ Dashboard no muestra predicciones

- Â¿EstÃ¡ corriendo predictions_server.py?
- Â¿EstÃ¡n los modelos entrenados? (`ls models/`)
- Verificar http://localhost:5000/api/health

---

## ðŸ“Š AnÃ¡lisis de Resultados

### InterpretaciÃ³n de Predicciones

**Ejemplo: Humedad Suelo**
```
Actual: 68.40%
PronÃ³stico: [69.5, 70.2, 71.0, 70.8, 70.5, 69.8]
Tendencia: ðŸ“ˆ Aumentando
Estado: ðŸŸ¢ Verde (dentro de rango 30-90%)
```

**Significado:**
- Humedad actual estÃ¡ en 68%
- Modelo predice aumento progresivo hasta 71%
- PermanecerÃ¡ dentro de rango seguro
- No se requiere riego inmediato

### ValidaciÃ³n del Modelo

**Indicadores de Calidad:**

1. **MAE (Mean Absolute Error):** Error promedio en predicciÃ³n
   - < 5%: Excelente
   - 5-10%: Bueno
   - > 10%: Revisar datos

2. **Tendencia correcta:** Â¿Predicciones siguen direcciÃ³n correcta?

3. **Consistencia:** Â¿Cambios graduales o saltos bruscos?

---

## ðŸŽ“ Conceptos Educativos Presentados

### 1. Machine Learning Series Temporal
- Secuencias de 24 pasos
- NormalizaciÃ³n MinMax
- Train/validation split (80/20)

### 2. Redes Neuronales Transformer
- Self-Attention Multi-Head
- Mecanismos de AtenciÃ³n (4 cabezas)
- Arquitectura Encoder-like con 2 bloques

### 3. Sistema de Alarmas
- Umbrales dobles (crÃ­tico + temprano)
- AnÃ¡lisis de tendencias
- LÃ³gica de semÃ¡foros

### 4. API REST
- Endpoints RESTful
- CORS para integraciÃ³n frontend
- DocumentaciÃ³n automÃ¡tica

### 5. Stack TecnolÃ³gico
- Python + TensorFlow/Keras (Transformer)
- Flask para API
- HTML5 + Vanilla JS para frontend

---

## ðŸ“ Notas para la PresentaciÃ³n

**Puntos Clave a Destacar:**

1. âœ… **Predicciones en Tiempo Real** - Modelo actualiza cada 5 minutos
2. âœ… **SemaforizaciÃ³n AutomÃ¡tica** - Sin intervenciÃ³n manual
3. âœ… **Alarmas Inteligentes** - Diferencia entre crÃ­tico y temprano
4. âœ… **Datos Reales** - Desde ThingSpeak, no dummy data
5. âœ… **Transformer Optimizado** - Multi-Head Attention para series temporales
6. âœ… **IntegraciÃ³n Completa** - Backend + Frontend + API

**DemostraciÃ³n Recomendada:**

1. Mostrar Dashboard con semaforizaciÃ³n verde
2. Explicar predicciones en grÃ¡fico
3. Simular alarma (modificar umbral en config)
4. Mostrar API endpoints en Postman/curl
5. Explicar arquitectura Transformer

---

## ðŸ“š Archivos del Proyecto

```
AgroTasker_Dashboard/
â”œâ”€â”€ predictions_model.py          # Modelo Transformer
â”œâ”€â”€ predictions_server.py         # Servidor Flask + Alarmas
â”œâ”€â”€ dashboard_ia.html             # Dashboard con semÃ¡foros
â”œâ”€â”€ dashboard_realtime_dual.html  # Dashboard dual (datos crudos)
â”œâ”€â”€ requirements.txt              # Dependencias Python
â”œâ”€â”€ START_IA.bat                  # Script de inicio automÃ¡tico
â”œâ”€â”€ README_IA.md                  # Este archivo
â”œâ”€â”€ models/                       # Modelos entrenados
â”‚   â”œâ”€â”€ transformer_field1.h5
â”‚   â”œâ”€â”€ transformer_field2.h5
â”‚   â”œâ”€â”€ transformer_field3.h5
â”‚   â”œâ”€â”€ transformer_field4.h5
â”‚   â””â”€â”€ metadata.json
â”œâ”€â”€ api/                          # APIs ThingSpeak
â””â”€â”€ js/                           # Scripts JavaScript
    â””â”€â”€ app.js
```

---

## âœ… Checklist de ValidaciÃ³n

- [ ] Python 3.11+ instalado
- [ ] requirements.txt instalado (`pip install -r requirements.txt`)
- [ ] TensorFlow funciona (`python -c "import tensorflow; print(tensorflow.__version__)"`)
- [ ] Modelo entrenado (`ls models/transformer_*.h5`)
- [ ] Servidor iniciado sin errores
- [ ] API responde (`curl http://localhost:5000/api/health`)
- [ ] Dashboard carga en navegador
- [ ] SemaforizaciÃ³n visible
- [ ] Predicciones mostradas

---

## ðŸŽ¯ ConclusiÃ³n

Este sistema demuestra:
1. **IA Aplicada** a agricultura real
2. **PredicciÃ³n Neural** con Transformer
3. **Sistema de Alarmas** inteligente
4. **Interfaz Completa** profesional
5. **IntegraciÃ³n Full-Stack** Python + JS

**Tiempo Total de ConfiguraciÃ³n:** ~15 minutos  
**Tiempo de Entrenamiento:** ~3-5 minutos  
**Preparado para PresentaciÃ³n:** âœ… Listo

---

**Â¿Preguntas?** Revisar troubleshooting o ejecutar:
```bash
python predictions_server.py --debug
```

---

*Documento preparado para presentaciÃ³n acadÃ©mica del proyecto AgroTasker*

