// Conectar a Socket.IO
const socket = io();

// Configuración de gráficos
const chartConfig = {
    ph: {
        ctx: document.getElementById('ph-chart').getContext('2d'),
        valueElement: document.getElementById('ph-value'),
        data: [],
        chart: null,
        min: 0,
        max: 14
    },
    temperatura: {
        ctx: document.getElementById('temp-chart').getContext('2d'),
        valueElement: document.getElementById('temp-value'),
        data: [],
        chart: null,
        min: 0,
        max: 50
    },
    humedad: {
        ctx: document.getElementById('humidity-chart').getContext('2d'),
        valueElement: document.getElementById('humidity-value'),
        data: [],
        chart: null,
        min: 0,
        max: 100
    }
};

// Crear gráficos
for (const sensor in chartConfig) {
    const config = chartConfig[sensor];
    config.chart = new Chart(config.ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: sensor.charAt(0).toUpperCase() + sensor.slice(1),
                data: config.data,
                borderColor: '#00A3FF',
                tension: 0.4,
                fill: false
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    min: config.min,
                    max: config.max
                }
            },
            plugins: {
                legend: {
                    display: false
                }
            }
        }
    });
}

// Recibir datos iniciales
socket.on('initial-data', (data) => {
    for (const sensor in data) {
        if (chartConfig[sensor]) {
            const values = data[sensor].map(d => d.value);
            const timestamps = data[sensor].map(d => new Date(d.timestamp).toLocaleTimeString());
            
            chartConfig[sensor].data = values;
            chartConfig[sensor].chart.data.labels = timestamps;
            chartConfig[sensor].chart.data.datasets[0].data = values;
            chartConfig[sensor].chart.update();
            
            if (values.length > 0) {
                updateCurrentValue(sensor, values[values.length - 1]);
            }
        }
    }
});

// Recibir actualizaciones en tiempo real
socket.on('sensor-update', (data) => {
    const config = chartConfig[data.sensor];
    if (config) {
        config.data.push(data.value);
        config.chart.data.labels.push(new Date().toLocaleTimeString());
        
        // Mantener solo los últimos 20 puntos
        if (config.data.length > 20) {
            config.data.shift();
            config.chart.data.labels.shift();
        }
        
        config.chart.data.datasets[0].data = config.data;
        config.chart.update();
        
        updateCurrentValue(data.sensor, data.value);
    }
});

function updateCurrentValue(sensor, value) {
    const element = chartConfig[sensor].valueElement;
    if (element) {
        let displayValue = value.toFixed(2);
        switch (sensor) {
            case 'temperatura':
                element.textContent = `${displayValue}°C`;
                break;
            case 'humedad':
                element.textContent = `${displayValue}%`;
                break;
            default:
                element.textContent = displayValue;
        }
    }
}