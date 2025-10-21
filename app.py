from flask import Flask, request, jsonify, send_from_directory
from flask_socketio import SocketIO, emit
from datetime import datetime

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Almacenamiento temporal de datos
sensor_data = {
    'ph': [],
    'temperatura': [],
    'humedad': []
}

@app.route('/')
def index():
    return send_from_directory('public', 'index.html')

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory('public', path)

@app.route('/api/sensors', methods=['POST'])
def receive_sensor_data():
    data = request.json
    sensor = data.get('sensor')
    value = data.get('value')
    
    if sensor in sensor_data:
        # Guardar datos con timestamp
        sensor_data[sensor].append({
            'value': float(value),
            'timestamp': datetime.now().isoformat()
        })
        
        # Mantener solo los últimos 100 datos
        if len(sensor_data[sensor]) > 100:
            sensor_data[sensor].pop(0)
            
        # Emitir actualización a través de Socket.IO
        socketio.emit('sensor-update', {'sensor': sensor, 'value': float(value)})
        return jsonify({'success': True})
    
    return jsonify({'error': 'Sensor no válido'}), 400

@app.route('/api/data', methods=['GET'])
def get_all_data():
    return jsonify(sensor_data)

@socketio.on('connect')
def handle_connect():
    # Enviar datos actuales al nuevo cliente
    emit('initial-data', sensor_data)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=3000, debug=True)