class PredictionSystem {
    constructor() {
        this.historicalData = {
            ph: [],
            temperatura: [],
            humedad: []
        };
        this.predictions = {
            ph: [],
            temperatura: [],
            humedad: []
        };
        this.chart = null;
        this.initChart();
    }

    initChart() {
        const ctx = document.getElementById('prediction-chart').getContext('2d');
        this.chart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [
                    {
                        label: 'Temperatura Real',
                        data: [],
                        borderColor: '#FF5722',
                        fill: false
                    },
                    {
                        label: 'Temperatura Predicha',
                        data: [],
                        borderColor: '#FF5722',
                        borderDash: [5, 5],
                        fill: false
                    },
                    {
                        label: 'Humedad Real',
                        data: [],
                        borderColor: '#2196F3',
                        fill: false
                    },
                    {
                        label: 'Humedad Predicha',
                        data: [],
                        borderColor: '#2196F3',
                        borderDash: [5, 5],
                        fill: false
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
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
    }

    addData(type, value) {
        this.historicalData[type].push({
            value,
            timestamp: new Date()
        });

        // Mantener solo las últimas 24 horas de datos
        const oneDayAgo = new Date(Date.now() - 24 * 60 * 60 * 1000);
        this.historicalData[type] = this.historicalData[type].filter(
            data => data.timestamp > oneDayAgo
        );

        this.updatePredictions();
    }

    updatePredictions() {
        // Calcular predicciones simples usando regresión lineal
        for (const type in this.historicalData) {
            const data = this.historicalData[type];
            if (data.length < 2) continue;

            // Preparar datos para la regresión
            const x = data.map((d, i) => i);
            const y = data.map(d => d.value);

            // Calcular regresión lineal
            const {slope, intercept} = this.linearRegression(x, y);

            // Generar predicciones para las próximas 6 horas
            this.predictions[type] = [];
            for (let i = 0; i < 12; i++) {
                const predictedValue = slope * (x.length + i) + intercept;
                this.predictions[type].push(predictedValue);
            }
        }

        this.updateChart();
        this.generateRecommendations();
    }

    linearRegression(x, y) {
        const n = x.length;
        let sumX = 0;
        let sumY = 0;
        let sumXY = 0;
        let sumXX = 0;

        for (let i = 0; i < n; i++) {
            sumX += x[i];
            sumY += y[i];
            sumXY += x[i] * y[i];
            sumXX += x[i] * x[i];
        }

        const slope = (n * sumXY - sumX * sumY) / (n * sumXX - sumX * sumX);
        const intercept = (sumY - slope * sumX) / n;

        return {slope, intercept};
    }

    updateChart() {
        // Actualizar datos reales
        this.chart.data.labels = this.generateTimeLabels();
        this.chart.data.datasets[0].data = this.historicalData.temperatura.map(d => d.value);
        this.chart.data.datasets[2].data = this.historicalData.humedad.map(d => d.value);

        // Agregar predicciones
        const nullPadding = new Array(this.historicalData.temperatura.length).fill(null);
        this.chart.data.datasets[1].data = [...nullPadding, ...this.predictions.temperatura];
        this.chart.data.datasets[3].data = [...nullPadding, ...this.predictions.humedad];

        this.chart.update();
    }

    generateTimeLabels() {
        const labels = [];
        const now = new Date();
        
        // Etiquetas para datos históricos
        for (let i = 0; i < this.historicalData.temperatura.length; i++) {
            labels.push(this.formatTime(this.historicalData.temperatura[i].timestamp));
        }

        // Etiquetas para predicciones
        for (let i = 0; i < 12; i++) {
            const futureTime = new Date(now.getTime() + i * 30 * 60 * 1000);
            labels.push(this.formatTime(futureTime));
        }

        return labels;
    }

    formatTime(date) {
        return new Intl.DateTimeFormat('es', {
            hour: '2-digit',
            minute: '2-digit'
        }).format(date);
    }

    generateRecommendations() {
        const latestTemp = this.historicalData.temperatura[this.historicalData.temperatura.length - 1]?.value;
        const latestHumidity = this.historicalData.humedad[this.historicalData.humedad.length - 1]?.value;
        const predictedTemp = this.predictions.temperatura[0];
        const predictedHumidity = this.predictions.humedad[0];

        // Generar recomendaciones basadas en tendencias
        if (predictedHumidity < 30 && latestHumidity < 35) {
            notificationSystem.notify('Alerta de Riego', {
                body: 'Se prevé baja humedad. Se recomienda programar riego en las próximas horas.',
                type: 'warning'
            });
        }

        if (predictedTemp > 32 && latestTemp > 30) {
            notificationSystem.notify('Alerta de Temperatura', {
                body: 'Se espera temperatura alta. Considere medidas de protección para el cultivo.',
                type: 'warning'
            });
        }

        // Actualizar panel de recomendaciones
        this.updateRecommendationPanel(predictedTemp, predictedHumidity);
    }

    updateRecommendationPanel(predictedTemp, predictedHumidity) {
        const container = document.getElementById('recommendations-container');
        if (!container) return;

        let recommendations = [];

        if (predictedTemp > 32) {
            recommendations.push({
                icon: 'thermostat',
                title: 'Temperatura Alta Prevista',
                text: 'Considere implementar medidas de sombreo o riego por aspersión.'
            });
        }

        if (predictedHumidity < 30) {
            recommendations.push({
                icon: 'water_drop',
                title: 'Riego Recomendado',
                text: 'Programe un riego en las próximas 3-6 horas.'
            });
        }

        container.innerHTML = recommendations
            .map(rec => `
                <div class="recommendation-item">
                    <span class="material-icons">${rec.icon}</span>
                    <div class="recommendation-content">
                        <h4>${rec.title}</h4>
                        <p>${rec.text}</p>
                    </div>
                </div>
            `)
            .join('');
    }
}

// Inicializar el sistema de predicciones
const predictionSystem = new PredictionSystem();