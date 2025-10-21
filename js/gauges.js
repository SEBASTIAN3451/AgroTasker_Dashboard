class SensorGauge {
    constructor(canvasId, options = {}) {
        this.canvas = document.getElementById(canvasId);
        this.options = {
            min: options.min || 0,
            max: options.max || 100,
            warningThreshold: options.warningThreshold || 70,
            criticalThreshold: options.criticalThreshold || 90,
            ...options
        };

        this.gauge = new Chart(this.canvas, {
            type: 'doughnut',
            data: {
                datasets: [{
                    data: [0, 100],
                    backgroundColor: [
                        this.options.color || '#2E7D32',
                        '#ECEFF1'
                    ],
                    borderWidth: 0
                }]
            },
            options: {
                circumference: 180,
                rotation: 270,
                cutout: '70%',
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        enabled: false
                    }
                }
            }
        });
    }

    update(value) {
        const normalizedValue = Math.min(Math.max(value, this.options.min), this.options.max);
        const percentage = ((normalizedValue - this.options.min) / (this.options.max - this.options.min)) * 100;

        // Actualizar color basado en umbrales
        let color = this.options.color || '#2E7D32';
        if (percentage >= this.options.criticalThreshold) {
            color = '#D32F2F';
        } else if (percentage >= this.options.warningThreshold) {
            color = '#FFA000';
        }

        this.gauge.data.datasets[0].data = [percentage, 100 - percentage];
        this.gauge.data.datasets[0].backgroundColor[0] = color;
        this.gauge.update();
    }
}

// Crear instancias de los medidores
const gauges = {
    ph: new SensorGauge('ph-gauge', {
        min: 0,
        max: 14,
        warningThreshold: 30,
        criticalThreshold: 70,
        color: '#2E7D32'
    }),

    temperatura: new SensorGauge('temp-gauge', {
        min: 0,
        max: 50,
        warningThreshold: 60,
        criticalThreshold: 80,
        color: '#FF5722'
    }),

    humedad: new SensorGauge('humidity-gauge', {
        min: 0,
        max: 100,
        warningThreshold: 70,
        criticalThreshold: 90,
        color: '#1976D2'
    })
};