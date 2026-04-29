"""
Modelo de predicciones con Transformer (Attention Mechanism)
Arquitectura moderna con Multi-Head Attention para series temporales
"""

import os
import json
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import requests
from sklearn.preprocessing import MinMaxScaler
import tensorflow as tf
from tensorflow.keras.models import Model
from tensorflow.keras.layers import (
    Input, Dense, Dropout, LayerNormalization, MultiHeadAttention,
    Flatten
)
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

class TransformerPredictor:
    def __init__(self):
        os.makedirs(MODEL_DIR, exist_ok=True)
        self.scalers = {}
        self.models = {}
        self.last_training = None
        
    def fetch_thingspeak_data(self, results=480):
        """
        Descarga datos históricos de ThingSpeak
        results=480: aproximadamente 5 días (1 lectura cada 15 min)
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
                print("[ERROR] No data from ThingSpeak")
                return None
            
            df = pd.DataFrame(data['feeds'])
            
            # Convertir campos a numéricas
            for field in VARIABLES.keys():
                df[field] = pd.to_numeric(df[field], errors='coerce')
            
            # Eliminar filas con NaN
            df = df.dropna(subset=list(VARIABLES.keys()))
            
            print(f"[OK] Descargados {len(df)} registros de ThingSpeak")
            return df.sort_values('created_at').reset_index(drop=True)
            
        except Exception as e:
            print(f"[ERROR] Error descargando datos: {e}")
            return None

    def prepare_data(self, df):
        """
        Prepara datos para el modelo Transformer
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
                y_train_list.append(np.array(y).reshape(len(y), PREDICTION_STEPS))
        
        return X_train_list, y_train_list

    def build_transformer_model(self, input_shape):
        """
        Construye modelo Transformer con Multi-Head Attention
        Arquitectura:
          - Input: Secuencia temporal
          - Multi-Head Attention (4 heads)
          - Feed Forward (Dense layers)
          - Output: Predicción multi-paso
        """
        
        inputs = Input(shape=input_shape)
        
        # Block 1: Multi-Head Attention
        attention = MultiHeadAttention(
            num_heads=4, 
            key_dim=16,
            attention_axes=1
        )(inputs, inputs)
        attention = Dropout(0.2)(attention)
        
        # Add & Norm
        out1 = LayerNormalization(epsilon=1e-6)(inputs + attention)
        
        # Feed Forward Network
        ff = Dense(32, activation='relu')(out1)
        ff = Dropout(0.2)(ff)
        ff = Dense(input_shape[-1])(ff)
        ff = Dropout(0.2)(ff)
        
        # Add & Norm
        out2 = LayerNormalization(epsilon=1e-6)(out1 + ff)
        
        # Block 2: Second Attention Layer
        attention2 = MultiHeadAttention(
            num_heads=4,
            key_dim=16,
            attention_axes=1
        )(out2, out2)
        attention2 = Dropout(0.2)(attention2)
        
        # Add & Norm
        out3 = LayerNormalization(epsilon=1e-6)(out2 + attention2)
        
        # Output layers
        flat = Flatten()(out3)
        dense1 = Dense(64, activation='relu')(flat)
        dense1 = Dropout(0.2)(dense1)
        dense2 = Dense(32, activation='relu')(dense1)
        outputs = Dense(PREDICTION_STEPS)(dense2)
        
        model = Model(inputs=inputs, outputs=outputs)
        model.compile(optimizer=Adam(learning_rate=0.001), loss='mse', metrics=['mae'])
        
        return model

    def train(self, df):
        """
        Entrena modelos Transformer para cada variable
        """
        if df is None or len(df) < SEQUENCE_LENGTH + PREDICTION_STEPS:
            print("[ERROR] Datos insuficientes para entrenar")
            return False
        
        print("\n[TRAIN] Entrenando modelos Transformer...")
        X_list, y_list = self.prepare_data(df)
        
        for idx, field in enumerate(VARIABLES.keys()):
            if idx >= len(X_list):
                continue
            
            X, y = X_list[idx], y_list[idx]
            
            if len(X) == 0:
                print(f"[WARN] {field}: Sin datos suficientes")
                continue
            
            print(f"  [DATA] {VARIABLES[field]['name']}: entrenando con {len(X)} secuencias...")
            
            # Construir y entrenar modelo Transformer
            model = self.build_transformer_model((X.shape[1], X.shape[2]))
            
            # Entrenar con early stopping y learning rate reduction
            history = model.fit(
                X, y,
                epochs=100,
                batch_size=32,
                validation_split=0.2,
                verbose=0,
                callbacks=[
                    tf.keras.callbacks.EarlyStopping(
                        monitor='val_loss',
                        patience=15,
                        restore_best_weights=True
                    ),
                    tf.keras.callbacks.ReduceLROnPlateau(
                        monitor='val_loss',
                        factor=0.5,
                        patience=5,
                        min_lr=0.00001
                    )
                ]
            )
            
            self.models[field] = model
            
            # Guardar modelo
            model_path = os.path.join(MODEL_DIR, f'transformer_{field}.h5')
            model.save(model_path)
            print(f"  [OK] Modelo Transformer guardado: {model_path}")
        
        self.last_training = datetime.now()
        self._save_metadata()
        
        # Guardar scalers
        import pickle
        scalers_path = os.path.join(MODEL_DIR, 'scalers.pkl')
        with open(scalers_path, 'wb') as f:
            pickle.dump(self.scalers, f)
        print(f"[OK] Scalers guardados: {scalers_path}")
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
            
            if field not in self.scalers:
                continue

            # Obtener últimos SEQUENCE_LENGTH valores
            data = df[field].tail(SEQUENCE_LENGTH).values.reshape(-1, 1).astype(float)
            
            scaled_data = self.scalers[field].transform(data)
            
            # Hacer predicción
            X_pred = np.expand_dims(scaled_data, axis=0)
            y_pred_scaled = self.models[field].predict(X_pred, verbose=0)[0]
            
            # Desnormalizar
            y_pred = self.scalers[field].inverse_transform(y_pred_scaled.reshape(-1, 1)).flatten()
            
            forecast = [float(np.clip(v, VARIABLES[field]['min'], VARIABLES[field]['max'])) for v in y_pred[:steps]]

            predictions[field] = {
                'field_name': VARIABLES[field]['name'],
                'current': float(df[field].iloc[-1]),
                'forecast': forecast,
                'min_threshold': VARIABLES[field]['min'],
                'max_threshold': VARIABLES[field]['max']
            }

        return predictions

    def _save_metadata(self):
        """Guarda metadata del entrenamiento"""
        metadata = {
            'last_training': self.last_training.isoformat(),
            'architecture': 'Transformer',
            'sequence_length': SEQUENCE_LENGTH,
            'prediction_steps': PREDICTION_STEPS,
            'variables': list(VARIABLES.keys()),
            'attention_heads': 4,
            'ff_dim': 32
        }
        
        with open(os.path.join(MODEL_DIR, 'metadata.json'), 'w') as f:
            json.dump(metadata, f, indent=2)

    def load_models(self):
        """Carga modelos previamente entrenados y scalers"""
        import pickle
        
        # Cargar scalers
        scalers_path = os.path.join(MODEL_DIR, 'scalers.pkl')
        if os.path.exists(scalers_path):
            try:
                with open(scalers_path, 'rb') as f:
                    self.scalers = pickle.load(f)
                print(f"[OK] Scalers cargados: {len(self.scalers)} variables")
            except Exception as e:
                print(f"[ERROR] Error cargando scalers: {e}")
        
        # Cargar modelos
        for field in VARIABLES.keys():
            model_path = os.path.join(MODEL_DIR, f'transformer_{field}.h5')
            if os.path.exists(model_path):
                try:
                    self.models[field] = tf.keras.models.load_model(model_path)
                    print(f"[OK] Modelo Transformer cargado: {field}")
                except Exception as e:
                    print(f"[ERROR] Error cargando modelo {field}: {e}")

        metadata_path = os.path.join(MODEL_DIR, 'metadata.json')
        if os.path.exists(metadata_path):
            try:
                with open(metadata_path, 'r') as f:
                    metadata = json.load(f)
                if metadata.get('last_training'):
                    self.last_training = datetime.fromisoformat(metadata['last_training'])
            except Exception as e:
                print(f"[WARN] Error cargando metadata: {e}")

# Función para uso directo
def get_predictions():
    """
    Obtiene predicciones actuales
    """
    predictor = TransformerPredictor()
    predictor.load_models()
    
    if not predictor.models:
        print("[WARN] Necesita entrenar primero con train_model()")
        return None
    
    df = predictor.fetch_thingspeak_data()
    if df is not None:
        return predictor.predict_next(df)
    
    return None

def train_model():
    """
    Entrena nuevo modelo Transformer con datos recientes
    """
    predictor = TransformerPredictor()
    df = predictor.fetch_thingspeak_data(results=480)  # Últimos ~5 días
    
    if df is not None:
        success = predictor.train(df)
        if success:
            print("[OK] Entrenamiento Transformer completado exitosamente")
            return predictor
    
    return None

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'train':
        print("=" * 50)
        print("ENTRENAMIENTO DE MODELO TRANSFORMER")
        print("=" * 50)
        train_model()
    else:
        print("=" * 50)
        print("PREDICCIONES ACTUALES (TRANSFORMER)")
        print("=" * 50)
        preds = get_predictions()
        if preds:
            print(json.dumps(preds, indent=2, ensure_ascii=False))
        else:
            print("[ERROR] No hay predicciones disponibles")
