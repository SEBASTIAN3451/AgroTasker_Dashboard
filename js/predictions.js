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
        const canvas = document.getElementById('prediction-chart');
        if (!canvas) {
            // El dashboard puede ocultar/separar este widget.
            this.chart = null;
            return;
        }

        const ctx = canvas.getContext('2d');
        if (!ctx) {
            this.chart = null;
            return;
        }

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
        if (!this.chart) return;

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

    predictHarvest(floweringDate) {
        const start = new Date(floweringDate);
        if (Number.isNaN(start.getTime())) {
            return {
                estimatedHarvestDate: 'Fecha no válida',
                daysRemaining: null,
                harvestMonth: 'Desconocido',
                progress: 0
            };
        }

        const harvestDate = new Date(start.getTime() + 210 * 24 * 60 * 60 * 1000);
        const totalDays = 210;
        const elapsedDays = Math.max(0, Math.floor((Date.now() - start.getTime()) / (24 * 60 * 60 * 1000)));
        const daysRemaining = Math.max(0, Math.ceil((harvestDate.getTime() - Date.now()) / (24 * 60 * 60 * 1000)));
        const progress = Math.max(0, Math.min(100, Math.round((elapsedDays / totalDays) * 100)));

        return {
            estimatedHarvestDate: harvestDate.toLocaleDateString('es-MX'),
            daysRemaining,
            harvestMonth: harvestDate.toLocaleDateString('es-MX', { month: 'long' }),
            progress
        };
    }

    predictWaterNeeds(humidity, temperature) {
        const hum = Number(humidity);
        const temp = Number(temperature);
        const safeHumidity = Number.isFinite(hum) ? hum : 0;
        const safeTemp = Number.isFinite(temp) ? temp : 0;

        let priority = 'Baja';
        let recommendedLiters = 15;
        let frequency = 'Cada 3-4 días';
        let bestTime = '06:00-08:00';
        let notes = 'Monitoreo estable.';

        if (safeHumidity < 35 || safeTemp > 32) {
            priority = 'Alta';
            recommendedLiters = 45;
            frequency = 'Diaria';
            bestTime = '05:30-07:30';
            notes = 'Riego prioritario por déficit hídrico y/o temperatura alta.';
        } else if (safeHumidity < 50 || safeTemp > 29) {
            priority = 'Media';
            recommendedLiters = 28;
            frequency = 'Cada 2 días';
            bestTime = '06:00-08:00';
            notes = 'Ajuste preventivo para sostener humedad útil.';
        } else if (safeHumidity > 72) {
            priority = 'Baja';
            recommendedLiters = 8;
            frequency = 'Suspender temporalmente';
            bestTime = 'No aplica';
            notes = 'El suelo conserva suficiente humedad; evitar sobre-riego.';
        }

        return {
            priority,
            recommendedLiters,
            frequency,
            bestTime,
            notes
        };
    }

    predictDiseases(humidity, temperature) {
        const hum = Number(humidity);
        const temp = Number(temperature);
        const safeHumidity = Number.isFinite(hum) ? hum : 0;
        const safeTemp = Number.isFinite(temp) ? temp : 0;

        const diseases = [];

        if (safeHumidity >= 72 && safeTemp >= 25 && safeTemp <= 30) {
            diseases.push({
                name: 'Antracnosis',
                riskLevel: 'Alto',
                confidence: 84,
                recommendation: 'Reducir humedad foliar, mejorar ventilación y vigilar síntomas iniciales.'
            });
        }

        if (safeHumidity >= 60 && safeTemp >= 24 && safeTemp <= 31) {
            diseases.push({
                name: 'Oídio',
                riskLevel: 'Medio',
                confidence: 68,
                recommendation: 'Mantener circulación de aire y aplicar control preventivo si aumenta la humedad.'
            });
        }

        if (safeTemp >= 33) {
            diseases.push({
                name: 'Estrés por Calor',
                riskLevel: 'Alto',
                confidence: 90,
                recommendation: 'Activar riego de apoyo, sombreo temporal y evitar labores en horas de mayor radiación.'
            });
        }

        if (diseases.length === 0) {
            diseases.push({
                name: 'Riesgo Fitosanitario Bajo',
                riskLevel: 'Bajo',
                confidence: 76,
                recommendation: 'Condiciones estables; continúe con monitoreo rutinario.'
            });
        }

        return diseases;
    }

    predictNutrientNeeds(nitrogen, phosphorus, potassium) {
        const n = Number(nitrogen);
        const p = Number(phosphorus);
        const k = Number(potassium);

        const needs = [];

        if (Number.isFinite(n) && n < 220) {
            needs.push({ nutrient: 'N', status: 'Bajo', recommendation: 'Aplicar fertilización nitrogenada de refuerzo.' });
        }
        if (Number.isFinite(p) && p < 45) {
            needs.push({ nutrient: 'P', status: 'Bajo', recommendation: 'Corregir fósforo para apoyar enraizamiento y floración.' });
        }
        if (Number.isFinite(k) && k < 190) {
            needs.push({ nutrient: 'K', status: 'Bajo', recommendation: 'Subir potasio para mejorar llenado de fruto y tolerancia al estrés.' });
        }

        if (needs.length === 0) {
            needs.push({ nutrient: 'NPK', status: 'Adecuado', recommendation: 'Los nutrientes principales están en rango operativo.' });
        }

        return needs;
    }

    generateRecommendations() {
        const latestTemp = this.historicalData.temperatura[this.historicalData.temperatura.length - 1]?.value;
        const latestHumidity = this.historicalData.humedad[this.historicalData.humedad.length - 1]?.value;
        const predictedTemp = this.predictions.temperatura[0];
        const predictedHumidity = this.predictions.humedad[0];

        // Generar recomendaciones basadas en tendencias
        if (typeof notificationSystem !== 'undefined' && predictedHumidity < 30 && latestHumidity < 35) {
            notificationSystem.notify('Alerta de Riego', {
                body: 'Se prevé baja humedad. Se recomienda programar riego en las próximas horas.',
                type: 'warning'
            });
        }

        if (typeof notificationSystem !== 'undefined' && predictedTemp > 32 && latestTemp > 30) {
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
window.predictionSystem = new PredictionSystem();
var predictionSystem = window.predictionSystem;