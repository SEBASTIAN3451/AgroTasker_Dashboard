class ChartManager {
    constructor() {
        this.charts = {};
        this.chartConfigs = {
            soilMoisture: {
                elementId: 'soilMoistureChart',
                valueId: 'soilMoistureValue',
                title: 'Humedad del Suelo',
                unit: '%',
                color: '#2196F3'
            },
            temperature: {
                elementId: 'temperatureChart',
                valueId: 'temperatureValue',
                title: 'Temperatura',
                unit: '°C',
                color: '#F44336'
            },
            conductivity: {
                elementId: 'conductivityChart',
                valueId: 'conductivityValue',
                title: 'Conductividad Eléctrica',
                unit: 'mS/cm',
                color: '#4CAF50'
            },
            pH: {
                elementId: 'phChart',
                valueId: 'phValue',
                title: 'pH del Suelo',
                unit: '',
                color: '#FFC107'
            }
        };
    }

    initializeCharts() {
        for (const [key, config] of Object.entries(this.chartConfigs)) {
            const ctx = document.getElementById(config.elementId)?.getContext('2d');
            if (!ctx) continue;

            this.charts[key] = new Chart(ctx, {
                type: 'line',
                data: {
                    datasets: [{
                        label: config.title,
                        data: [],
                        borderColor: config.color,
                        backgroundColor: `${config.color}20`,
                        borderWidth: 2,
                        fill: true,
                        tension: 0.4
                    }]
                },
                options: this.getChartOptions(config)
            });
        }
    }

    getChartOptions(config) {
        return {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                    backgroundColor: 'rgba(255, 255, 255, 0.9)',
                    titleColor: '#000',
                    bodyColor: '#000',
                    borderColor: config.color,
                    borderWidth: 1,
                    callbacks: {
                        label: (context) => {
                            const value = context.parsed.y;
                            return `${value.toFixed(1)}${config.unit}`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    type: 'time',
                    time: {
                        unit: 'minute',
                        displayFormats: {
                            minute: 'HH:mm'
                        }
                    },
                    ticks: {
                        source: 'auto',
                        maxRotation: 0
                    },
                    grid: {
                        display: false
                    }
                },
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(0, 0, 0, 0.1)'
                    }
                }
            },
            interaction: {
                intersect: false,
                mode: 'index'
            },
            animation: {
                duration: 750,
                easing: 'easeInOutQuart'
            }
        };
    }

    updateCharts(data) {
        for (const [key, chartData] of Object.entries(data)) {
            if (this.charts[key]) {
                const chart = this.charts[key];
                const config = this.chartConfigs[key];

                // Actualizar gráfica
                chart.data.datasets[0].data = chartData.map(item => ({
                    x: item.timestamp,
                    y: item.value
                }));
                chart.update('none');

                // Actualizar valor actual
                const valueElement = document.getElementById(config.valueId);
                if (valueElement && chartData.length > 0) {
                    const lastValue = chartData[chartData.length - 1].value;
                    valueElement.textContent = `${lastValue.toFixed(1)}${config.unit}`;
                }
            }
        }
    }
}

export const chartManager = new ChartManager();