# 🌾 AgroTasker - Sistema de IA con Predicciones Neuronales

**Profesor:** [Nombre del profesor]  
**Estudiante:** [Tu nombre]  
**Fecha:** Abril 2026  

## 📋 Resumen del Proyecto

Sistema completo de monitoreo agrícola con:
- ✅ **Predicciones con Redes Neuronales Transformer** (Multi-Head Attention)
- ✅ **Semaforización** (indicadores rojo/amarillo/verde)
- ✅ **Sistema de Alarmas** (tempranas y críticas)
- ✅ **Dashboard interactivo** con gráficos de pronóstico
- ✅ **API REST** para integración

---

## 🏗️ Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────┐
│                    DASHBOARD HTML                       │
│  (Semaforización + Alarmas + Predicciones Visuales)    │
└────────────────────┬────────────────────────────────────┘
                     │ HTTP Requests
                     ▼
┌─────────────────────────────────────────────────────────┐
│          SERVIDOR DE PREDICCIONES (Flask)              │
│              Puerto: 5000                               │
│  /api/predictions  - Predicciones actuales              │
│  /api/alarms      - Alarmas del sistema                 │
│  /api/traffic-light - Estado de semáforos              │
│  /api/health      - Estado del servidor                 │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│       MODELO TRANSFORMER (TensorFlow/Keras)            │
│                                                         │
│  Input → MultiHeadAttention(4 heads) → Dropout       │
│       → LayerNorm → FeedForward → LayerNorm            │
│  (x2 bloques de Attention)                             │
│       → Flatten → Dense(64) → Dense(32) → Dense(6)    │
│                                                         │
│  Predicción: 24 últimos valores → 6 valores futuros   │
│  Arquitectura: Transformer con Attention Mechanism    │
│  Variables: Humedad, Temp, EC, pH                     │
│  Entrenamiento: ~480 registros históricos (5 días)    │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│            DATOS DE THINGSPEAK                         │
│                                                         │
│  Canal Principal (2791076):                            │
│    • field1: Humedad Suelo (%)                         │
│    • field2: Temperatura (°C)                          │
│    • field3: EC (uS/cm)                                │
│    • field4: pH                                        │
│    • field5-7: NPK (N, P, K)                           │
│                                                         │
│  Frecuencia: 1 lectura cada 15 minutos                 │
└─────────────────────────────────────────────────────────┘
```

---

## 🚀 Inicio Rápido (3 Pasos)

### Paso 1: Abrir Terminal y Navegar
```bash
cd C:\Users\SEBASTIAN\AgroTasker_Dashboard
```

### Paso 2: Ejecutar Script de Inicio
```bash
START_IA.bat
```

Este script automáticamente:
1. ✓ Instala dependencias
2. ✓ Verifica/entrena modelo
3. ✓ Inicia servidor predicciones
4. ✓ Abre dashboard en navegador

### Paso 3: Ver Dashboard
```
Abre en navegador: file:///c:/Users/SEBASTIAN/AgroTasker_Dashboard/dashboard_ia.html
```

---

## 📊 Componentes Principales

### 1. **predictions_model.py** - Modelo de Redes Neuronales Transformer

**Características:**
- Arquitectura Transformer con Multi-Head Attention (4 heads)
- Dos bloques de Self-Attention con Feed Forward Networks
- Descarga automática de datos históricos de ThingSpeak
- Normalización MinMax (0-1)
- Predicción multi-paso (6 pasos = ~1.5 horas)
- Early stopping y Learning Rate Reduction para optimización

**Uso:**

```bash
# Entrenar nuevo modelo (primera vez o reentrenamiento)
python predictions_model.py train

# Ver predicciones actuales
python predictions_model.py

# Guardar modelos en: ./models/transformer_field1.h5, etc.
```

**Proceso de Entrenamiento:**
1. Descarga últimos ~480 registros (5 días)
2. Normaliza cada variable independientemente
3. Crea secuencias de 24 pasos
4. Entrena Transformer con 100 épocas (early stopping)
5. Guarda 4 modelos (uno por variable)
6. Estima tiempo: 3-7 minutos

### 2. **predictions_server.py** - API REST con Alarmas

**Puerto:** 5000 (http://localhost:5000)

**Endpoints Disponibles:**

#### GET `/api/predictions`
Obtiene predicciones actuales con pronóstico
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
Obtiene estado de alarmas (críticas, tempranas, normales)
```json
{
  "status": "success",
  "alarms": {
    "critical": [
      {
        "field": "field1",
        "message": "⛔ CRÍTICO: Humedad fuera de rango",
        "status": "red"
      }
    ],
    "early_warning": [...],
    "normal": [...]
  }
}
```

#### GET `/api/traffic-light`
Estado de semáforo (rojo/amarillo/verde)
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

**Características Visuales:**

1. **Encabezado**
   - Título: "AgroTasker - Monitoreo Inteligente con IA"
   - Status en vivo de datos y predicciones
   - Última actualización

2. **Centro de Alertas** (Panel amarillo)
   - Muestra alarmas críticas (🔴 rojo)
   - Alertas tempranas (🟡 amarillo)
   - Variables normales (✓ verde)

3. **Mediciones en Vivo**
   - Tarjetas con valor actual
   - Indicador de semáforo (rojo/amarillo/verde)
   - Color de fondo según estado

4. **Predicciones IA**
   - Valor actual → Próximo valor
   - Tendencia (📈 📉)
   - Pronóstico de 3 pasos

5. **Gráficos de Pronóstico**
   - 6 barras para próximas 1.5 horas
   - Altura proporcional al valor predicho
   - Uno por variable

---

## 🎨 Sistema de Semaforización

Tres estados visuales:

### 🟢 VERDE - Normal
- Valor dentro de rango seguro
- No hay tendencias peligrosas
- Acción: Monitoreo normal

### 🟡 AMARILLO - Alerta Temprana
- Valor en rango pero cerca de límite
- Predicción muestra tendencia peligrosa
- Acción: Revisar en 15-30 minutos

### 🔴 ROJO - Crítico
- Valor fuera de rango seguro
- Predicción predice superación de límites
- Acción: Intervención inmediata

**Configuración de Umbrales (en predictions_server.py):**

```python
ALARM_CONFIG = {
    'field1': {                        # Humedad
        'min': 30, 'max': 90,         # Rango crítico
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

## 🧠 Arquitectura Neural: Transformer con Attention

**¿Por qué Transformer?**

| Aspecto | Transformer | GRU | LSTM |
|--------|-------------|-----|------|
| Complejidad | Media | Simple | Compleja |
| Paralelización | ⚡ Excelente | Limitada | Limitada |
| Rendimiento | ⭐⭐⭐ | ⭐⭐ | ⭐⭐ |
| Precisión Series | ⭐⭐⭐ | ⭐⭐ | ⭐⭐ |
| Contexto Largo | ⭐⭐⭐ | ⭐⭐ | ⭐⭐ |
| Latencia | Baja | Muy Baja | Baja |

**Estructura Transformer Implementada:**
```
Entrada (24 valores históricos)
    ↓
MultiHeadAttention(4 heads) [Self-Attention]
    ↓
Dropout(0.2) + LayerNormalization
    ↓
FeedForward Network (Dense layers)
    ↓
Dropout(0.2) + LayerNormalization
    ↓
MultiHeadAttention(4 heads) [Second Attention Block]
    ↓
Dropout(0.2) + LayerNormalization
    ↓
Flatten → Dense(64) → Dense(32) [Compresión]
    ↓
Dense(6) [6 predicciones futuras]
    ↓
Salida (Pronóstico 1.5h)
```

**Ventajas del Transformer:**
- Mecanismo de Attention captura dependencias a largo plazo
- Procesamiento paralelo mucho más eficiente
- Mejor generalización en series temporales
- Escalable a más capas y heads
- State-of-the-art en ML moderno

**Variables Predichas:**
- field1: Humedad Suelo (%)
- field2: Temperatura (°C)
- field3: EC (uS/cm)
- field4: pH

---

## 📈 Instrucciones Paso a Paso para el Profesor

### 📍 PASO 1: Entorno (5 min)

```bash
# Opción A: Con venv
cd C:\Users\SEBASTIAN\AgroTasker_Dashboard
python -m venv venv
venv\Scripts\activate.bat

# Opción B: Con conda
conda create -n agrotasker python=3.11
conda activate agrotasker
```

### 📍 PASO 2: Instalar Dependencias (2 min)

```bash
pip install -r requirements.txt
```

**Paquetes principales:**
- `tensorflow==2.14.0` - Redes neuronales
- `pandas==2.0.3` - Manejo datos
- `scikit-learn==1.3.0` - Normalización
- `flask==3.0.0` - API REST
- `numpy==1.24.3` - Cálculos numéricos

### 📍 PASO 3: Entrenar Modelo (3-5 min)

```bash
python predictions_model.py train
```

**Output esperado:**
```
==================================================
ENTRENAMIENTO DE MODELO TRANSFORMER
==================================================
✓ Descargados 480 registros de ThingSpeak

🔄 Entrenando modelos Transformer...
  📊 Humedad Suelo (%): entrenando con 450 secuencias...
  ✓ Modelo Transformer guardado: ./models/transformer_field1.h5
  [similares para field2, field3, field4]

✓ Entrenamiento Transformer completado exitosamente
```

**Archivos generados:**
```
models/
  ├── transformer_field1.h5      # Modelo humedad (Transformer)
  ├── transformer_field2.h5      # Modelo temperatura (Transformer)
  ├── transformer_field3.h5      # Modelo EC (Transformer)
  ├── transformer_field4.h5      # Modelo pH (Transformer)
  └── metadata.json              # Metadatos entrenamiento
```

### 📍 PASO 4: Iniciar Servidor (2 min)

```bash
python predictions_server.py
```

**Output esperado:**
```
[STARTUP] Cargando modelos entrenados...
[STARTUP] ✓ 4 modelos cargados
[STARTUP] ✓ Predicciones iniciales generadas

============================================================
SERVIDOR DE PREDICCIONES Y ALARMAS
============================================================
🚀 Iniciando en http://0.0.0.0:5000
📊 Predicciones: http://localhost:5000/api/predictions
🚨 Alarmas: http://localhost:5000/api/alarms
🚦 Semáforo: http://localhost:5000/api/traffic-light
============================================================
```

### 📍 PASO 5: Abrir Dashboard (1 min)

```
Opción A (con servidor):
  http://localhost:5000/api - Ve a cualquier endpoint

Opción B (solo HTML):
  file:///c:/Users/SEBASTIAN/AgroTasker_Dashboard/dashboard_ia.html
```

---

## 🔧 Troubleshooting

### ❌ Error: "ModuleNotFoundError: No module named 'tensorflow'"

```bash
pip install tensorflow==2.14.0
```

### ❌ Error: "Port 5000 already in use"

```bash
# Encontrar proceso usando puerto 5000
netstat -ano | findstr :5000

# Matar proceso (reemplazar PID)
taskkill /PID <PID> /F
```

### ❌ Error: "No data from ThingSpeak"

- Verificar conexión a internet
- Verificar ID de canal (2791076)
- Esperar 15 minutos (tiempo de actualización ThingSpeak)

### ❌ Dashboard no muestra predicciones

- ¿Está corriendo predictions_server.py?
- ¿Están los modelos entrenados? (`ls models/`)
- Verificar http://localhost:5000/api/health

---

## 📊 Análisis de Resultados

### Interpretación de Predicciones

**Ejemplo: Humedad Suelo**
```
Actual: 68.40%
Pronóstico: [69.5, 70.2, 71.0, 70.8, 70.5, 69.8]
Tendencia: 📈 Aumentando
Estado: 🟢 Verde (dentro de rango 30-90%)
```

**Significado:**
- Humedad actual está en 68%
- Modelo predice aumento progresivo hasta 71%
- Permanecerá dentro de rango seguro
- No se requiere riego inmediato

### Validación del Modelo

**Indicadores de Calidad:**

1. **MAE (Mean Absolute Error):** Error promedio en predicción
   - < 5%: Excelente
   - 5-10%: Bueno
   - > 10%: Revisar datos

2. **Tendencia correcta:** ¿Predicciones siguen dirección correcta?

3. **Consistencia:** ¿Cambios graduales o saltos bruscos?

---

## 🎓 Conceptos Educativos Presentados

### 1. Machine Learning Series Temporal
- Secuencias de 24 pasos
- Normalización MinMax
- Train/validation split (80/20)

### 2. Redes Neuronales Transformer
- Self-Attention Multi-Head
- Mecanismos de Atención (4 cabezas)
- Arquitectura Encoder-like con 2 bloques

### 3. Sistema de Alarmas
- Umbrales dobles (crítico + temprano)
- Análisis de tendencias
- Lógica de semáforos

### 4. API REST
- Endpoints RESTful
- CORS para integración frontend
- Documentación automática

### 5. Stack Tecnológico
- Python + TensorFlow/Keras (Transformer)
- Flask para API
- HTML5 + Vanilla JS para frontend

---

## 📝 Notas para la Presentación

**Puntos Clave a Destacar:**

1. ✅ **Predicciones en Tiempo Real** - Modelo actualiza cada 5 minutos
2. ✅ **Semaforización Automática** - Sin intervención manual
3. ✅ **Alarmas Inteligentes** - Diferencia entre crítico y temprano
4. ✅ **Datos Reales** - Desde ThingSpeak, no dummy data
5. ✅ **GRU Optimizado** - Más ligero que LSTM, igual precisión
6. ✅ **Integración Completa** - Backend + Frontend + API

**Demostración Recomendada:**

1. Mostrar Dashboard con semaforización verde
2. Explicar predicciones en gráfico
3. Simular alarma (modificar umbral en config)
4. Mostrar API endpoints en Postman/curl
5. Explicar arquitectura GRU

---

## 📚 Archivos del Proyecto

```
AgroTasker_Dashboard/
├── predictions_model.py          # Modelo GRU
├── predictions_server.py         # Servidor Flask + Alarmas
├── dashboard_ia.html             # Dashboard con semáforos
├── dashboard_realtime_dual.html  # Dashboard dual (datos crudos)
├── requirements.txt              # Dependencias Python
├── START_IA.bat                  # Script de inicio automático
├── README_IA.md                  # Este archivo
├── models/                       # Modelos entrenados
│   ├── gru_field1.h5
│   ├── gru_field2.h5
│   ├── gru_field3.h5
│   ├── gru_field4.h5
│   └── metadata.json
├── api/                          # APIs ThingSpeak
└── js/                           # Scripts JavaScript
    └── app.js
```

---

## ✅ Checklist de Validación

- [ ] Python 3.11+ instalado
- [ ] requirements.txt instalado (`pip install -r requirements.txt`)
- [ ] TensorFlow funciona (`python -c "import tensorflow; print(tensorflow.__version__)"`)
- [ ] Modelo entrenado (`ls models/gru_*.h5`)
- [ ] Servidor iniciado sin errores
- [ ] API responde (`curl http://localhost:5000/api/health`)
- [ ] Dashboard carga en navegador
- [ ] Semaforización visible
- [ ] Predicciones mostradas

---

## 🎯 Conclusión

Este sistema demuestra:
1. **IA Aplicada** a agricultura real
2. **Predicción Neural** con GRU
3. **Sistema de Alarmas** inteligente
4. **Interfaz Completa** profesional
5. **Integración Full-Stack** Python + JS

**Tiempo Total de Configuración:** ~15 minutos  
**Tiempo de Entrenamiento:** ~3-5 minutos  
**Preparado para Presentación:** ✅ Listo

---

**¿Preguntas?** Revisar troubleshooting o ejecutar:
```bash
python predictions_server.py --debug
```

---

*Documento preparado para presentación académica del proyecto AgroTasker*
