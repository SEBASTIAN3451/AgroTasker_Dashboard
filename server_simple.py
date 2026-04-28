from http.server import HTTPServer, SimpleHTTPRequestHandler
import json
import os
import urllib.request
from urllib.parse import urlparse
import time

class ProxyHandler(SimpleHTTPRequestHandler):
    # Cache de datos para evitar solicitudes repetidas
    cache = {}
    cache_time = 300  # segundos (5 minutos)
    
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Cache-Control', 'max-age=30')
        super().end_headers()
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()
    
    def do_GET(self):
        parsed_path = urlparse(self.path)
        
        # Redirigir raíz a dashboard_simple.html
        if parsed_path.path in ('/', '/index.html', '/dashboard.html'):
            self.path = '/dashboard_simple.html'
            return SimpleHTTPRequestHandler.do_GET(self)

        if parsed_path.path.startswith('/api/thingspeak/'):
            channel_type = parsed_path.path.split('/')[-1]
            
            channels = {
                'soil': {'id': '2791076', 'key': 'ILV07NI5I2GUTD41'},
                'weather': {'id': '2791069', 'key': 'MN0TNLAPB9EF24DQ'},
                'matric_uv': {'id': '2906294', 'key': 'TK8VXZFSN2T5GNTL'}
            }
            
            if channel_type in channels:
                # Verificar caché
                now = time.time()
                if channel_type in self.cache:
                    cached_data, cache_timestamp = self.cache[channel_type]
                    if now - cache_timestamp < self.cache_time:
                        self.send_response(200)
                        self.send_header('Content-Type', 'application/json')
                        self.end_headers()
                        self.wfile.write(json.dumps(cached_data).encode())
                        return
                
                ch = channels[channel_type]
                url = f"https://api.thingspeak.com/channels/{ch['id']}/feeds.json?api_key={ch['key']}&results=60"
                
                try:
                    with urllib.request.urlopen(url, timeout=10) as response:
                        data = response.read()
                    
                    json_data = json.loads(data)
                    
                    # Limpiar datos: filtrar valores cero inútiles pero mantener datos válidos
                    if json_data.get('feeds'):
                        cleaned_feeds = []
                        for feed in json_data['feeds']:
                            cleaned_feed = {}
                            for key, value in feed.items():
                                if key == 'created_at':
                                    cleaned_feed[key] = value
                                elif value is not None and value != '' and value != '0':
                                    try:
                                        float_val = float(value)
                                        # Aceptar cualquier número válido (incluso 0 si es dato actual)
                                        cleaned_feed[key] = value
                                    except:
                                        pass
                            if cleaned_feed:
                                cleaned_feeds.append(cleaned_feed)
                        
                        json_data['feeds'] = cleaned_feeds
                    
                    # Guardar en caché
                    ProxyHandler.cache[channel_type] = (json_data, now)
                    
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps(json_data).encode())
                    return
                    
                except urllib.error.URLError as e:
                    # Error de conexión - retornar caché viejo si existe
                    if channel_type in self.cache:
                        cached_data, _ = self.cache[channel_type]
                        self.send_response(200)
                        self.send_header('Content-Type', 'application/json')
                        self.end_headers()
                        self.wfile.write(json.dumps(cached_data).encode())
                        return
                    
                    self.send_response(503)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({'error': 'ThingSpeak no disponible', 'feeds': []}).encode())
                    return
                    
                except Exception as e:
                    self.send_response(500)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({'error': str(e), 'feeds': []}).encode())
                    return
        
        return SimpleHTTPRequestHandler.do_GET(self)

if __name__ == '__main__':
    host = os.getenv('HOST', '0.0.0.0')  # 0.0.0.0 para permitir acceso en la red local
    port = int(os.getenv('PORT', '8080'))
    server = HTTPServer((host, port), ProxyHandler)
    print(f'Servidor iniciado en http://{host}:{port}')
    print('Sugerencia: si estás en la misma red, comparte la URL con la IP local, por ejemplo:')
    print(f'  http://<tu-ip-local>:{port}/dashboard.html')
    print('Presiona Ctrl+C para detener')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\nServidor detenido')
        server.shutdown()
