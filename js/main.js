// Estado actual de los sensores
const sensorState = {
    ph: null,
    temperatura: null,
    humedad: null
};

// Elementos DOM
const elements = {
    connectionIndicator: document.getElementById('connection-indicator'),
    connectionText: document.getElementById('connection-text'),
    phValue: document.getElementById('ph-value'),
    tempValue: document.getElementById('temp-value'),
    humidityValue: document.getElementById('humidity-value'),
    alertsContainer: document.getElementById('alerts-container')
};

// Función para actualizar la interfaz
function updateUI() {
    // Actualizar valores
    elements.phValue.textContent = sensorState.ph?.toFixed(2) || '--';
    elements.tempValue.textContent = sensorState.temperatura?.toFixed(1) || '--';
    elements.humidityValue.textContent = sensorState.humedad?.toFixed(1) || '--';

    // Actualizar medidores
    if (sensorState.ph !== null) gauges.ph.update(sensorState.ph);
    if (sensorState.temperatura !== null) gauges.temperatura.update(sensorState.temperatura);
    if (sensorState.humedad !== null) gauges.humedad.update(sensorState.humedad);

    // Actualizar gráfica si tenemos todos los valores
    if (sensorState.ph !== null && sensorState.temperatura !== null && sensorState.humedad !== null) {
        historyChart.addData(sensorState);
    }

    // Generar alertas si es necesario
    checkAlerts();
}

// Función para mostrar alertas
function showAlert(message, type = 'warning') {
    const alertElement = document.createElement('div');
    alertElement.className = `alert-item ${type}`;
    alertElement.textContent = message;
    
    elements.alertsContainer.insertBefore(alertElement, elements.alertsContainer.firstChild);

    // Eliminar la alerta después de 10 segundos
    setTimeout(() => {
        alertElement.remove();
    }, 10000);
}

// Función para verificar alertas
function checkAlerts() {
    if (sensorState.humedad !== null) {
        if (sensorState.humedad < 30) {
            showAlert('¡Alerta! Humedad del suelo baja. Se recomienda riego.', 'error');
        } else if (sensorState.humedad > 80) {
            showAlert('¡Precaución! Humedad del suelo muy alta.', 'warning');
        }
    }

    if (sensorState.ph !== null) {
        if (sensorState.ph < 5.5 || sensorState.ph > 7.5) {
            showAlert(`¡Atención! pH fuera del rango óptimo: ${sensorState.ph}`, 'warning');
        }
    }

    if (sensorState.temperatura !== null) {
        if (sensorState.temperatura > 35) {
            showAlert('¡Alerta! Temperatura muy alta. Considere medidas de protección.', 'error');
        } else if (sensorState.temperatura < 20) {
            showAlert('¡Atención! Temperatura baja para el cultivo.', 'warning');
        }
    }
}

// Inicializar cliente MQTT
const mqttClient = new MQTTClient();

// Manejar eventos de conexión MQTT
mqttClient.onConnect(() => {
    elements.connectionIndicator.classList.add('connected');
    elements.connectionText.textContent = 'Conectado';
    showAlert('Conexión establecida con el servidor', 'success');
});

mqttClient.onDisconnect(() => {
    elements.connectionIndicator.classList.remove('connected');
    elements.connectionText.textContent = 'Desconectado';
    showAlert('Conexión perdida con el servidor', 'error');
});

mqttClient.onMessage((topic, value) => {
    // Actualizar estado según el topic
    switch(topic) {
        case MQTT_CONFIG.topics.ph:
            sensorState.ph = value;
            break;
        case MQTT_CONFIG.topics.temperatura:
            sensorState.temperatura = value;
            break;
        case MQTT_CONFIG.topics.humedad:
            sensorState.humedad = value;
            break;
    }

    // Actualizar la interfaz
    updateUI();
});

// Conectar al broker MQTT
mqttClient.connect();