// Configuración del cliente MQTT
const MQTT_CONFIG = {
    broker: 'ws://test.mosquitto.org:8080', // Broker público de prueba
    topics: {
        ph: 'agrotasker/test/sensor/ph',
        temperatura: 'agrotasker/test/sensor/temperatura',
        humedad: 'agrotasker/test/sensor/humedad'
    }
};

class MQTTClient {
    constructor() {
        this.client = null;
        this.isConnected = false;
        this.callbacks = {
            onConnect: [],
            onMessage: [],
            onDisconnect: []
        };
    }

    connect() {
        try {
            this.client = mqtt.connect(MQTT_CONFIG.broker);

            this.client.on('connect', () => {
                console.log('Conectado al broker MQTT');
                this.isConnected = true;
                this._subscribeToTopics();
                this.callbacks.onConnect.forEach(cb => cb());
            });

            this.client.on('message', (topic, message) => {
                const value = parseFloat(message.toString());
                if (!isNaN(value)) {
                    this.callbacks.onMessage.forEach(cb => cb(topic, value));
                }
            });

            this.client.on('offline', () => {
                console.log('Desconectado del broker MQTT');
                this.isConnected = false;
                this.callbacks.onDisconnect.forEach(cb => cb());
            });

            this.client.on('error', (error) => {
                console.error('Error MQTT:', error);
                this.isConnected = false;
                this.callbacks.onDisconnect.forEach(cb => cb());
            });
        } catch (error) {
            console.error('Error al conectar:', error);
        }
    }

    _subscribeToTopics() {
        Object.values(MQTT_CONFIG.topics).forEach(topic => {
            this.client.subscribe(topic, (err) => {
                if (err) {
                    console.error('Error al suscribirse a', topic, err);
                } else {
                    console.log('Suscrito a', topic);
                }
            });
        });
    }

    onConnect(callback) {
        this.callbacks.onConnect.push(callback);
    }

    onMessage(callback) {
        this.callbacks.onMessage.push(callback);
    }

    onDisconnect(callback) {
        this.callbacks.onDisconnect.push(callback);
    }
}