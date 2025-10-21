from http.server import HTTPServer, SimpleHTTPRequestHandler
import json
import os
import urllib.request
from urllib.parse import urlparse

class ProxyHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse(self.path)
        
        # Redirigir raíz a dashboard.html para comodidad
        if parsed_path.path in ('/', '/index.html'):
            self.path = '/dashboard.html'
            return SimpleHTTPRequestHandler.do_GET(self)

        # Rutas del API proxy
        if parsed_path.path.startswith('/api/thingspeak/'):
            channel_type = parsed_path.path.split('/')[-1]
            
            channels = {
                'soil': {'id': '2791076', 'key': 'ILV07NI5I2GUTD41'},
                'weather': {'id': '2791069', 'key': 'MN0TNLAPB9EF24DQ'},
                'matric_uv': {'id': '2906294', 'key': 'TK8VXZFSN2T5GNTL'}
            }
            
            if channel_type in channels:
                ch = channels[channel_type]
                url = f"https://api.thingspeak.com/channels/{ch['id']}/feeds.json?api_key={ch['key']}&results=10"
                
                try:
                    with urllib.request.urlopen(url, timeout=10) as response:
                        data = response.read()
                    
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    self.wfile.write(data)
                    return
                except Exception as e:
                    self.send_response(500)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({'error': str(e)}).encode())
                    return
        
        # Archivos estáticos
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
