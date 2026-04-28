#!/usr/bin/env python3
"""
AgroTasker Server - Sistema Inteligente de Cultivo de Mango
Servidor proxy con caching, filtrado inteligente y soporte CORS
"""

from http.server import HTTPServer, SimpleHTTPRequestHandler
import json
import urllib.request
import urllib.error
from urllib.parse import urljoin
import time
from datetime import datetime
import os
import io
import csv
import zipfile
import unicodedata
from urllib.parse import urlparse

class ProxyHandler(SimpleHTTPRequestHandler):
    """Maneja solicitudes HTTP y sirve datos derivados de Dropbox."""

    DROPBOX_WEEKLY_ZIP_URL = os.getenv(
        'DROPBOX_WEEKLY_ZIP_URL',
        'https://www.dropbox.com/scl/fo/krvc94h3vbqwwblm2dex7/AGn4F268L5Zzvq-Ikr98PHY?rlkey=otk6nty4ik2hq53nihbim6jkq&dl=1'
    )
    DROPBOX_CACHE_KEY = 'dropbox_series'
    DROPBOX_CACHE_TIME = 60  # 1 minuto para refresco casi en tiempo real
    DROPBOX_METRICS = {
        'humedad del suelo': 'humedadSuelo',
        'temperatura': 'tempAire',
        'ph del suelo': 'phSuelo',
        'humedad relativa': 'humedadAire'
    }
    
    # Configuración de canales lógicos expuestos al dashboard
    CHANNELS = {
        'soil': {
            'id': '2791076',
            'key': 'ILV07NI5I2GUTD41',
            'url': 'https://api.thingspeak.com/channels/2791076/feeds.json'
        },
        'weather': {
            'id': '2791069',
            'key': 'MN0TNLAPB9EF24DQ',
            'url': 'https://api.thingspeak.com/channels/2791069/feeds.json'
        },
        'matric_uv': {
            'id': '2906294',
            'key': 'TK8VXZFSN2T5GNTL',
            'url': 'https://api.thingspeak.com/channels/2906294/feeds.json'
        }
    }

    # Canal secundario (7 fields) para integración dual en dashboard_realtime_dual.html
    SECONDARY_CHANNEL_ID = os.getenv('THINGSPEAK_SECONDARY_CHANNEL_ID', '3341502').strip()
    SECONDARY_READ_KEY = os.getenv('THINGSPEAK_SECONDARY_READ_KEY', 'CUCMUN5YZ3DAS3NX').strip()
    SECONDARY_WRITE_KEY = os.getenv('THINGSPEAK_SECONDARY_WRITE_KEY', 'HR96S1DF966QGFTB').strip()
    
    # Cache para reducir llamadas a API
    cache = {}
    cache_time = 300  # segundos (5 minutos)
    
    def do_GET(self):
        """Maneja solicitudes GET"""
        path_only = urlparse(self.path).path
        
        # Rutas de API (solo estas son JSON)
        if path_only.startswith('/api/thingspeak/'):
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()
            
            channel_type = path_only.replace('/api/thingspeak/', '').replace('/', '')
            data = self.get_thingspeak_data(channel_type)
            self.wfile.write(json.dumps(data).encode())
            return

        if path_only.startswith('/api/dropbox/series'):
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()

            data = self.get_dropbox_series_data()
            self.wfile.write(json.dumps(data).encode())
            return

        if path_only.startswith('/api/data/merged'):
            # Endpoint: /api/data/merged?channel=soil&user_channel_id=...&user_api_key=...
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()

            # Parse query params
            from urllib.parse import parse_qs
            qs = parse_qs(urlparse(self.path).query)
            channel = qs.get('channel', ['soil'])[0]
            user_channel_id = qs.get('user_channel_id', [None])[0]
            user_api_key = qs.get('user_api_key', [None])[0]
            max_gap_minutes = int(qs.get('max_gap_minutes', [30])[0])

            # Si no envían canal secundario en query, usar valores por defecto del servidor.
            if not user_channel_id and self.SECONDARY_CHANNEL_ID:
                user_channel_id = self.SECONDARY_CHANNEL_ID
            if not user_api_key and self.SECONDARY_READ_KEY:
                user_api_key = self.SECONDARY_READ_KEY

            data = self.get_merged_data(channel, user_channel_id, user_api_key, max_gap_minutes)
            self.wfile.write(json.dumps(data).encode())
            return
        
        # Servir archivos estáticos (HTML, CSS, JS)
        if self.path == '/':
            self.path = '/index-menu.html'
        elif self.path == '':
            self.path = '/index-menu.html'
        
        try:
            return super().do_GET()
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': str(e)}).encode())
    
    def do_OPTIONS(self):
        """Maneja CORS preflight"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def get_thingspeak_data(self, channel_type):
        """Obtiene datos de ThingSpeak real con fallback a Dropbox sintético."""
        
        if channel_type not in self.CHANNELS:
            return {'error': 'Channel not found', 'feeds': []}

        now = time.time()
        
        # Verificar caché
        if channel_type in self.cache:
            cached_data, cache_timestamp = self.cache[channel_type]
            if now - cache_timestamp < self.cache_time:
                print(f"[CACHE] {channel_type} - Data from cache ({self.cache_time}s)")
                return cached_data

        channel = self.CHANNELS[channel_type]
        try:
            url = f"{channel['url']}?api_key={channel['key']}&results=8000"
            req = urllib.request.Request(url, headers={'User-Agent': 'AgroTasker'})
            with urllib.request.urlopen(req, timeout=8) as response:
                data = json.loads(response.read().decode())

            if 'feeds' in data:
                data['feeds'] = self.clean_feeds(data['feeds'])

            data['source'] = 'thingspeak'
            self.cache[channel_type] = (data, now)
            print(f"[API] {channel_type} - {len(data.get('feeds', []))} records from ThingSpeak")
            return data
        except Exception as e:
            print(f"[WARN] {channel_type} ThingSpeak unavailable: {e}")

            # Fallback: sintetizar desde Dropbox para no romper el dashboard.
            try:
                drop = self.get_dropbox_series_data()
                series = drop.get('series', []) if isinstance(drop, dict) else []
                if series:
                    data = self.build_synthetic_thingspeak_data(channel_type, series)
                    self.cache[channel_type] = (data, now)
                    print(f"[FALLBACK] {channel_type} - synthetic feeds from Dropbox ({len(series)} records)")
                    return data
            except Exception as drop_error:
                print(f"[ERROR] fallback dropbox for {channel_type}: {drop_error}")

            # Último fallback: caché vieja si existe.
            if channel_type in self.cache:
                cached_data, _ = self.cache[channel_type]
                return cached_data

            return {
                'source': 'thingspeak',
                'error': str(e),
                'feeds': [],
                'channel': {'id': channel['id'], 'name': channel_type},
                'created_at': datetime.now().isoformat()
            }

    def build_synthetic_thingspeak_data(self, channel_type, series):
        """Construye feeds con forma ThingSpeak a partir de la serie de Dropbox."""
        channel = self.CHANNELS[channel_type]
        feeds = []

        for entry_id, row in enumerate(series, start=1):
            created_at = row.get('created_at') or datetime.now().isoformat()
            temp_aire = self.parse_float(row.get('tempAire')) or 0.0
            humedad_suelo = self.parse_float(row.get('humedadSuelo')) or 0.0
            ph_suelo = self.parse_float(row.get('phSuelo')) or 0.0
            humedad_aire = self.parse_float(row.get('humedadAire')) or 0.0

            if channel_type == 'soil':
                feed = {
                    'entry_id': entry_id,
                    'created_at': created_at,
                    'field1': round(humedad_suelo, 2),
                    'field2': round(max(0.0, temp_aire - 1.5), 2),
                    'field3': round(max(0.1, ph_suelo), 2),
                    'field4': round(max(1.0, humedad_suelo * 14 + 120), 2),
                    'field5': round(max(1.0, humedad_suelo * 4 + 180), 2),
                    'field6': round(max(1.0, humedad_suelo * 2.5 + 40), 2),
                    'field7': round(max(1.0, humedad_suelo * 5 + 150), 2)
                }
            elif channel_type == 'weather':
                feed = {
                    'entry_id': entry_id,
                    'created_at': created_at,
                    'field1': round((temp_aire * 11 + humedad_aire) % 360, 2),
                    'field2': round(max(0.1, (100 - humedad_aire) / 8 + 1.2), 2),
                    'field3': round(max(0.0, (humedad_aire - 65) / 12), 2),
                    'field4': round(temp_aire, 2),
                    'field5': round(max(0.1, humedad_aire), 2),
                    'field6': round(max(900.0, 1013.25 - (humedad_aire - 50) * 0.7), 2)
                }
            else:
                uv_index = round(max(0.1, (temp_aire - 18) * 0.45 + (100 - humedad_aire) / 30), 2)
                resistance_30 = round(max(1.0, 2200 - humedad_suelo * 26), 2)
                resistance_60 = round(max(1.0, resistance_30 * 1.08), 2)
                feed = {
                    'entry_id': entry_id,
                    'created_at': created_at,
                    'field1': resistance_30,
                    'field2': resistance_60,
                    'field3': uv_index
                }

            feeds.append(feed)

        return {
            'source': 'dropbox',
            'channel': {
                'id': channel['id'],
                'name': channel_type
            },
            'feeds': feeds,
            'meta': {
                'records': len(feeds),
                'cached_at': datetime.now().isoformat()
            }
        }

    def normalize_text(self, text):
        """Normaliza texto para comparaciones de nombres sin acentos."""
        normalized = unicodedata.normalize('NFD', text)
        without_marks = ''.join(ch for ch in normalized if unicodedata.category(ch) != 'Mn')
        return without_marks.strip().lower()

    def parse_float(self, value):
        """Convierte valores numéricos en texto a float de forma tolerante."""
        if value is None:
            return None

        raw = str(value).strip().replace(',', '.')
        if raw == '':
            return None

        try:
            return float(raw)
        except ValueError:
            return None

    def parse_created_at(self, value):
        """Convierte timestamps CSV a datetime con fallback."""
        if not value:
            return None

        text = value.strip()
        # ThingSpeak usa ISO 8601 con sufijo Z
        if text.endswith('Z'):
            text = text.replace('Z', '+00:00')

        try:
            return datetime.fromisoformat(text)
        except ValueError:
            pass

        for fmt in ('%Y-%m-%d %H:%M:%S %z', '%Y-%m-%d %H:%M:%S'):
            try:
                return datetime.strptime(text, fmt)
            except ValueError:
                continue

        return None

    def get_dropbox_series_data(self):
        """Descarga y unifica CSV semanales de Dropbox para las 4 variables clave."""
        now = time.time()
        cache_entry = self.cache.get(self.DROPBOX_CACHE_KEY)
        if cache_entry:
            cached_data, cached_at = cache_entry
            if now - cached_at < self.DROPBOX_CACHE_TIME:
                print(f"[CACHE] dropbox_series - Data from cache ({self.DROPBOX_CACHE_TIME}s)")
                return cached_data

        try:
            request = urllib.request.Request(
                self.DROPBOX_WEEKLY_ZIP_URL,
                headers={'User-Agent': 'AgroTasker'}
            )

            with urllib.request.urlopen(request, timeout=20) as response:
                zip_bytes = response.read()

            rows_by_timestamp = {}

            with zipfile.ZipFile(io.BytesIO(zip_bytes)) as weekly_zip:
                for member in weekly_zip.namelist():
                    if member.endswith('/'):
                        continue

                    basename = os.path.basename(member)
                    metric_name = os.path.splitext(basename)[0]
                    metric_key = self.DROPBOX_METRICS.get(self.normalize_text(metric_name))
                    if not metric_key:
                        continue

                    with weekly_zip.open(member) as csv_file:
                        text_stream = io.TextIOWrapper(csv_file, encoding='utf-8-sig', errors='replace')
                        reader = csv.DictReader(text_stream)

                        for row in reader:
                            created_at = (row.get('created_at') or '').strip()
                            if not created_at:
                                continue

                            value = None
                            for key, raw_value in row.items():
                                if key and key.lower().startswith('field'):
                                    value = self.parse_float(raw_value)
                                    break

                            if value is None or value <= 0:
                                continue

                            item = rows_by_timestamp.setdefault(created_at, {'created_at': created_at})
                            item[metric_key] = value

            required = ['tempAire', 'humedadSuelo', 'phSuelo', 'humedadAire']
            sorted_rows = sorted(
                rows_by_timestamp.values(),
                key=lambda row: self.parse_created_at(row.get('created_at')) or datetime.min
            )

            filled_rows = []
            last_values = {}
            for row in sorted_rows:
                merged = {'created_at': row.get('created_at')}
                for metric in required:
                    current = row.get(metric)
                    if current is not None:
                        last_values[metric] = current
                        merged[metric] = current
                    elif metric in last_values:
                        merged[metric] = last_values[metric]

                if all(metric in merged for metric in required):
                    filled_rows.append(merged)

            data = {
                'source': 'dropbox',
                'series': filled_rows,
                'meta': {
                    'records': len(filled_rows),
                    'cached_at': datetime.now().isoformat(),
                    'url': self.DROPBOX_WEEKLY_ZIP_URL
                }
            }

            self.cache[self.DROPBOX_CACHE_KEY] = (data, now)
            print(f"[API] dropbox_series - {len(filled_rows)} records")
            return data
        except Exception as e:
            print(f"[ERROR] dropbox_series - {str(e)}")

            if cache_entry:
                cached_data, _ = cache_entry
                return cached_data

            return {
                'error': str(e),
                'source': 'dropbox',
                'series': [],
                'meta': {
                    'records': 0,
                    'cached_at': datetime.now().isoformat(),
                    'url': self.DROPBOX_WEEKLY_ZIP_URL
                }
            }
    
    def fetch_thingspeak_by_channel(self, channel_id, api_key=None, results=8000):
        """Obtiene feeds por channel id (público o privado con read api key)."""
        try:
            base_url = f"https://api.thingspeak.com/channels/{channel_id}/feeds.json"
            url = f"{base_url}?results={results}"
            if api_key:
                url += f"&api_key={api_key}"

            req = urllib.request.Request(url, headers={'User-Agent': 'AgroTasker'})
            with urllib.request.urlopen(req, timeout=8) as response:
                data = json.loads(response.read().decode())

            if 'feeds' in data:
                data['feeds'] = self.clean_feeds(data['feeds'])

            data['source'] = 'thingspeak'
            return data
        except Exception as e:
            print(f"[ERROR] fetch_thingspeak_by_channel {channel_id} - {e}")
            return {'error': str(e), 'feeds': [], 'source': 'thingspeak'}

    def get_merged_data(self, channel_type='soil', user_channel_id=None, user_api_key=None, max_gap_minutes=30):
        """Fusiona series de Dropbox con ThingSpeak (canal interno) y opcional ThingSpeak del usuario.

        Strategy: para cada fila de Dropbox, busca el feed ThingSpeak más cercano dentro de max_gap_minutes
        y lo adjunta; también incluye feeds de ThingSpeak que no encontraron match.
        """
        try:
            dropbox = self.get_dropbox_series_data()
            if 'series' not in dropbox:
                dropbox['series'] = []

            # Obtener feeds del canal interno (si existe en CHANNELS)
            things_data = {'feeds': []}
            if channel_type in self.CHANNELS:
                things_data = self.get_thingspeak_data(channel_type)
            else:
                # Try to interpret channel_type as id
                things_data = self.fetch_thingspeak_by_channel(channel_type)

            # Obtener feeds del usuario si se pidió
            user_data = None
            if user_channel_id:
                user_data = self.fetch_thingspeak_by_channel(user_channel_id, user_api_key)

            # Parse ThingSpeak feeds into list with parsed datetime
            def parse_feeds(feeds):
                parsed = []
                for f in feeds:
                    created = f.get('created_at')
                    ts = self.parse_created_at(created.isoformat() if isinstance(created, datetime) else (created or ''))
                    parsed.append({'raw': f, 'created_at': created, 'dt': ts})
                return parsed

            feeds_parsed = parse_feeds(things_data.get('feeds', []))
            user_parsed = parse_feeds(user_data.get('feeds', [])) if user_data else []

            # Index user feeds by epoch for nearest search
            def to_epoch(dt):
                if not dt:
                    return None
                return int(dt.timestamp())

            max_gap = max_gap_minutes * 60

            merged = []
            # For each dropbox row, find nearest feed
            for row in dropbox.get('series', []):
                created = row.get('created_at')
                dt = self.parse_created_at(created)
                epoch = to_epoch(dt)
                nearest = None
                nearest_dt = None
                if epoch and feeds_parsed:
                    best = None
                    best_gap = None
                    for f in feeds_parsed:
                        fe = to_epoch(f['dt'])
                        if fe is None:
                            continue
                        gap = abs(fe - epoch)
                        if best is None or gap < best_gap:
                            best = f
                            best_gap = gap
                    if best and best_gap <= max_gap:
                        nearest = best['raw']
                        nearest_dt = best['dt']

                merged_item = {
                    'created_at': created,
                    'dropbox': row,
                    'thingspeak_nearest': nearest,
                    'thingspeak_nearest_dt': (nearest_dt.isoformat() if nearest_dt else None)
                }
                merged.append(merged_item)

            # Also include ThingSpeak feeds that had no matching dropbox (recent readings)
            matched_things = set()
            for m in merged:
                if m['thingspeak_nearest']:
                    matched_things.add(m['thingspeak_nearest'].get('entry_id'))

            extra_things = []
            for f in feeds_parsed:
                eid = f['raw'].get('entry_id')
                if eid and eid not in matched_things:
                    extra_things.append({'created_at': f['raw'].get('created_at'), 'thingspeak': f['raw']})

            # Build response
            response = {
                'merged': merged,
                'extra_thingspeak': extra_things,
                'dropbox_meta': dropbox.get('meta', {}),
                'thingspeak_meta': {'count': len(feeds_parsed)},
                'user_thingspeak_meta': {'count': len(user_parsed) if user_parsed else 0}
            }

            if user_parsed:
                response['user_thingspeak'] = [u['raw'] for u in user_parsed]

            return response
        except Exception as e:
            print(f"[ERROR] get_merged_data - {e}")
            return {'error': str(e), 'merged': [], 'dropbox_meta': {}, 'thingspeak_meta': {}}
    
    def clean_feeds(self, feeds):
        """Filtra valores cero y nulos de manera inteligente"""
        cleaned = []
        
        for feed in feeds:
            # Verificar si tiene al menos un campo válido
            has_valid_data = False
            
            for i in range(1, 9):
                field = f'field{i}'
                if field in feed and feed[field] is not None:
                    value = float(feed[field]) if feed[field] else 0
                    # Solo incluir si es diferente de cero o si es un campo importante
                    if value > 0 or field in ['field4', 'field3']:  # Conductividad y pH
                        has_valid_data = True
                        break
            
            if has_valid_data:
                cleaned.append(feed)
        
        return cleaned
    
    def log_message(self, format, *args):
        """Personalizar log de servidor"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        print(f"[{timestamp}] {format % args}")


def start_server(host='0.0.0.0', port=8080):
    """Inicia el servidor HTTP"""
    
    server_address = (host, port)
    httpd = HTTPServer(server_address, ProxyHandler)
    
    print("=" * 60)
    print("🌱 AgroTasker Server - Sistema Inteligente")
    print("=" * 60)
    print(f"✓ Servidor iniciado en http://{host}:{port}")
    print(f"✓ Dashboard simple: http://{host}:{port}/dashboard_simple.html")
    print(f"✓ Dashboard avanzado: http://{host}:{port}/dashboard_advanced.html")
    print(f"✓ Menú de selección: http://{host}:{port}/index-menu.html")
    print("✓ API endpoints:")
    print(f"  - /api/thingspeak/soil")
    print(f"  - /api/thingspeak/weather")
    print(f"  - /api/thingspeak/matric_uv")
    print(f"  - /api/dropbox/series")
    print(f"  - /api/data/merged?channel=soil&user_channel_id=ID&user_api_key=KEY")
    print("=" * 60)
    print("Presiona Ctrl+C para detener el servidor\n")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\n✓ Servidor detenido correctamente")
        httpd.server_close()


if __name__ == '__main__':
    # Cambiar a directorio del script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # Iniciar servidor
    start_server()
