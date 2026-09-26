# AgroTasker Dashboard 🌱

> Dashboard web para monitoreo y análisis de variables agrícolas, con integración de datos IoT, alertas y predicciones mediante modelos Transformer.

![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.0-000000?logo=flask&logoColor=white)
![TensorFlow](https://img.shields.io/badge/TensorFlow-2.14-FF6F00?logo=tensorflow&logoColor=white)
![ThingSpeak](https://img.shields.io/badge/ThingSpeak-IoT-0B6E99)
![Status](https://img.shields.io/badge/Status-Acad%C3%A9mico-blue)

## 📌 Descripción

**AgroTasker** es un proyecto académico orientado al monitoreo de variables de interés agrícola. El dashboard permite visualizar datos recibidos desde ThingSpeak, consultar el estado de las variables, generar alertas mediante un sistema de semaforización y realizar predicciones de series temporales.

El repositorio contiene la parte de software y análisis del sistema, incluyendo el servidor web, el dashboard y los modelos de predicción.

## ✨ Funcionalidades

- 📊 Visualización de datos agrícolas.
- 🌱 Monitoreo de humedad del suelo, temperatura, conductividad eléctrica y pH.
- 🚦 Semaforización según umbrales configurados.
- 🔔 Alertas tempranas y críticas.
- 🤖 Predicción de valores futuros mediante modelos Transformer.
- 📈 Visualización de predicciones.
- 🌐 API REST desarrollada con Flask.
- 💚 Endpoint de salud para comprobar el estado del servidor y los modelos.
- 🔄 Integración con ThingSpeak.

## 🧠 Modelo de predicción

El sistema utiliza una arquitectura basada en **Transformer con Multi-Head Attention** para trabajar con series temporales.

Flujo general:

```text
Datos históricos
      ↓
Normalización
      ↓
Secuencias temporales
      ↓
Transformer
      ↓
Predicciones futuras
      ↓
Dashboard + alertas
```

La implementación disponible utiliza secuencias históricas y genera múltiples pasos futuros para las variables configuradas.

## 🏗️ Arquitectura

```text
┌──────────────────┐
│ Sensores / IoT   │
└────────┬─────────┘
         ↓
┌──────────────────┐
│    ThingSpeak    │
└────────┬─────────┘
         ↓
┌──────────────────┐
│ Modelo Transformer│
└────────┬─────────┘
         ↓
┌──────────────────┐
│   Flask API      │
└────────┬─────────┘
         ↓
┌──────────────────┐
│ Dashboard Web    │
└──────────────────┘
```

## 📁 Estructura

```text
AgroTasker_Dashboard/
├── predictions_model.py
├── predictions_server.py
├── dashboard_ia.html
├── README.md
├── README_IA.md
├── START_IA.bat
├── requirements.txt
├── models/
│   ├── transformer_field1.h5
│   ├── transformer_field2.h5
│   ├── transformer_field3.h5
│   ├── transformer_field4.h5
│   ├── scalers.pkl
│   └── metadata.json
├── js/
├── css/
└── api/
```

## 🚀 Instalación

### Requisitos

- Python 3.11
- Git
- Dependencias indicadas en `requirements.txt`

### 1. Clonar

```bash
git clone https://github.com/SEBASTIAN3451/AgroTasker_Dashboard.git
cd AgroTasker_Dashboard
```

### 2. Instalar dependencias

Se recomienda utilizar un entorno virtual:

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Ejecutar

```bash
python predictions_server.py
```

Después abre:

```text
http://localhost:5000
```

Si necesitas entrenar nuevamente los modelos:

```bash
python predictions_model.py train
```

## 🔌 API

| Método | Endpoint | Función |
|---|---|---|
| GET | `/` | Dashboard |
| GET | `/api/predictions` | Predicciones |
| GET | `/api/alarms` | Alertas |
| GET | `/api/traffic-light` | Estado por variable |
| GET | `/api/health` | Estado del sistema |
| GET | `/api/variables` | Variables monitoreadas |
| GET/PUT | `/api/config/alarms` | Configuración de umbrales |
| POST | `/api/train` | Iniciar entrenamiento |

## 🛠️ Tecnologías

- **Python**
- **Flask**
- **TensorFlow / Keras**
- **NumPy**
- **Pandas**
- **Scikit-learn**
- **HTML / CSS / JavaScript**
- **ThingSpeak**
- **Transformer / Multi-Head Attention**

## 🎓 Contexto

AgroTasker forma parte de un proyecto académico de **Ingeniería Electrónica**, con enfoque en IoT, monitoreo de datos agrícolas, respaldo de información y análisis mediante software.

## 👨‍💻 Autor

**Sebastian Lara**  
Ingeniería Electrónica · IoT · Software · Data & AI

- GitHub: [@SEBASTIAN3451](https://github.com/SEBASTIAN3451)

## 📄 Licencia

Este repositorio utiliza la licencia MIT cuando está indicada en el proyecto.

---

⭐ Proyecto académico enfocado en integrar electrónica, IoT, software y análisis de datos para aplicaciones agrícolas.
