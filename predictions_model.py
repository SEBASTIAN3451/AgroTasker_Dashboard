"""
Modelo de predicciones con GRU (Gated Recurrent Unit)
Alternativa ligera a LSTM para predicción de variables agrícolas
"""

import os
import json
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import requests
from sklearn.preprocessing import MinMaxScaler
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import GRU, Dense, Dropout
from tensorflow.keras.optimizers import Adam
import warnings
warnings.filterwarnings('ignore')

# Configuración
THINGSPEAK_CHANNEL = 2791076
THINGSPEAK_API_KEY = "S6P4MH7ZT48FQCAD"  # Read API key
SEQUENCE_LENGTH = 24  # Usar últimas 24 mediciones para predecir
PREDICTION_STEPS = 6  # Predecir 6 pasos adelante (próximas 1.5 horas si cada 15 min)
MODEL_DIR = "./models"

# Variables a predecir
VARIABLES = {
    'field1': {'name': 'Humedad Suelo (%)', 'min': 0, 'max': 100},
    'field2': {'name': 'Temperatura (°C)', 'min': -5, 'max': 50},
    'field3': {'name': 'EC (uS/cm)', 'min': 0, 'max': 5000},
    'field4': {'name': 'pH', 'min': 4, 'max': 9},
}

class SensorPredictor:
    def __init__(self):
        os.makedirs(MODEL_DIR, exist_ok=True)
        self.scalers = {}
        self.models = {}
        self.last_training = None
        
    def fetch_thingspeak_data(self, results=480):
        """
        Descarga datos históricos de ThingSpeak
        results=480 → aproximadamente 5 días (1 lectura cada 15 min)
        """
        url = f"https://api.thingspeak.com/channels/{THINGSPEAK_CHANNEL}/feeds.json"
        params = {
            'api_key': THINGSPEAK_API_KEY,
            'results': results,
            'fields': ','.join(list(VARIABLES.keys()))
        }
        
        try:
            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            if 'feeds' not in data or not data['feeds']:
                print("❌ No data from ThingSpeak")
                return None
            
            df = pd.DataFrame(data['feeds'])
            
            # Convertir campos a numéricas
            for field in VARIABLES.keys():
                df[field] = pd.to_numeric(df[field], errors='coerce')
            
            # Eliminar filas con NaN
            df = df.dropna(subset=list(VARIABLES.keys()))
            
            print(f"✓ Descargados {len(df)} registros de ThingSpeak")
            return df.sort_values('created_at').reset_index(drop=True)
            
        except Exception as e:
            print(f"❌ Error descargando datos: {e}")
            return None

    def prepare_data(self, df):
        """
        Prepara datos para el modelo GRU
        Normaliza y crea secuencias para entrenamiento
        """
        X_train_list = []
        y_train_list = []
        
        for field in VARIABLES.keys():
            if field not in df.columns:
                continue
            
            # Obtener datos
            data = df[field].values.reshape(-1, 1).astype(float)
            
            # Normalizar (0 a 1)
            scaler = MinMaxScaler(feature_range=(0, 1))
            scaled_data = scaler.fit_transform(data)
            self.scalers[field] = scaler
            
            # Crear secuencias
            X, y = [], []
            for i in range(len(scaled_data) - SEQUENCE_LENGTH - PREDICTION_STEPS):
                X.append(scaled_data[i:i+SEQUENCE_LENGTH])
                y.append(scaled_data[i+SEQUENCE_LENGTH:i+SEQUENCE_LENGTH+PREDICTION_STEPS])
            
            if X:
                X_train_list.append(np.array(X))
                y_train_list.append(np.array(y))
        
        return X_train_list, y_train_list

    def build_gru_model(self, input_shape):
        """
        Construye modelo GRU (más ligero que LSTM)
        """
        model = Sequential([
            GRU(64, activation='relu', input_shape=input_shape, return_sequences=True),
            Dropout(0.2),
            GRU(32, activation='relu', return_sequences=False),
            Dropout(0.2),
            Dense(16, activation='relu'),
            Dense(PREDICTION_STEPS)  # Predicción multi-paso
        ])
        
        model.compile(optimizer=Adam(learning_rate=0.001), loss='mse', metrics=['mae'])
        return model

    def train(self, df):
        """
        Entrena modelos GRU para cada variable
        """
        if df is None or len(df) < SEQUENCE_LENGTH + PREDICTION_STEPS:
            print("❌ Datos insuficientes para entrenar")
            return False
        
        print(f"\n🔄 Entrenando modelos GRU...")
        X_list, y_list = self.prepare_data(df)
        
        for idx, field in enumerate(VARIABLES.keys()):
            if idx >= len(X_list):
                continue
            
            X, y = X_list[idx], y_list[idx]
            
            if len(X) == 0:
                print(f"⚠️  {field}: Sin datos suficientes")
                continue
            
            print(f"  📊 {VARIABLES[field]['name']}: entrenando con {len(X)} secuencias...")
            
            # Construir y entrenar modelo
            model = self.build_gru_model((X.shape[1], X.shape[2]))
            
            # Entrenar con early stopping
            history = model.fit(
                X, y,
                epochs=50,
                batch_size=32,
                validation_split=0.2,
                verbose=0,
                callbacks=[
                    tf.keras.callbacks.EarlyStopping(
                        monitor='val_loss',
                        patience=10,
                        restore_best_weights=True
                    )
                ]
            )
            
            self.models[field] = model
            
            # Guardar modelo
            model_path = os.path.join(MODEL_DIR, f'gru_{field}.h5')
            model.save(model_path)
            print(f"  ✓ Modelo guardado: {model_path}")
        
        self.last_training = datetime.now()
        self._save_metadata()
        return True

    def predict_next(self, df, steps=PREDICTION_STEPS):
        """
        Predice los próximos valores basado en últimos datos
        """
        predictions = {}
        
        if df is None or len(df) < SEQUENCE_LENGTH:
            return None
        
        for field in VARIABLES.keys():
            if field not in self.models:
                continue
            
            # Obtener últimos SEQUENCE_LENGTH valores
            data = df[field].tail(SEQUENCE_LENGTH).values.reshape(-1, 1).astype(float)
            
            if field in self.scalers:
                scaled_data = self.scalers[field].transform(data)
            else:
                continue
            
            # Hacer predicción
            X_pred = np.expand_dims(scaled_data, axis=0)
            y_pred_scaled = self.models[field].predict(X_pred, verbose=0)[0]
            
            # Desnormalizar
            y_pred = self.scalers[field].inverse_transform(y_pred_scaled.reshape(-1, 1)).flatten()
            
            predictions[field] = {
                'field_name': VARIABLES[field]['name'],
                'current': float(df[field].iloc[-1]),
                'forecast': [max(0, float(v)) for v in y_pred],
                'min_threshold': VARIABLES[field]['min'],
                'max_threshold': VARIABLES[field]['max']
            }
        
        return predictions

    def _save_metadata(self):
        """Guarda metadata del entrenamiento"""
        metadata = {
            'last_training': self.last_training.isoformat(),
            'sequence_length': SEQUENCE_LENGTH,
            'prediction_steps': PREDICTION_STEPS,
            'variables': list(VARIABLES.keys())
        }
        
        with open(os.path.join(MODEL_DIR, 'metadata.json'), 'w') as f:
            json.dump(metadata, f, indent=2)

    def load_models(self):
        """Carga modelos previamente entrenados"""
        for field in VARIABLES.keys():
            model_path = os.path.join(MODEL_DIR, f'gru_{field}.h5')
            if os.path.exists(model_path):
                try:
                    self.models[field] = tf.keras.models.load_model(model_path)
                    print(f"✓ Modelo cargado: {field}")
                except Exception as e:
                    print(f"❌ Error cargando modelo {field}: {e}")

# Función para uso directo
def get_predictions():
    """
    Obtiene predicciones actuales
    """
    predictor = SensorPredictor()
    predictor.load_models()
    
    if not predictor.models:
        print("⚠️  Necesita entrenar primero con train_model()")
        return None
    
    df = predictor.fetch_thingspeak_data()
    if df is not None:
        return predictor.predict_next(df)
    
    return None

def train_model():
    """
    Entrena nuevo modelo con datos recientes
    """
    predictor = SensorPredictor()
    df = predictor.fetch_thingspeak_data(results=480)  # Últimos ~5 días
    
    if df is not None:
        success = predictor.train(df)
        if success:
            print("✓ Entrenamiento completado exitosamente")
            return predictor
    
    return None

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'train':
        print("=" * 50)
        print("ENTRENAMIENTO DE MODELO GRU")
        print("=" * 50)
        train_model()
    else:
        print("=" * 50)
        print("PREDICCIONES ACTUALES")
        print("=" * 50)
        preds = get_predictions()
        if preds:
            print(json.dumps(preds, indent=2, ensure_ascii=False))
        else:
            print("❌ No hay predicciones disponibles")
