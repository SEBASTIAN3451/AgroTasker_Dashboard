class ThingSpeakService {
    constructor() {
        this.channelId = '2791076';
        this.baseUrl = '/api/thingspeak';
        this.updateInterval = 30000; // 30 segundos
    }

    async fetchData() {
        try {
            const response = await fetch(`${this.baseUrl}/soil?results=1000`);
            if (!response.ok) {
                throw new Error('Error al obtener datos desde Dropbox');
            }
            const data = await response.json();
            return this.processData(data);
        } catch (error) {
            console.error('Error fetching Dropbox-derived data:', error);
            throw error;
        }
    }

    processData(data) {
        const feeds = data.feeds;
        return {
            soilMoisture: this.extractFieldData(feeds, 'field1'),
            soilTemperature: this.extractFieldData(feeds, 'field2'),
            electricalConductivity: this.extractFieldData(feeds, 'field3'),
            soilPH: this.extractFieldData(feeds, 'field4'),
            nitrogen: this.extractFieldData(feeds, 'field5'),
            phosphorus: this.extractFieldData(feeds, 'field6'),
            potassium: this.extractFieldData(feeds, 'field7'),
            lastUpdate: feeds[feeds.length - 1]?.created_at
        };
    }

    extractFieldData(feeds, fieldName) {
        return feeds.map(feed => ({
            value: parseFloat(feed[fieldName]) || 0,
            timestamp: new Date(feed.created_at)
        })).filter(item => !isNaN(item.value));
    }

    startAutoUpdate(callback) {
        // Obtener datos inmediatamente
        this.fetchData().then(callback).catch(console.error);

        // Configurar actualización automática
        this.updateInterval = setInterval(() => {
            this.fetchData().then(callback).catch(console.error);
        }, this.updateInterval);
    }

    stopAutoUpdate() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
        }
    }
}

export const thingSpeakService = new ThingSpeakService();