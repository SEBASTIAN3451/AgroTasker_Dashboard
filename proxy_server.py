from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
import requests
import os

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)  # Habilitar CORS para todas las rutas

# Configuración de ThingSpeak
THINGSPEAK_CHANNELS = {
    'weather': {
        'id': '2791069',
        'api_key': 'MN0TNLAPB9EF24DQ'
    },
    'soil': {
        'id': '2791076',
        'api_key': 'ILV07NI5I2GUTD41'
    },
    'matric_uv': {
        'id': '2906294',
        'api_key': 'TK8VXZFSN2T5GNTL'
    }
}

@app.route('/')
def index():
    return send_from_directory('.', 'dashboard.html')

@app.route('/<path:path>')
def static_files(path):
    try:
        return send_from_directory('.', path)
    except:
        return jsonify({'error': 'File not found'}), 404

@app.route('/api/thingspeak/<channel_type>')
def get_thingspeak_data(channel_type):
    """Proxy para obtener datos de ThingSpeak"""
    if channel_type not in THINGSPEAK_CHANNELS:
        return jsonify({'error': 'Canal no encontrado'}), 404
    
    channel = THINGSPEAK_CHANNELS[channel_type]
    url = f"https://api.thingspeak.com/channels/{channel['id']}/feeds.json"
    params = {
        'api_key': channel['api_key'],
        'results': 10  # Últimos 10 resultados
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return jsonify(response.json())
    except requests.exceptions.RequestException as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000, debug=True)
