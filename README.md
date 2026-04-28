# 🌾 AgroTasker Dashboard - Sistema de IA con Predicciones Neuronales

![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen)
![Python](https://img.shields.io/badge/Python-3.11-blue)
![TensorFlow](https://img.shields.io/badge/TensorFlow-2.14-orange)
![License](https://img.shields.io/badge/License-MIT-green)

> **Sistema completo de monitoreo agrícola** con predicciones de redes neuronales GRU, semaforización inteligente y alarmas automáticas.

---

## 📋 Contenido del Repositorio

### 🤖 **Componentes IA**

- **`predictions_model.py`** - Modelo GRU (Gated Recurrent Unit)
  - Descarga datos históricos de ThingSpeak
  - Entrena 4 modelos independientes
  - Predice 6 pasos adelante (~1.5 horas)
  - Guardia modelos en `./models/gru_*.h5`

- **`predictions_server.py`** - Servidor Flask con API REST
  - Puerto 5000
  - Endpoints: `/api/predictions`, `/api/alarms`, `/api/traffic-light`
  - Sistema automático de alarmas (tempranas + críticas)
  - Semaforización en tiempo real 🟢🟡🔴

### 📊 **Dashboards**

- **`dashboard_ia.html`** ⭐ **Principal - CON IA**
  - Semaforización visual completa
  - Centro de alertas y alarmas
  - Mediciones en vivo
  - Predicciones IA con gráficos
  - Pronóstico de 1.5 horas

- **`dashboard_realtime_dual.html`** - Dual ThingSpeak
  - Datos crudos de dos canales
  - Sin predicciones

### 📁 **Estructura**

```
AgroTasker_Dashboard/
├── 🤖 predictions_model.py       # Modelo GRU
├── 🚀 predictions_server.py      # Servidor + Alarmas
├── 📊 dashboard_ia.html          # Dashboard IA (USAR ESTE)
├── 📝 README_IA.md               # Documentación académica
├── 🔧 START_IA.bat              # Script inicio automático
├── 📋 requirements.txt           # Dependencias Python
├── models/                       # Modelos entrenados (4 GRU)
│   ├── gru_field1.h5            # Humedad Suelo
│   ├── gru_field2.h5            # Temperatura
│   ├── gru_field3.h5            # EC (Conductividad)
│   ├── gru_field4.h5            # pH
│   └── metadata.json            # Info entrenamiento
├── js/                          # JavaScript utilities
├── css/                         # Estilos
└── api/                         # APIs ThingSpeak
```

---

## 🚀 Inicio Rápido

### Opción 1: Script Automático (Recomendado)

```bash
cd C:\Users\SEBASTIAN\AgroTasker_Dashboard
START_IA.bat
```

El script automáticamente:
- ✓ Instala dependencias
- ✓ Verifica/entrena modelo
- ✓ Inicia servidor (puerto 5000)
- ✓ Abre dashboard en navegador

### Opción 2: Manual

```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Entrenar modelo (primera vez)
python predictions_model.py train

# 3. Iniciar servidor
python predictions_server.py

# 4. Abrir en navegador
file:///c:/Users/SEBASTIAN/AgroTasker_Dashboard/dashboard_ia.html
```

---

## 📊 Dashboard en Vivo

**URL Local:**
```
file:///c:/Users/SEBASTIAN/AgroTasker_Dashboard/dashboard_ia.html
```

**Con servidor activo:**
```
http://localhost:5000/api/predictions
http://localhost:5000/api/alarms
http://localhost:5000/api/traffic-light
```

### Características Visuales

🟢 **Verde** - Medición normal, dentro de rango seguro

🟡 **Amarillo** - Alerta temprana, tendencia peligrosa detectada

🔴 **Rojo** - Crítico, fuera de rango o predicción excede límite

---

## 🧠 Arquitectura del Modelo

### GRU (Gated Recurrent Unit)

```
Entrada (24 valores históricos)
    ↓
GRU(64) + Dropout(0.2)
    ↓
GRU(32) + Dropout(0.2)
    ↓
Dense(16) + Dense(6)
    ↓
Salida (6 predicciones futuras)
```

### Ventajas sobre LSTM

| Métrica | GRU | LSTM |
|---------|-----|------|
| Parámetros | -25% | Mayor |
| Entrenamiento | ⚡ Rápido | Lento |
| Memoria | Bajo | Alto |
| Precisión | Similar | Similar |

### Datos de Entrenamiento

- **Fuente:** ThingSpeak Canal 2791076
- **Historial:** 480 registros (~5 días)
- **Frecuencia:** 1 lectura cada 15 minutos
- **Variables:** Humedad, Temperatura, EC, pH

---

## 🚨 Sistema de Alarmas

### Alarmas Tempranas 🟡

Detectadas cuando:
- Valor actual normal pero cerca de límite
- Predicción muestra tendencia hacia rango peligroso

**Acción:** Revisar en 15-30 minutos

### Alarmas Críticas 🔴

Detectadas cuando:
- Valor actual fuera de rango seguro
- Predicción predice superación de límites

**Acción:** Intervención inmediata

### Configuración de Umbrales

```python
# En predictions_server.py
ALARM_CONFIG = {
    'field1': {               # Humedad
        'min': 30, 'max': 90,
        'early_min': 40, 'early_max': 80
    },
    'field2': {               # Temperatura
        'min': 10, 'max': 35,
        'early_min': 15, 'early_max': 30
    },
    # ... más variables
}
```

---

## 📈 Predicciones en Vivo

**Ejemplo de Salida:**

```json
{
  "status": "success",
  "data": {
    "field1": {
      "field_name": "Humedad Suelo (%)",
      "current": 68.40,
      "forecast": [69.5, 70.2, 71.0, 70.8, 70.5, 69.8]
    },
    "field2": {
      "field_name": "Temperatura (°C)",
      "current": 27.20,
      "forecast": [27.5, 27.8, 28.0, 27.9, 27.5, 27.0]
    }
  }
}
```

---

## 🔧 API REST

### Endpoints Disponibles

#### GET `/api/predictions`
Predicciones actuales con pronóstico

#### GET `/api/alarms`
Estado de alarmas (críticas, tempranas, normales)

#### GET `/api/traffic-light`
Estado de semáforos por variable

#### GET `/api/health`
Estado del servidor y modelos

#### GET `/api/variables`
Información sobre variables monitoreadas

#### GET/PUT `/api/config/alarms`
Obtener/actualizar configuración de alarmas

#### POST `/api/train`
Iniciar entrenamiento de modelo

---

## 📚 Documentación

### Archivos Incluidos

- **`README_IA.md`** - Documentación académica completa (500+ líneas)
- **`DASHBOARD_GUIDE.md`** - Guía de uso del dashboard
- **`NGROK_DEPLOYMENT.md`** - Despliegue en la nube
- **`RESUMEN_IMPLEMENTACION.txt`** - Resumen técnico

---

## 🎓 Conceptos Educativos

### Machine Learning Series Temporal
- Secuencias de 24 pasos
- Normalización MinMax
- Train/validation split 80/20

### Redes Neuronales Recurrentes
- Puertas de actualización (Update Gate)
- Puertas de reset (Reset Gate)
- Memoria a corto/largo plazo

### Sistema de Alarmas Inteligentes
- Umbrales dobles (crítico + temprano)
- Análisis de tendencias futuras
- Lógica de semaforización

---

## 📋 Requisitos

### Software
- Python 3.11+
- pip o conda

### Librerías Principales
```
tensorflow==2.14.0
flask==3.0.0
numpy==1.26.0
pandas==2.1.3
scikit-learn==1.3.0
requests==2.31.0
```

---

## ⚙️ Configuración

### Variables de Entorno (Opcional)

```bash
THINGSPEAK_CHANNEL=2791076
THINGSPEAK_API_KEY=S6P4MH7ZT48FQCAD
```

### Puertos Utilizados

- **5000** - Servidor Flask (predicciones)
- **8080** - Servidor dashboard (alternativo)

---

## 🐛 Troubleshooting

### Error: ModuleNotFoundError: tensorflow

```bash
pip install tensorflow==2.14.0
```

### Error: Port 5000 already in use

```bash
# Encontrar proceso
netstat -ano | findstr :5000

# Matar proceso
taskkill /PID <PID> /F
```

### Error: No data from ThingSpeak

- Verificar conexión internet
- Verificar ID de canal (2791076)
- Esperar 15 minutos (actualización ThingSpeak)

---

## 📊 Resultados

### Modelo Entrenado

```
✓ Modelos Guardados: 4 (field1, field2, field3, field4)
✓ Datos Entrenamiento: 480 registros (~5 días)
✓ Secuencias Generadas: 450 por variable
✓ Horizonte Predicción: 6 pasos (1.5 horas)
✓ Arquitectura: GRU(64+32) + Dense layers
```

### Validación Dashboard

```
✓ Semaforización visible
✓ Predicciones actualizándose
✓ Alarmas generándose
✓ Gráficos renderizando
✓ API respondiendo
```

---

## 🎯 Presentación Académica

### Puntos Clave a Destacar

1. ✅ **Predicciones Neuronales** - GRU entrenado con datos reales
2. ✅ **Semaforización Inteligente** - Indicadores 🟢🟡🔴
3. ✅ **Alarmas Tempranas** - Análisis de tendencias futuras
4. ✅ **Sistema Completo** - Backend + API + Frontend
5. ✅ **Documentación Académica** - Conceptos explicados

### Demo Recomendada

1. Abrir dashboard (verde)
2. Explicar predicciones en gráfico
3. Mostrar API endpoints
4. Cambiar umbral → alarma amarilla
5. Cambiar valor → alarma roja

---

## 📝 Notas

- **Tiempo Inicio:** ~15 segundos (sin entrenamiento)
- **Tiempo Entrenamiento:** 3-5 minutos (primera vez)
- **Actualización Predicciones:** Cada 5 minutos
- **Modo Offline:** Dashboard funciona sin servidor
- **Datos Demo:** Disponible si no hay conexión

---

## 🔗 Enlaces

- **GitHub:** https://github.com/SEBASTIAN3451/AgroTasker_Dashboard
- **ThingSpeak:** https://thingspeak.com/channels/2791076
- **TensorFlow Docs:** https://www.tensorflow.org/

---

## 📄 Licencia

MIT License - Ver LICENSE file

---

## 👤 Autor

**Sebastian Dev** - Proyecto académico AgroTasker 2026

---

## ✅ Checklist de Validación

- [ ] Python 3.11+ instalado
- [ ] requirements.txt instalado
- [ ] Modelo entrenado
- [ ] Servidor iniciado sin errores
- [ ] Dashboard carga en navegador
- [ ] Semaforización visible
- [ ] Predicciones mostradas
- [ ] API respondiendo
- [ ] Alarmas generándose

---

**Última actualización:** Abril 28, 2026  
**Estado:** ✅ Producción Lista - Listo para Presentación

---

*Sistema de IA para monitoreo agrícola inteligente con predicciones neuronales GRU*
