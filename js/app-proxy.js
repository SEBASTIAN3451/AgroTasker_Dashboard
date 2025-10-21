// Aplicación principal con conexión a través del proxy
let charts = {};
let updateInterval;

// Inicializar la aplicación
document.addEventListener('DOMContentLoaded', function() {
    console.log('Inicializando dashboard...');
    initCharts();
    fetchAllData();
    updateInterval = setInterval(fetchAllData, 20000); // Actualizar cada 20 segundos
});

// Inicializar todas las gráficas
function initCharts() {
    const chartConfig = {
        type: 'line',
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: false
                }
            },
            plugins: {
                legend: {
                    display: false
                }
            }
        }
    };

    // Gráficas de suelo
    const soilCharts = ['humedad-suelo', 'temp-suelo', 'ph-suelo', 'conductividad'];
    soilCharts.forEach(id => {
        const canvas = document.getElementById(`chart-${id}`);
        if (canvas) {
            charts[id] = new Chart(canvas, {
                ...chartConfig,
                data: {
                    labels: [],
                    datasets: [{
                        label: id.replace('-', ' ').toUpperCase(),
                        data: [],
                        borderColor: '#00A3FF',
                        backgroundColor: 'rgba(0, 163, 255, 0.1)',
                        tension: 0.4
                    }]
                }
            });
        }
    });

    // Gráficas de clima
    const weatherCharts = ['temp-aire', 'humedad-aire', 'precipitacion'];
    weatherCharts.forEach(id => {
        const canvas = document.getElementById(`chart-${id}`);
        if (canvas) {
            charts[id] = new Chart(canvas, {
                ...chartConfig,
                data: {
                    labels: [],
                    datasets: [{
                        label: id.replace('-', ' ').toUpperCase(),
                        data: [],
                        borderColor: '#00A3FF',
                        backgroundColor: 'rgba(0, 163, 255, 0.1)',
                        tension: 0.4
                    }]
                }
            });
        }
    });

    // Gráficas de potencial mátrico y UV
    const matricCharts = ['resistencia-30cm', 'resistencia-60cm', 'uv-index'];
    matricCharts.forEach(id => {
        const canvas = document.getElementById(`chart-${id}`);
        if (canvas) {
            charts[id] = new Chart(canvas, {
                ...chartConfig,
                data: {
                    labels: [],
                    datasets: [{
                        label: id.replace('-', ' ').toUpperCase(),
                        data: [],
                        borderColor: '#00A3FF',
                        backgroundColor: 'rgba(0, 163, 255, 0.1)',
                        tension: 0.4
                    }]
                }
            });
        }
    });
}

// Obtener datos de todos los canales
async function fetchAllData() {
    console.log('Obteniendo datos de ThingSpeak...');
    updateStatus('Actualizando...', 'warning');

    try {
        // Obtener datos de los tres canales en paralelo
        const [soilData, weatherData, matricData] = await Promise.all([
            fetch('/api/thingspeak/soil').then(r => r.json()),
            fetch('/api/thingspeak/weather').then(r => r.json()),
            fetch('/api/thingspeak/matric_uv').then(r => r.json())
        ]);

        console.log('Datos recibidos:', { soilData, weatherData, matricData });

        // Procesar datos de suelo
        if (soilData.feeds && soilData.feeds.length > 0) {
            processSoilData(soilData);
        }

        // Procesar datos de clima
        if (weatherData.feeds && weatherData.feeds.length > 0) {
            processWeatherData(weatherData);
        }

        // Procesar datos de potencial mátrico y UV
        if (matricData.feeds && matricData.feeds.length > 0) {
            processMatricData(matricData);
        }

        // Actualizar tiempo
        const now = new Date();
        document.getElementById('last-update').textContent = 
            `Última actualización: ${now.toLocaleTimeString('es-MX')}`;
        
        updateStatus('Conectado', 'success');
    } catch (error) {
        console.error('Error al obtener datos:', error);
        updateStatus('Error de conexión', 'error');
    }
}

// Procesar datos de suelo (Canal 2791076)
function processSoilData(data) {
    const feeds = data.feeds.slice(-10); // Últimos 10 datos
    
    // Field1: Humedad del Suelo
    updateSensor('humedad-suelo', feeds.map(f => parseFloat(f.field1)), feeds.map(f => f.created_at), '%');
    
    // Field2: Temperatura del Suelo
    updateSensor('temp-suelo', feeds.map(f => parseFloat(f.field2)), feeds.map(f => f.created_at), '°C');
    
    // Field3: pH
    updateSensor('ph-suelo', feeds.map(f => parseFloat(f.field3)), feeds.map(f => f.created_at), '');
    
    // Field4: Conductividad
    updateSensor('conductividad', feeds.map(f => parseFloat(f.field4)), feeds.map(f => f.created_at), 'µS/cm');
    
    // Field5: Nitrógeno (solo valor)
    const lastN = feeds[feeds.length - 1].field5;
    updateValueOnly('nitrogeno', lastN, 'mg/kg');
    
    // Field6: Fósforo (solo valor)
    const lastP = feeds[feeds.length - 1].field6;
    updateValueOnly('fosforo', lastP, 'mg/kg');
    
    // Field7: Potasio (solo valor)
    const lastK = feeds[feeds.length - 1].field7;
    updateValueOnly('potasio', lastK, 'mg/kg');
}

// Procesar datos de clima (Canal 2791069)
function processWeatherData(data) {
    const feeds = data.feeds.slice(-10);
    
    // Field1: Dirección del Viento (solo valor)
    const lastWindDir = feeds[feeds.length - 1].field1;
    updateValueOnly('viento-direccion', lastWindDir, '°');
    
    // Field2: Velocidad del Viento (solo valor)
    const lastWindSpeed = feeds[feeds.length - 1].field2;
    updateValueOnly('viento-velocidad', lastWindSpeed, 'km/h');
    
    // Field3: Precipitación
    updateSensor('precipitacion', feeds.map(f => parseFloat(f.field3)), feeds.map(f => f.created_at), 'mm');
    
    // Field4: Temperatura del Aire
    updateSensor('temp-aire', feeds.map(f => parseFloat(f.field4)), feeds.map(f => f.created_at), '°C');
    
    // Field5: Humedad del Aire
    updateSensor('humedad-aire', feeds.map(f => parseFloat(f.field5)), feeds.map(f => f.created_at), '%');
    
    // Field6: Presión Atmosférica (solo valor)
    const lastPressure = feeds[feeds.length - 1].field6;
    updateValueOnly('presion', lastPressure, 'hPa');
}

// Procesar datos de potencial mátrico y UV (Canal 2906294)
function processMatricData(data) {
    const feeds = data.feeds.slice(-10);
    
    // Field1: Resistencia a 30cm
    updateSensor('resistencia-30cm', feeds.map(f => parseFloat(f.field1)), feeds.map(f => f.created_at), 'kΩ');
    
    // Field2: Resistencia a 60cm
    updateSensor('resistencia-60cm', feeds.map(f => parseFloat(f.field2)), feeds.map(f => f.created_at), 'kΩ');
    
    // Field3: Índice UV
    updateSensor('uv-index', feeds.map(f => parseFloat(f.field3)), feeds.map(f => f.created_at), '');
}

// Actualizar sensor con gráfica
function updateSensor(sensorId, values, timestamps, unit) {
    // Filtrar valores válidos
    const validData = values.map((v, i) => ({ value: v, time: timestamps[i] }))
                           .filter(d => !isNaN(d.value));
    
    if (validData.length === 0) return;
    
    // Actualizar valor actual
    const lastValue = validData[validData.length - 1].value;
    const valueElement = document.getElementById(`value-${sensorId}`);
    if (valueElement) {
        valueElement.textContent = lastValue.toFixed(2) + ' ' + unit;
    }
    
    // Actualizar gráfica
    if (charts[sensorId]) {
        const labels = validData.map(d => new Date(d.time).toLocaleTimeString('es-MX', { 
            hour: '2-digit', 
            minute: '2-digit' 
        }));
        
        charts[sensorId].data.labels = labels;
        charts[sensorId].data.datasets[0].data = validData.map(d => d.value);
        charts[sensorId].update('none'); // Sin animación para mejor rendimiento
    }
}

// Actualizar sensor sin gráfica (solo valor)
function updateValueOnly(sensorId, value, unit) {
    const valueElement = document.getElementById(`value-${sensorId}`);
    if (valueElement && value !== null && value !== undefined) {
        const numValue = parseFloat(value);
        if (!isNaN(numValue)) {
            valueElement.textContent = numValue.toFixed(2) + ' ' + unit;
        }
    }
}

// Actualizar estado de conexión
function updateStatus(message, status) {
    const statusElement = document.getElementById('connection-status');
    if (statusElement) {
        statusElement.textContent = message;
        statusElement.className = `status-indicator status-${status}`;
    }
}
