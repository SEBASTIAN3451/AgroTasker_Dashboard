class ThingSpeakService {
    constructor() {
        this.channelId = '2791075';
        this.baseUrl = 'https://api.thingspeak.com/channels';
        this.updateInterval = 30000; // 30 segundos
    }

    async fetchData() {
        try {
            const response = await fetch(`${this.baseUrl}/${this.channelId}/feeds.json?results=1000`);
            if (!response.ok) {
                throw new Error('Error al obtener datos de ThingSpeak');
            }
            const data = await response.json();
            return this.processData(data);
        } catch (error) {
            console.error('Error fetching ThingSpeak data:', error);
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