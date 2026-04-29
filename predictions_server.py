"""
Servidor de predicciones con alarmas
Integrado con Flask para servir predicciones vía API.
Modelo: Transformer con Multi-Head Attention.
"""

from flask import Flask, jsonify, request, send_from_directory, make_response
from flask_cors import CORS
import json
import os
from datetime import datetime, timezone
import requests
from predictions_model import (
    TransformerPredictor,
    train_model,
    VARIABLES,
    THINGSPEAK_CHANNEL,
    THINGSPEAK_API_KEY,
    SECONDARY_THINGSPEAK_CHANNEL,
    SECONDARY_THINGSPEAK_API_KEY,
)
import threading
import time

app = Flask(__name__)
CORS(app)

# Estado global
predictor = TransformerPredictor()
ALARM_CONFIG = {
    'field1': {'min': 30, 'max': 90, 'early_min': 40, 'early_max': 80},  # Humedad
    'field2': {'min': 10, 'max': 35, 'early_min': 15, 'early_max': 30},   # Temperatura
    'field3': {'min': 5.5, 'max': 7.5, 'early_min': 5.8, 'early_max': 7.2},  # pH
    'field4': {'min': 0, 'max': 5000, 'early_min': 50, 'early_max': 4500},  # EC
}

# Almacenar última predicción en memoria
last_predictions = None
last_alarms = None
update_timestamp = None
active_source = None
CACHE_FILE = os.path.join('models', 'live_sources_cache.json')

DATA_SOURCES = [
    {
        'id': 'primary',
        'name': 'ThingSpeak principal',
        'channel': THINGSPEAK_CHANNEL,
        'api_key': THINGSPEAK_API_KEY,
    },
    {
        'id': 'secondary',
        'name': 'ThingSpeak secundario',
        'channel': SECONDARY_THINGSPEAK_CHANNEL,
        'api_key': SECONDARY_THINGSPEAK_API_KEY,
    },
]

def get_traffic_light(current, forecast, min_th, early_min, early_max, max_th):
    """
    Determina estado de semáforo basado en valor actual y predicción
    Verde: Todo bien
    Amarillo: Alerta temprana
    Rojo: Fuera de rango
    """
    # Valores críticos
    if current < min_th or current > max_th:
        return 'red'
    
    # Verificar tendencia peligrosa en predicción
    if len(forecast) > 0:
        max_pred = max(forecast)
        min_pred = min(forecast)
        
        if min_pred < min_th or max_pred > max_th:
            return 'red'
        
        if min_pred < early_min or max_pred > early_max:
            return 'yellow'
    
    return 'green'

def generate_alarms(predictions):
    """
    Genera alarmas basadas en predicciones
    Alarmas tempranas (yellow) y críticas (red)
    """
    alarms = {
        'critical': [],      # Rojo - Acción inmediata
        'early_warning': [], # Amarillo - Prevención
        'normal': [],        # Verde - Todo bien
        'timestamp': datetime.now().isoformat()
    }
    
    if not predictions:
        return alarms
    
    for field, data in predictions.items():
        if field not in ALARM_CONFIG:
            continue
        
        config = ALARM_CONFIG[field]
        current = data['current']
        forecast = data.get('forecast', [])
        
        status = get_traffic_light(
            current,
            forecast,
            config['min'],
            config['early_min'],
            config['early_max'],
            config['max']
        )
        
        alarm_item = {
            'field': field,
            'field_name': data.get('field_name', field),
            'current': current,
            'status': status,
            'forecast': forecast[:3] if forecast else [],  # Próximas 3 predicciones
        }
        
        if status == 'red':
            alarm_item['message'] = f"⛔ CRÍTICO: {data['field_name']} fuera de rango ({current})"
            alarms['critical'].append(alarm_item)
        elif status == 'yellow':
            alarm_item['message'] = f"⚠️  PRECAUCIÓN: {data['field_name']} tendencia preocupante ({current})"
            alarms['early_warning'].append(alarm_item)
        else:
            alarm_item['message'] = f"✓ NORMAL: {data['field_name']} bajo control ({current})"
            alarms['normal'].append(alarm_item)
    
    return alarms

def fetch_source_snapshot(source, results=1):
    """Obtiene la ultima lectura cruda de una fuente ThingSpeak."""
    try:
        response = requests.get(
            f"https://api.thingspeak.com/channels/{source['channel']}/feeds.json",
            params={'api_key': source['api_key'], 'results': results},
            timeout=12
        )
        response.raise_for_status()
        payload = response.json()
        feeds = payload.get('feeds', [])
        latest = feeds[-1] if feeds else None
        return {
            'id': source['id'],
            'name': source['name'],
            'channel': source['channel'],
            'ok': bool(latest),
            'latest': latest,
            'is_valid': is_valid_feed(latest),
            'age_minutes': get_age_minutes(latest.get('created_at')) if latest else None,
            'source': 'thingspeak'
        }
    except Exception as exc:
        return {
            'id': source['id'],
            'name': source['name'],
            'channel': source['channel'],
            'ok': False,
            'latest': None,
            'is_valid': False,
            'age_minutes': None,
            'error': str(exc),
            'source': 'thingspeak'
        }

def fetch_dropbox_snapshot():
    """Obtiene estado resumido del historico Dropbox usado por dashboards duales."""
    try:
        from server_production import ProxyHandler
        handler = object.__new__(ProxyHandler)
        payload = handler.get_dropbox_series_data()
        series = payload.get('series', []) if isinstance(payload, dict) else []
        latest = series[-1] if series else None

        return {
            'id': 'dropbox',
            'name': 'Dropbox historico',
            'channel': None,
            'ok': bool(series),
            'is_valid': bool(latest),
            'latest': latest,
            'records': len(series),
            'age_minutes': get_age_minutes(latest.get('created_at')) if latest else None,
            'source': 'dropbox',
            'meta': payload.get('meta', {}) if isinstance(payload, dict) else {}
        }
    except Exception as exc:
        return {
            'id': 'dropbox',
            'name': 'Dropbox historico',
            'channel': None,
            'ok': False,
            'is_valid': False,
            'latest': None,
            'records': 0,
            'age_minutes': None,
            'source': 'dropbox',
            'error': str(exc)
        }

def normalize_soil_feed(feed):
    """Convierte field1-field4 a nombres de lectura usados por la UI."""
    if not feed:
        return None

    def as_float(value):
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    return {
        'created_at': feed.get('created_at'),
        'humidity': as_float(feed.get('field1')),
        'temperature': as_float(feed.get('field2')),
        'ph': as_float(feed.get('field3')),
        'ec': as_float(feed.get('field4')),
        'raw': feed
    }

def normalize_dropbox_row(row):
    if not row:
        return None

    humidity = row.get('humedadSuelo')
    try:
        estimated_ec = round(max(1.0, float(humidity) * 14 + 120), 2)
    except (TypeError, ValueError):
        estimated_ec = None

    return {
        'created_at': row.get('created_at'),
        'humidity': humidity,
        'temperature': row.get('tempAire'),
        'ph': row.get('phSuelo'),
        'ec': estimated_ec,
        'raw': row
    }

def load_live_cache():
    try:
        if os.path.exists(CACHE_FILE):
            with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception:
        pass
    return {}

def save_live_cache(cache):
    try:
        os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
        with open(CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(cache, f, indent=2, ensure_ascii=False)
    except Exception as exc:
        print(f"[WARN] No se pudo guardar cache de fuentes: {exc}")

def source_payload(snapshot, cache_key=None):
    reading = normalize_soil_feed(snapshot.get('latest'))
    payload = {
        'id': snapshot.get('id'),
        'name': snapshot.get('name'),
        'channel': snapshot.get('channel'),
        'is_valid': snapshot.get('is_valid', False),
        'age_minutes': snapshot.get('age_minutes'),
        'reading': reading,
        'stored': False,
        'status': 'valid' if snapshot.get('is_valid') else 'invalid'
    }

    cache = load_live_cache()
    if snapshot.get('is_valid') and reading and cache_key:
        cache[cache_key] = {
            'reading': reading,
            'saved_at': datetime.now().isoformat(),
            'age_minutes': snapshot.get('age_minutes')
        }
        save_live_cache(cache)
    elif cache_key and cache.get(cache_key):
        payload['reading'] = cache[cache_key].get('reading')
        payload['stored'] = True
        payload['status'] = 'stored'

    return payload

def is_valid_feed(feed):
    if not feed:
        return False

    try:
        humidity = float(feed.get('field1') or 0)
        temperature = float(feed.get('field2') or -99)
        ph = float(feed.get('field3') or 0)
        ec = float(feed.get('field4') or 0)
    except (TypeError, ValueError):
        return False

    return (
        0 < humidity <= 100 and
        -5 < temperature <= 60 and
        3 <= ph <= 10 and
        ec > 0
    )

def get_age_minutes(created_at):
    if not created_at:
        return None

    try:
        normalized = created_at.replace('Z', '+00:00')
        created = datetime.fromisoformat(normalized)
        return round((datetime.now(timezone.utc) - created).total_seconds() / 60, 1)
    except ValueError:
        return None

def update_predictions_background():
    """Actualiza predicciones cada minuto en background."""
    global last_predictions, last_alarms, update_timestamp, active_source
    
    while True:
        try:
            time.sleep(60)
            
            print("[PREDICCIONES] Actualizando predicciones...")
            df = predictor.fetch_thingspeak_data(results=480)
            
            if df is not None and predictor.models:
                last_predictions = predictor.predict_next(df)
                last_alarms = generate_alarms(last_predictions)
                update_timestamp = datetime.now().isoformat()
                active_source = predictor.last_source
                print("[PREDICCIONES] OK Predicciones actualizadas")
            
        except Exception as e:
            print(f"[PREDICCIONES] ERROR actualizando: {e}")

# Inicializar predicciones en startup
def init_predictions():
    """
    Carga modelos e inicializa predicciones
    """
    global last_predictions, last_alarms, update_timestamp, active_source
    
    try:
        print("[STARTUP] Cargando modelos entrenados...")
        predictor.load_models()
        
        if predictor.models:
            print(f"[STARTUP] OK {len(predictor.models)} modelos cargados")
            df = predictor.fetch_thingspeak_data(results=480)
            
            if df is not None:
                last_predictions = predictor.predict_next(df)
                if last_predictions:
                    last_alarms = generate_alarms(last_predictions)
                    update_timestamp = datetime.now().isoformat()
                    active_source = predictor.last_source
                    print("[STARTUP] OK Predicciones iniciales generadas")
                else:
                    print("[STARTUP] WARN Modelos cargados, pero no se generaron predicciones")
        else:
            print("[STARTUP] WARN No hay modelos. Ejecute: python predictions_model.py train")
    
    except Exception as e:
        print(f"[STARTUP] ERROR inicializando: {e}")

# ============ RUTAS API ============

@app.route('/api/predictions', methods=['GET'])
def get_predictions_api():
    """GET /api/predictions - Obtiene predicciones actuales"""
    if not last_predictions:
        return jsonify({
            'status': 'error',
            'message': 'No predictions available. Train model first.',
            'train_command': 'python predictions_model.py train'
        }), 503
    
    return jsonify({
        'status': 'success',
        'data': last_predictions,
        'timestamp': update_timestamp,
        'source': active_source,
        'next_update': None  # Cliente puede calcular
    })

@app.route('/', methods=['GET'])
def dashboard():
    """Sirve el dashboard IA desde el mismo servidor Flask."""
    response = make_response(send_from_directory(os.getcwd(), 'dashboard_ia.html'))
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/api/alarms', methods=['GET'])
def get_alarms_api():
    """GET /api/alarms - Obtiene alarmas actuales"""
    if not last_alarms:
        return jsonify({
            'status': 'error',
            'message': 'No alarms available'
        }), 503
    
    return jsonify({
        'status': 'success',
        'alarms': last_alarms,
        'timestamp': update_timestamp,
        'source': active_source
    })

@app.route('/api/traffic-light', methods=['GET'])
def get_traffic_light_api():
    """GET /api/traffic-light - Estado semáforo de todas variables"""
    if not last_predictions or not last_alarms:
        return jsonify({'status': 'error'}), 503
    
    lights = {}
    for alarm in last_alarms['critical']:
        lights[alarm['field']] = 'red'
    for alarm in last_alarms['early_warning']:
        lights[alarm['field']] = 'yellow'
    for alarm in last_alarms['normal']:
        lights[alarm['field']] = 'green'
    
    return jsonify({
        'status': 'success',
        'lights': lights,
        'timestamp': update_timestamp,
        'source': active_source
    })

@app.route('/api/health', methods=['GET'])
def health_check():
    """GET /api/health - Estado del servidor de predicciones"""
    models_loaded = len(predictor.models)
    has_predictions = last_predictions is not None
    
    return jsonify({
        'status': 'ok',
        'models_loaded': models_loaded,
        'has_predictions': has_predictions,
        'last_update': update_timestamp,
        'active_source': active_source,
        'models': list(predictor.models.keys())
    })

@app.route('/api/data-sources', methods=['GET'])
def data_sources_api():
    """GET /api/data-sources - Estado de las fuentes ThingSpeak usadas."""
    sources = [fetch_source_snapshot(source) for source in DATA_SOURCES]
    sources.append(fetch_dropbox_snapshot())
    return jsonify({
        'status': 'success',
        'active_source': active_source,
        'sources': sources,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/live-channels', methods=['GET'])
def live_channels_api():
    """GET /api/live-channels - Muestra principal+Dropbox y secundario por separado."""
    primary_snapshot = fetch_source_snapshot(DATA_SOURCES[0])
    secondary_snapshot = fetch_source_snapshot(DATA_SOURCES[1])
    dropbox_snapshot = fetch_dropbox_snapshot()

    primary = source_payload(primary_snapshot, 'primary')
    secondary = source_payload(secondary_snapshot, 'secondary')

    dropbox_reading = normalize_dropbox_row(dropbox_snapshot.get('latest'))
    primary_group_reading = primary.get('reading')
    primary_group_source = 'thingspeak'
    primary_group_status = primary.get('status')

    if not primary_snapshot.get('is_valid') and dropbox_reading:
        primary_group_reading = dropbox_reading
        primary_group_source = 'dropbox'
        primary_group_status = 'fallback_dropbox'

    return jsonify({
        'status': 'success',
        'updated_at': datetime.now().isoformat(),
        'refresh_seconds': 60,
        'primary_dropbox': {
            'title': 'ThingSpeak principal + Dropbox',
            'reading': primary_group_reading,
            'source': primary_group_source,
            'status': primary_group_status,
            'thingspeak': primary,
            'dropbox': {
                'id': 'dropbox',
                'name': 'Dropbox historico',
                'is_valid': dropbox_snapshot.get('is_valid', False),
                'records': dropbox_snapshot.get('records', 0),
                'age_minutes': dropbox_snapshot.get('age_minutes'),
                'reading': dropbox_reading,
                'status': 'valid' if dropbox_snapshot.get('is_valid') else 'invalid'
            }
        },
        'secondary': secondary
    })

@app.route('/api/train', methods=['POST'])
def train_api():
    """POST /api/train - Entrena nuevo modelo (operación larga)"""
    try:
        print("[API] Iniciando entrenamiento vía API...")
        
        # Ejecutar en thread para no bloquear
        def train_background():
            global predictor, active_source
            predictor = train_model()
            if predictor:
                df = predictor.fetch_thingspeak_data(results=480)
                global last_predictions, last_alarms, update_timestamp
                last_predictions = predictor.predict_next(df)
                last_alarms = generate_alarms(last_predictions)
                update_timestamp = datetime.now().isoformat()
                active_source = predictor.last_source
        
        thread = threading.Thread(target=train_background, daemon=True)
        thread.start()
        
        return jsonify({
            'status': 'training',
            'message': 'Model training started in background. Check /api/health for status.',
            'check_interval': 30
        }), 202
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/config/alarms', methods=['GET', 'PUT'])
def alarm_config():
    """GET/PUT /api/config/alarms - Obtiene/actualiza configuración de alarmas"""
    global ALARM_CONFIG, last_alarms
    
    if request.method == 'GET':
        return jsonify({
            'status': 'success',
            'config': ALARM_CONFIG
        })
    
    elif request.method == 'PUT':
        try:
            data = request.get_json()
            ALARM_CONFIG.update(data)
            
            # Recalcular alarmas
            last_alarms = generate_alarms(last_predictions)
            
            return jsonify({
                'status': 'success',
                'message': 'Alarm config updated',
                'config': ALARM_CONFIG
            })
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)}), 400

@app.route('/api/variables', methods=['GET'])
def variables_info():
    """GET /api/variables - Información sobre variables monitoreadas"""
    info = {}
    for field, data in VARIABLES.items():
        info[field] = {
            'name': data['name'],
            'min': data['min'],
            'max': data['max'],
            'alarm_config': ALARM_CONFIG.get(field, {})
        }
    
    return jsonify({
        'status': 'success',
        'variables': info
    })

@app.errorhandler(404)
def not_found(e):
    return jsonify({
        'status': 'error',
        'message': 'Endpoint not found',
        'available': [
            '/api/predictions',
            '/api/alarms',
            '/api/traffic-light',
            '/api/health',
            '/api/config/alarms',
            '/api/variables',
            '/api/train (POST)'
        ]
    }), 404

if __name__ == '__main__':
    # Inicializar
    init_predictions()
    
    # Iniciar actualización en background
    bg_thread = threading.Thread(target=update_predictions_background, daemon=True)
    bg_thread.start()
    
    # Ejecutar servidor
    print("\n" + "="*60)
    print("SERVIDOR DE PREDICCIONES Y ALARMAS")
    print("="*60)
    print("Iniciando en http://0.0.0.0:5000")
    print("Predicciones: http://localhost:5000/api/predictions")
    print("Alarmas: http://localhost:5000/api/alarms")
    print("Semaforo: http://localhost:5000/api/traffic-light")
    print("="*60 + "\n")
    
    app.run(host='0.0.0.0', port=5000, debug=False)
