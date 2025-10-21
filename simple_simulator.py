import paho.mqtt.publish as publish
import time
import random
from datetime import datetime

# Configuración MQTT
MQTT_BROKER = "test.mosquitto.org"
MQTT_PORT = 1883

# Topics MQTT
TOPIC_PH = "agrotasker/test/sensor/ph"
TOPIC_TEMP = "agrotasker/test/sensor/temperatura"
TOPIC_HUM = "agrotasker/test/sensor/humedad"

print("=== Simulador Simple AgroTasker ===")
print(f"Conectando a {MQTT_BROKER}...")

try:
    while True:
        # Generar datos aleatorios
        ph = random.uniform(5.5, 7.5)
        temp = random.uniform(20.0, 35.0)
        hum = random.uniform(20.0, 80.0)

        # Crear mensajes
        messages = [
            {'topic': TOPIC_PH, 'payload': f"{ph:.2f}"},
            {'topic': TOPIC_TEMP, 'payload': f"{temp:.2f}"},
            {'topic': TOPIC_HUM, 'payload': f"{hum:.2f}"}
        ]

        # Publicar mensajes
        publish.multiple(messages, hostname=MQTT_BROKER, port=MQTT_PORT)
        
        # Mostrar en consola
        print(f"\n{datetime.now().strftime('%H:%M:%S')}:")
        print(f"pH: {ph:.2f}")
        print(f"Temperatura: {temp:.2f}°C")
        print(f"Humedad: {hum:.2f}%")
        
        # Esperar 5 segundos
        print("\nEsperando 5 segundos...")
        time.sleep(5)

except KeyboardInterrupt:
    print("\nSimulador detenido.")