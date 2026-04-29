# AgroTasker Dashboard - Sistema IA con Transformer

![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen)
![Python](https://img.shields.io/badge/Python-3.11-blue)
![TensorFlow](https://img.shields.io/badge/TensorFlow-2.14-orange)
![License](https://img.shields.io/badge/License-MIT-green)

> Sistema completo de monitoreo agricola con predicciones de redes neuronales Transformer, semaforizacion inteligente y alarmas automaticas.

---

## Contenido del Repositorio

### Componentes IA

- **`predictions_model.py`** - Modelo Transformer con Multi-Head Attention
  - Descarga datos historicos de ThingSpeak.
  - Entrena 4 modelos independientes, uno por variable agricola.
  - Usa secuencias de 24 mediciones para predecir 6 pasos adelante (~1.5 horas).
  - Guarda modelos en `./models/transformer_*.h5`.
  - Guarda normalizadores en `./models/scalers.pkl`.

- **`predictions_server.py`** - Servidor Flask con API REST
  - Puerto 5000.
  - Sirve el dashboard principal en `http://localhost:5000`.
  - Endpoints: `/api/predictions`, `/api/alarms`, `/api/traffic-light`, `/api/health`.
  - Sistema automatico de alarmas tempranas y criticas.
  - Semaforizacion en tiempo real: verde, amarillo y rojo.

### Dashboards

- **`dashboard_ia.html`** - Principal con IA
  - Semaforizacion visual completa.
  - Centro de alertas y alarmas.
  - Mediciones en vivo.
  - Predicciones IA con graficos.
  - Pronostico de 1.5 horas.

- **`dashboard_realtime_dual.html`** - Dual ThingSpeak
  - Datos crudos de dos canales.
  - Sin predicciones neuronales.

### Paquete ZIP

- **`AgroTasker_IA_Transformer.zip`**
  - Paquete con los archivos principales del sistema IA.
  - Incluye dashboard, servidor, modelo, documentacion, script de arranque, dependencias y modelos Transformer entrenados.

---

## Estructura Principal

```text
AgroTasker_Dashboard/
|-- predictions_model.py          # Modelo Transformer
|-- predictions_server.py         # Servidor Flask + API + alarmas
|-- dashboard_ia.html             # Dashboard IA principal
|-- README.md                     # Resumen del repositorio
|-- README_IA.md                  # Documentacion tecnica y academica
|-- START_IA.bat                  # Arranque automatico en Windows
|-- requirements.txt              # Dependencias Python
|-- AgroTasker_IA_Transformer.zip # Paquete del sistema IA
|-- models/
|   |-- transformer_field1.h5     # Modelo humedad suelo
|   |-- transformer_field2.h5     # Modelo temperatura
|   |-- transformer_field3.h5     # Modelo EC
|   |-- transformer_field4.h5     # Modelo pH
|   |-- scalers.pkl               # Normalizadores MinMax
|   |-- metadata.json             # Metadatos de entrenamiento
|-- js/
|-- css/
|-- api/
```

---

## Inicio Rapido

### Opcion 1: Script Automatico

```bat
cd C:\Users\SEBASTIAN\AgroTasker_Dashboard
START_IA.bat
```

El script:

- Activa o crea el entorno virtual.
- Instala dependencias.
- Verifica modelos Transformer entrenados.
- Entrena automaticamente si faltan modelos.
- Inicia Flask en el puerto 5000.
- Abre el dashboard en `http://localhost:5000`.

### Opcion 2: Manual

```bash
pip install -r requirements.txt
python predictions_model.py train
python predictions_server.py
```

Luego abre:

```text
http://localhost:5000
```

---

## Arquitectura del Modelo

### Transformer con Multi-Head Attention

```text
Entrada: 24 valores historicos
    |
MultiHeadAttention(4 heads)
    |
Dropout + LayerNormalization
    |
Feed Forward Network
    |
Dropout + LayerNormalization
    |
MultiHeadAttention(4 heads)
    |
Flatten + Dense(64) + Dense(32)
    |
Salida: 6 predicciones futuras
```

### Datos de Entrenamiento

- **Fuente:** ThingSpeak canal `2791076`.
- **Historial:** 480 registros aproximadamente.
- **Frecuencia:** 1 lectura cada 15 minutos.
- **Variables:** humedad del suelo, temperatura, EC y pH.
- **Horizonte:** 6 pasos futuros, equivalente a ~1.5 horas.

### Ventajas del Transformer

| Aspecto | Transformer |
|---|---|
| Contexto temporal | Captura relaciones entre mediciones lejanas |
| Paralelizacion | Mejor que modelos recurrentes clasicos |
| Arquitectura | Multi-Head Attention + Feed Forward |
| Uso en AgroTasker | Prediccion multi-paso por variable |

---

## API REST

| Metodo | Endpoint | Descripcion |
|---|---|---|
| GET | `/` | Dashboard IA |
| GET | `/api/predictions` | Predicciones actuales |
| GET | `/api/alarms` | Alarmas criticas, tempranas y normales |
| GET | `/api/traffic-light` | Estado de semaforo por variable |
| GET | `/api/health` | Estado del servidor y modelos cargados |
| GET | `/api/variables` | Variables monitoreadas |
| GET/PUT | `/api/config/alarms` | Configuracion de umbrales |
| POST | `/api/train` | Entrenamiento en segundo plano |

---

## Sistema de Alarmas

### Verde

La medicion actual y el pronostico estan dentro del rango seguro.

### Amarillo

La medicion aun puede estar en rango, pero el pronostico muestra tendencia preocupante o cercania a un umbral.

### Rojo

La medicion actual esta fuera de rango o el pronostico supera limites criticos.

---

## Archivos de IA

```text
models/
|-- transformer_field1.h5
|-- transformer_field2.h5
|-- transformer_field3.h5
|-- transformer_field4.h5
|-- scalers.pkl
|-- metadata.json
```

Los archivos `.h5` contienen los modelos Transformer entrenados. `scalers.pkl` guarda los normalizadores usados para convertir datos reales a escala 0-1 y volver a unidades originales durante la prediccion.

---

## Validacion

Comprobaciones realizadas:

```bash
python -m py_compile predictions_model.py predictions_server.py
python predictions_model.py
```

Tambien se valido:

- Carga de 4 modelos Transformer.
- Carga de 4 scalers.
- Descarga de 480 registros desde ThingSpeak.
- Generacion de predicciones para `field1`, `field2`, `field3` y `field4`.
- Flask sirviendo el dashboard en `/`.
- `/api/health` respondiendo con `models_loaded: 4`.

---

## Requisitos

```text
flask==3.0.0
flask-socketio==5.3.6
flask-cors==4.0.0
python-dotenv==1.0.0
paho-mqtt==2.1.0
tensorflow==2.14.0
numpy==1.24.3
pandas==2.0.3
scikit-learn==1.3.0
requests==2.31.0
```

---

## Troubleshooting

### `localhost:5000` no abre

Ejecuta:

```bash
python predictions_server.py
```

### No hay predicciones

Entrena o verifica los modelos:

```bash
python predictions_model.py train
```

### Puerto 5000 ocupado

```bat
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

---

## Enlaces

- **GitHub:** https://github.com/SEBASTIAN3451/AgroTasker_Dashboard
- **ThingSpeak:** https://thingspeak.com/channels/2791076
- **TensorFlow:** https://www.tensorflow.org/

---

## Autor

**Sebastian Dev** - Proyecto academico AgroTasker 2026

---

**Ultima actualizacion:** Abril 29, 2026  
**Estado:** Produccion lista con red neuronal Transformer

---

*Sistema de IA para monitoreo agricola inteligente con predicciones neuronales Transformer.*
