class HistoryChart {
    constructor() {
        this.chart = new Chart(document.getElementById('history-chart'), {
            type: 'line',
            data: {
                labels: [],
                datasets: [
                    {
                        label: 'pH',
                        data: [],
                        borderColor: '#2E7D32',
                        tension: 0.4,
                        fill: false
                    },
                    {
                        label: 'Temperatura (°C)',
                        data: [],
                        borderColor: '#FF5722',
                        tension: 0.4,
                        fill: false
                    },
                    {
                        label: 'Humedad (%)',
                        data: [],
                        borderColor: '#1976D2',
                        tension: 0.4,
                        fill: false
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    intersect: false,
                    mode: 'index'
                },
                plugins: {
                    title: {
                        display: true,
                        text: 'Historial de Sensores'
                    },
                    legend: {
                        position: 'top'
                    }
                },
                scales: {
                    x: {
                        display: true,
                        title: {
                            display: true,
                            text: 'Tiempo'
                        }
                    },
                    y: {
                        display: true,
                        title: {
                            display: true,
                            text: 'Valor'
                        }
                    }
                }
            }
        });

        this.maxDataPoints = 50; // Número máximo de puntos en la gráfica
    }

    addData(sensorData) {
        const now = new Date().toLocaleTimeString();

        // Agregar nueva etiqueta de tiempo
        this.chart.data.labels.push(now);
        
        // Agregar datos para cada sensor
        this.chart.data.datasets.forEach((dataset, index) => {
            let value = null;
            switch(index) {
                case 0: value = sensorData.ph; break;
                case 1: value = sensorData.temperatura; break;
                case 2: value = sensorData.humedad; break;
            }
            dataset.data.push(value);
        });

        // Mantener solo los últimos maxDataPoints puntos
        if (this.chart.data.labels.length > this.maxDataPoints) {
            this.chart.data.labels.shift();
            this.chart.data.datasets.forEach(dataset => dataset.data.shift());
        }

        this.chart.update();
    }
}

const historyChart = new HistoryChart();