import paho.mqtt.publish as publish
import time
import random
from datetime import datetime

# Configuración MQTT
MQTT_BROKER = "test.mosquitto.org"
MQTT_PORT = 1883
MQTT_TOPICS = {
    'ph': 'agrotasker/test/sensor/ph',
    'temperatura': 'agrotasker/test/sensor/temperatura',
    'humedad': 'agrotasker/test/sensor/humedad'
}

# Configuración de los rangos de los sensores
SENSOR_RANGES = {
    'ph': {'min': 5.5, 'max': 7.5, 'variation': 0.1},
    'temperatura': {'min': 20, 'max': 35, 'variation': 0.5},
    'humedad': {'min': 20, 'max': 80, 'variation': 2.0}
}

class SensorSimulator:
    def __init__(self):
        # Inicializar valores de sensores
        self.values = {
            'ph': 6.5,
            'temperatura': 25.0,
            'humedad': 50.0
        }

    def update_sensor_value(self, sensor):
        # Obtener el valor actual y los límites
        current = self.values[sensor]
        ranges = SENSOR_RANGES[sensor]
        
        # Generar una variación aleatoria
        variation = random.uniform(-ranges['variation'], ranges['variation'])
        new_value = current + variation
        
        # Mantener el valor dentro de los límites
        new_value = max(ranges['min'], min(ranges['max'], new_value))
        
        self.values[sensor] = new_value
        return new_value

    def start_simulation(self):
        print("=== Simulador de Sensores AgroTasker ===")
        print("Presiona Ctrl+C para detener")
        print("---------------------------------------")
        print("\nRangos de simulación:")
        for sensor, range_data in SENSOR_RANGES.items():
            print(f"{sensor}: {range_data['min']} a {range_data['max']}")
        
        try:
            while True:
                # Actualizar y publicar valores de sensores
                messages = []
                for sensor, topic in MQTT_TOPICS.items():
                    value = self.update_sensor_value(sensor)
                    messages.append({'topic': topic, 'payload': f"{value:.2f}"})
                    print(f"{datetime.now().strftime('%H:%M:%S')} - {sensor}: {value:.2f}")
                
                # Publicar todos los mensajes
                publish.multiple(messages, hostname=MQTT_BROKER, port=MQTT_PORT)
                
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