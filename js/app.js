import { authService } from './auth.js';
import { mqttClient } from './mqtt-client.js';
import { notifications } from './notifications.js';
import { predictionService } from './predictions.js';
import { chartManager } from './charts.js';
import { irrigationController } from './irrigation-control.js';
import { thingSpeakService } from './thingspeak-service.js';

class App {
    constructor() {
        this.init();
    }

    async init() {
        // Esperar a que la autenticación esté lista
        document.addEventListener('authReady', async () => {
            await this.initializeServices();
            this.setupEventListeners();
            this.startDataRefresh();
        });

        // Manejar errores de conexión
        document.addEventListener('mqttError', (e) => {
            notifications.create({
                type: 'error',
                title: 'Error de Conexión',
                message: 'Se perdió la conexión con el servidor. Intentando reconectar...'
            });
        });

        // Manejar reconexión fallida
        document.addEventListener('mqttReconnectFailed', () => {
            notifications.create({
                type: 'error',
                title: 'Error de Reconexión',
                message: 'No se pudo restablecer la conexión. Por favor, recarga la página.'
            });
        });
    }

    async initializeServices() {
        try {
            // Conectar al broker MQTT
            await mqttClient.connect();

            // Inicializar servicios
            chartManager.initializeCharts();
            irrigationController.initialize();

            // Cargar configuración inicial
            await this.loadSettings();

            // Mostrar notificación de inicio exitoso
            notifications.create({
                type: 'success',
                title: 'Sistema Iniciado',
                message: 'AgroTasker está listo y monitoreando.'
            });
        } catch (error) {
            console.error('Error al inicializar servicios:', error);
            notifications.create({
                type: 'error',
                title: 'Error de Inicialización',
                message: 'Ocurrió un error al iniciar el sistema.'
            });
        }
    }

    setupEventListeners() {
        // Manejar cambios de tema
        const themeToggle = document.getElementById('themeToggle');
        themeToggle.addEventListener('click', () => {
            document.body.dataset.theme = 
                document.body.dataset.theme === 'dark' ? 'light' : 'dark';
            localStorage.setItem('theme', document.body.dataset.theme);
        });

        // Manejar cambios en el rango de tiempo de gráficos
        const chartTimeRange = document.getElementById('chartTimeRange');
        chartTimeRange.addEventListener('change', (e) => {
            chartManager.updateTimeRange(e.target.value);
        });

        // Manejar envío del formulario de configuración
        const settingsForm = document.getElementById('settingsForm');
        settingsForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            await this.saveSettings();
        });

        // Escuchar nuevos datos
        document.addEventListener('newData', (e) => {
            this.handleNewData(e.detail);
        });
    }

    async loadSettings() {
        try {
            const response = await fetch('/api/settings', {
                headers: authService.getAuthHeader()
            });
            
            if (!response.ok) {
                throw new Error('Error al cargar configuración');
            }

            const settings = await response.json();
            this.applySettings(settings);
        } catch (error) {
            console.error('Error al cargar configuración:', error);
        }
    }

    applySettings(settings) {
        // Aplicar umbrales
        document.getElementById('maxTemp').value = settings.thresholds.maxTemp;
        document.getElementById('minTemp').value = settings.thresholds.minTemp;
        document.getElementById('minHumidity').value = settings.thresholds.minHumidity;
        document.getElementById('minSoilMoisture').value = settings.thresholds.minSoilMoisture;

        // Aplicar configuración de notificaciones
        document.getElementById('emailNotifications').checked = settings.notifications.email;
        document.getElementById('pushNotifications').checked = settings.notifications.push;

        // Aplicar tema
        const savedTheme = localStorage.getItem('theme') || 'light';
        document.body.dataset.theme = savedTheme;
    }

    async saveSettings() {
        const settings = {
            thresholds: {
                maxTemp: parseFloat(document.getElementById('maxTemp').value),
                minTemp: parseFloat(document.getElementById('minTemp').value),
                minHumidity: parseFloat(document.getElementById('minHumidity').value),
                minSoilMoisture: parseFloat(document.getElementById('minSoilMoisture').value)
            },
            notifications: {
                email: document.getElementById('emailNotifications').checked,
                push: document.getElementById('pushNotifications').checked
            }
        };

        try {
            const response = await fetch('/api/settings', {
                method: 'POST',
                headers: {
                    ...authService.getAuthHeader(),
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(settings)
            });

            if (!response.ok) {
                throw new Error('Error al guardar configuración');
            }

            notifications.create({
                type: 'success',
                title: 'Configuración Guardada',
                message: 'Los cambios se han aplicado correctamente.'
            });
        } catch (error) {
            console.error('Error al guardar configuración:', error);
            notifications.create({
                type: 'error',
                title: 'Error',
                message: 'No se pudo guardar la configuración.'
            });
        }
    }

    handleNewData(data) {
        // Actualizar última actualización
        const lastUpdate = document.getElementById('lastUpdate');
        lastUpdate.textContent = new Date().toLocaleTimeString();

        // Actualizar gráficos
        chartManager.updateCharts(data);

        // Verificar predicciones si es necesario
        predictionService.addDataPoint(data);
    }

    startDataRefresh() {
        // Actualizar predicciones cada hora
        setInterval(() => {
            predictionService.updatePredictions();
        }, 3600000);

        // Actualizar hora de última actualización
        setInterval(() => {
            const elements = document.querySelectorAll('time');
            elements.forEach(element => {
                const timestamp = element.getAttribute('datetime');
                if (timestamp) {
                    element.textContent = this.formatTimestamp(timestamp);
                }
            });
        }, 60000);
    }

    formatTimestamp(timestamp) {
        const date = new Date(timestamp);
        const now = new Date();
        const diffMinutes = Math.floor((now - date) / 60000);

        if (diffMinutes < 1) {
            return 'Hace un momento';
        } else if (diffMinutes < 60) {
            return `Hace ${diffMinutes} minutos`;
        } else if (diffMinutes < 1440) {
            const hours = Math.floor(diffMinutes / 60);
            return `Hace ${hours} horas`;
        } else {
            return date.toLocaleDateString();
        }
    }
}

// Inicializar la aplicación
const app = new App();