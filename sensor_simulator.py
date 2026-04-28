import paho.mqtt.publish as publish
import time
import random
from datetime import datetime
import os
import base64
import json
import urllib.parse
import urllib.request
import urllib.error

# Configuración MQTT
MQTT_BROKER = "test.mosquitto.org"
MQTT_PORT = 1883
MQTT_TOPICS = {
    'ph': 'agrotasker/test/sensor/ph',
    'temperatura': 'agrotasker/test/sensor/temperatura',
    'humedad': 'agrotasker/test/sensor/humedad_suelo',
    'humedad_aire': 'agrotasker/test/sensor/humedad_aire'
}

# Configuración de los rangos de los sensores
SENSOR_RANGES = {
    # Rangos alineados al dashboard/ThingSpeak para mantener lógica de semáforo.
    'ph': {'min': 5.0, 'max': 8.1, 'variation': 0.05, 'target': 6.5},
    'temperatura': {'min': 20.0, 'max': 37.0, 'variation': 0.75, 'target': 28.2},
    'humedad': {'min': 30.0, 'max': 85.0, 'variation': 1.0, 'target': 68.0},
    'humedad_aire': {'min': 35.0, 'max': 92.0, 'variation': 1.1, 'target': 72.0},
    'conductividad': {'min': 120.0, 'max': 1800.0, 'variation': 35.0, 'target': 650.0},
    'nitrogeno': {'min': 120.0, 'max': 360.0, 'variation': 6.0, 'target': 245.0},
    'fosforo': {'min': 20.0, 'max': 90.0, 'variation': 2.0, 'target': 52.0},
    'potasio': {'min': 120.0, 'max': 320.0, 'variation': 5.0, 'target': 210.0}
}

# Configuración ThingSpeak
THINGSPEAK_UPDATE_URL = "https://api.thingspeak.com/update"
THINGSPEAK_MIN_INTERVAL = 15  # ThingSpeak free acepta 1 update cada 15s aprox.
THINGSPEAK_SOIL_WRITE_KEY = os.getenv('THINGSPEAK_SOIL_WRITE_KEY', '').strip()

# Alertas externas (simulación por defecto, envío real opcional con Twilio).
def env_bool(name, default=False):
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in ('1', 'true', 'yes', 'si', 'on')


EXTERNAL_ALERTS_ENABLED = env_bool('EXTERNAL_ALERTS_ENABLED', True)
EXTERNAL_ALERT_COOLDOWN = 90
ALERT_SIMULATION_ONLY = env_bool('ALERT_SIMULATION_ONLY', True)
ALERT_CHANNELS = [
    part.strip().lower()
    for part in os.getenv('ALERT_CHANNELS', 'whatsapp,sms').split(',')
    if part.strip()
]

TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID', '').strip()
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN', '').strip()
TWILIO_FROM_WHATSAPP = os.getenv('TWILIO_FROM_WHATSAPP', '').strip()
TWILIO_FROM_SMS = os.getenv('TWILIO_FROM_SMS', '').strip()
ALERT_TO_WHATSAPP = os.getenv('ALERT_TO_WHATSAPP', '').strip()
ALERT_TO_SMS = os.getenv('ALERT_TO_SMS', '').strip()

class SensorSimulator:
    def __init__(self):
        # Inicializar valores de sensores
        self.values = {
            'ph': 6.5,
            'temperatura': 27.0,
            'humedad': 67.0,
            'humedad_aire': 71.0,
            'conductividad': 640.0,
            'nitrogeno': 240.0,
            'fosforo': 50.0,
            'potasio': 205.0
        }
        self.last_thingspeak_publish = 0
        self.last_external_alert = 0
        self.tick_count = 0

    def clamp(self, value, low, high):
        return max(low, min(high, value))

    def status_for(self, sensor, value):
        if sensor == 'temperatura':
            if 30 <= value < 34:
                return 'verde'
            if (27 <= value < 30) or (34 <= value < 42):
                return 'amarillo'
            return 'rojo'

        if sensor == 'humedad':
            if 20 <= value <= 35:
                return 'verde'
            if (15 <= value < 20) or (35 < value <= 40):
                return 'amarillo'
            return 'rojo'

        if sensor == 'ph':
            if 5.5 <= value < 7.0:
                return 'verde'
            if value < 5.5 or (7.0 <= value < 7.5):
                return 'amarillo'
            return 'rojo'

        if sensor == 'humedad_aire':
            if 60 <= value < 70:
                return 'verde'
            if (50 <= value < 60) or (70 <= value < 80):
                return 'amarillo'
            return 'rojo'

        return 'amarillo'

    def maybe_external_alert(self):
        if not EXTERNAL_ALERTS_ENABLED:
            return

        now = time.time()
        if now - self.last_external_alert < EXTERNAL_ALERT_COOLDOWN:
            return

        critical = [
            s for s, v in self.values.items()
            if self.status_for(s, v) == 'rojo'
        ]
        if critical:
            message = self.build_alert_message(critical)

            if ALERT_SIMULATION_ONLY:
                self.simulate_alert_delivery(message)
                self.last_external_alert = now
                return

            sent = False
            if 'whatsapp' in ALERT_CHANNELS:
                ok, detail = self.send_whatsapp_alert(message)
                print(f"{datetime.now().strftime('%H:%M:%S')} - WhatsApp: {detail}")
                sent = sent or ok

            if 'sms' in ALERT_CHANNELS:
                ok, detail = self.send_sms_alert(message)
                print(f"{datetime.now().strftime('%H:%M:%S')} - SMS: {detail}")
                sent = sent or ok

            if sent:
                self.last_external_alert = now

    def build_alert_message(self, critical):
        metrics = []
        if 'temperatura' in critical:
            metrics.append(f"T={self.values['temperatura']:.2f}°C")
        if 'humedad' in critical:
            metrics.append(f"HS={self.values['humedad']:.2f}%")
        if 'ph' in critical:
            metrics.append(f"pH={self.values['ph']:.2f}")
        if 'humedad_aire' in critical:
            metrics.append(f"HA={self.values['humedad_aire']:.2f}%")

        metrics_text = ', '.join(metrics) if metrics else 'sin métricas'
        return (
            f"ALERTA AgroTasker: variables críticas: {', '.join(critical)}. "
            f"Lecturas: {metrics_text}. Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )

    def simulate_alert_delivery(self, message):
        channels = '/'.join(ALERT_CHANNELS) if ALERT_CHANNELS else 'whatsapp/sms'
        print(f"{datetime.now().strftime('%H:%M:%S')} - SIM ALERT [{channels}]: {message}")

    def twilio_send_message(self, from_number, to_number, body):
        if not TWILIO_ACCOUNT_SID or not TWILIO_AUTH_TOKEN:
            return False, "credenciales Twilio faltantes"
        if not from_number or not to_number:
            return False, "número origen/destino faltante"

        payload = urllib.parse.urlencode({
            'From': from_number,
            'To': to_number,
            'Body': body
        }).encode('utf-8')

        url = f"https://api.twilio.com/2010-04-01/Accounts/{TWILIO_ACCOUNT_SID}/Messages.json"
        token = base64.b64encode(f"{TWILIO_ACCOUNT_SID}:{TWILIO_AUTH_TOKEN}".encode('utf-8')).decode('ascii')
        request = urllib.request.Request(url, data=payload, method='POST')
        request.add_header('Authorization', f"Basic {token}")

        try:
            with urllib.request.urlopen(request, timeout=15) as response:
                response_payload = json.loads(response.read().decode('utf-8'))
            sid = response_payload.get('sid', 'sin_sid')
            return True, f"enviado sid={sid}"
        except urllib.error.HTTPError as error:
            detail = error.read().decode('utf-8', errors='replace')
            return False, f"HTTP {error.code}: {detail}"
        except Exception as error:
            return False, f"error envío: {error}"

    def send_whatsapp_alert(self, message):
        from_number = TWILIO_FROM_WHATSAPP
        to_number = ALERT_TO_WHATSAPP
        if from_number and not from_number.startswith('whatsapp:'):
            from_number = f"whatsapp:{from_number}"
        if to_number and not to_number.startswith('whatsapp:'):
            to_number = f"whatsapp:{to_number}"
        return self.twilio_send_message(from_number, to_number, message)

    def send_sms_alert(self, message):
        return self.twilio_send_message(TWILIO_FROM_SMS, ALERT_TO_SMS, message)

    def update_sensor_value(self, sensor):
        current = self.values[sensor]
        ranges = SENSOR_RANGES[sensor]

        drift = random.uniform(-ranges['variation'], ranges['variation'])
        pull = (ranges['target'] - current) * 0.18
        new_value = current + drift + pull

        # Acople ambiental: cuando sube temperatura, baja humedad ambiente y suelo.
        if sensor == 'humedad_aire':
            temp = self.values['temperatura']
            new_value -= max(0, temp - 30) * 0.22
        if sensor == 'humedad':
            temp = self.values['temperatura']
            hum_aire = self.values['humedad_aire']
            new_value -= max(0, temp - 30) * 0.25
            if hum_aire < 50:
                new_value -= 0.35

        # Eventos raros realistas.
        if sensor == 'temperatura' and random.random() < 0.01:
            new_value = random.uniform(35.1, 36.8)
        # Pulso térmico controlado para que la semaforización/alertas no queden planas.
        if sensor == 'temperatura' and random.random() < 0.05:
            new_value += random.uniform(0.8, 2.1)
        if sensor == 'humedad' and random.random() < 0.012:
            new_value = random.uniform(33.0, 39.0)
        if sensor == 'humedad' and random.random() < 0.02:
            new_value += random.uniform(4.0, 7.0)  # riego/lluvia

        new_value = self.clamp(new_value, ranges['min'], ranges['max'])
        self.values[sensor] = new_value
        return new_value

    def update_soil_npk(self):
        temp = self.values['temperatura']
        humedad = self.values['humedad']
        ph = self.values['ph']

        # A mayor temperatura/humedad extrema, simula lavado o consumo de nutrientes.
        stress = max(0.0, temp - 31.0) * 0.7 + max(0.0, humedad - 78.0) * 0.12
        ph_penalty = 0.0 if 5.8 <= ph <= 7.2 else 1.8

        for nutrient in ('nitrogeno', 'fosforo', 'potasio'):
            cfg = SENSOR_RANGES[nutrient]
            current = self.values[nutrient]
            drift = random.uniform(-cfg['variation'], cfg['variation'])
            pull = (cfg['target'] - current) * 0.10
            new_value = current + drift + pull - stress - ph_penalty

            # Pulso positivo ocasional para representar fertilización.
            if random.random() < 0.03:
                new_value += random.uniform(4.0, 14.0)

            self.values[nutrient] = self.clamp(new_value, cfg['min'], cfg['max'])

        cond_cfg = SENSOR_RANGES['conductividad']
        cond_base = 340 + self.values['nitrogeno'] * 0.8 + self.values['potasio'] * 0.4 + self.values['fosforo'] * 0.5
        cond_drift = random.uniform(-cond_cfg['variation'], cond_cfg['variation'])
        cond_penalty = max(0.0, humedad - 80.0) * 4.0
        conductivity = cond_base + cond_drift - cond_penalty
        self.values['conductividad'] = self.clamp(conductivity, cond_cfg['min'], cond_cfg['max'])

    def publish_to_thingspeak(self):
        if not THINGSPEAK_SOIL_WRITE_KEY:
            return False, "WRITE API KEY no configurada"

        now = time.time()
        if now - self.last_thingspeak_publish < THINGSPEAK_MIN_INTERVAL:
            seconds_left = int(THINGSPEAK_MIN_INTERVAL - (now - self.last_thingspeak_publish))
            return False, f"esperando ventana ThingSpeak ({seconds_left}s)"

        payload = {
            'api_key': THINGSPEAK_SOIL_WRITE_KEY,
            'field1': f"{self.values['humedad']:.2f}",
            'field2': f"{self.values['temperatura']:.2f}",
            'field3': f"{self.values['ph']:.2f}",
            'field4': f"{self.values['conductividad']:.2f}",
            'field5': f"{self.values['nitrogeno']:.2f}",
            'field6': f"{self.values['fosforo']:.2f}",
            'field7': f"{self.values['potasio']:.2f}"
        }

        data = urllib.parse.urlencode(payload).encode('utf-8')
        request = urllib.request.Request(THINGSPEAK_UPDATE_URL, data=data, method='POST')

        try:
            with urllib.request.urlopen(request, timeout=8) as response:
                entry_id = response.read().decode('utf-8').strip()

            self.last_thingspeak_publish = now

            if entry_id and entry_id != '0':
                return True, f"entry_id={entry_id}"

            return False, "ThingSpeak rechazó el update (respuesta 0)"
        except Exception as error:
            return False, f"error ThingSpeak: {error}"

    def start_simulation(self):
        print("=== Simulador de Sensores AgroTasker ===")
        print("Presiona Ctrl+C para detener")
        print("---------------------------------------")
        print("\nRangos de simulación:")
        for sensor, range_data in SENSOR_RANGES.items():
            print(f"{sensor}: {range_data['min']} a {range_data['max']}")

        print("\nThingSpeak:")
        if THINGSPEAK_SOIL_WRITE_KEY:
            print("✓ Publicación habilitada (canal suelo field1-field7)")
        else:
            print("⚠ Publicación deshabilitada (define THINGSPEAK_SOIL_WRITE_KEY)")

        print("\nAlertas externas:")
        if not EXTERNAL_ALERTS_ENABLED:
            print("⚠ Alertas deshabilitadas (EXTERNAL_ALERTS_ENABLED=false)")
        elif ALERT_SIMULATION_ONLY:
            print(f"✓ Modo simulación activo ({'/'.join(ALERT_CHANNELS)})")
            print("  No envía mensajes reales. Solo imprime eventos de alerta.")
        else:
            print(f"✓ Envío real activo ({'/'.join(ALERT_CHANNELS)})")
            print("  Requiere credenciales/números de Twilio configurados en variables de entorno.")
        
        try:
            while True:
                # Actualizar y publicar valores de sensores
                messages = []
                for sensor, topic in MQTT_TOPICS.items():
                    value = self.update_sensor_value(sensor)
                    messages.append({'topic': topic, 'payload': f"{value:.2f}"})
                    status = self.status_for(sensor, value)
                    print(f"{datetime.now().strftime('%H:%M:%S')} - {sensor}: {value:.2f} [{status}]")

                self.update_soil_npk()
                print(
                    f"{datetime.now().strftime('%H:%M:%S')} - NPK: "
                    f"N={self.values['nitrogeno']:.2f} mg/kg, "
                    f"P={self.values['fosforo']:.2f} mg/kg, "
                    f"K={self.values['potasio']:.2f} mg/kg, "
                    f"EC={self.values['conductividad']:.2f} µS/cm"
                )
                
                # Publicar todos los mensajes
                publish.multiple(messages, hostname=MQTT_BROKER, port=MQTT_PORT)

                # Publicar en ThingSpeak (suelo: field1-field7)
                ok, detail = self.publish_to_thingspeak()
                if THINGSPEAK_SOIL_WRITE_KEY:
                    if ok:
                        print(f"{datetime.now().strftime('%H:%M:%S')} - ThingSpeak: {detail}")
                    else:
                        print(f"{datetime.now().strftime('%H:%M:%S')} - ThingSpeak: {detail}")

                self.maybe_external_alert()
                
                # Esperar antes de la siguiente actualización
                print("\nEsperando 5 segundos...\n")
                time.sleep(5)

        except KeyboardInterrupt:
            print("\nSimulador detenido.")

if __name__ == "__main__":
    print("=== Simulador de Sensores AgroTasker ===")
    print("Presiona Ctrl+C para detener")
    print("---------------------------------------")
    
    simulator = SensorSimulator()
    simulator.start_simulation()