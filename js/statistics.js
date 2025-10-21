class Statistics {
    constructor() {
        this.data = {
            ph: [],
            temperatura: [],
            humedad: []
        };
        this.maxDataPoints = 288; // 24 horas con datos cada 5 minutos
    }

    addData(type, value) {
        this.data[type].push({
            value: value,
            timestamp: new Date()
        });

        // Mantener solo las últimas 24 horas de datos
        if (this.data[type].length > this.maxDataPoints) {
            this.data[type].shift();
        }

        this.updateStatistics();
    }

    calculateAverage(data) {
        if (data.length === 0) return 0;
        const sum = data.reduce((acc, item) => acc + item.value, 0);
        return sum / data.length;
    }

    calculateMax(data) {
        if (data.length === 0) return 0;
        return Math.max(...data.map(item => item.value));
    }

    calculateMin(data) {
        if (data.length === 0) return 0;
        return Math.min(...data.map(item => item.value));
    }

    updateStatistics() {
        // Actualizar promedios
        document.getElementById('ph-avg').textContent = 
            this.calculateAverage(this.data.ph).toFixed(2);
        
        document.getElementById('temp-max').textContent = 
            this.calculateMax(this.data.temperatura).toFixed(1) + '°C';
        
        document.getElementById('humidity-avg').textContent = 
            this.calculateAverage(this.data.humedad).toFixed(1) + '%';
    }

    exportData() {
        const csv = ['Timestamp,pH,Temperatura,Humedad'];
        
        // Encontrar el tiempo más antiguo común
        const startTime = Math.max(
            ...Object.values(this.data).map(arr => 
                arr.length > 0 ? arr[0].timestamp.getTime() : 0
            )
        );

        // Crear filas de datos
        Object.values(this.data)[0].forEach((_, index) => {
            const row = [
                new Date(startTime + index * 5 * 60000).toISOString(),
                this.data.ph[index]?.value.toFixed(2) || '',
                this.data.temperatura[index]?.value.toFixed(1) || '',
                this.data.humedad[index]?.value.toFixed(1) || ''
            ];
            csv.push(row.join(','));
        });

        // Crear y descargar el archivo
        const blob = new Blob([csv.join('\n')], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.setAttribute('hidden', '');
        a.setAttribute('href', url);
        a.setAttribute('download', 'agrotasker_datos.csv');
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
    }
}

// Inicializar las estadísticas
const statistics = new Statistics();

// Configurar el botón de exportación
document.getElementById('export-data').addEventListener('click', () => {
    statistics.exportData();
});