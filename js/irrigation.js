// Control de Riego Automatizado
class IrrigationControl {
    constructor() {
        this.isActive = JSON.parse(localStorage.getItem('irrigation_active') || 'false');
        this.schedule = JSON.parse(localStorage.getItem('irrigation_schedule') || '{}');
        this.history = JSON.parse(localStorage.getItem('irrigation_history') || '[]');
    }

    // Activar/desactivar riego manual
    toggleIrrigation() {
        this.isActive = !this.isActive;
        this.logEvent('toggle', this.isActive ? 'Activado' : 'Desactivado');
        localStorage.setItem('irrigation_active', this.isActive);
        return this.isActive;
    }

    // Programar riego automático
    scheduleIrrigation(startTime, duration, daysOfWeek) {
        this.schedule = {
            startTime,
            duration, // minutos
            daysOfWeek, // ['mon', 'wed', 'fri']
            enabled: true
        };
        localStorage.setItem('irrigation_schedule', JSON.stringify(this.schedule));
    }

    // Riego inteligente basado en humedad
    autoIrrigation(humidity) {
        if (humidity < 35) {
            this.isActive = true;
            this.logEvent('auto', 'Activado automáticamente - Humedad crítica');
            return { action: 'START', duration: 60 };
        } else if (humidity > 65) {
            this.isActive = false;
            this.logEvent('auto', 'Detenido automáticamente - Humedad suficiente');
            return { action: 'STOP' };
        }
        return { action: 'MAINTAIN' };
    }

    // Registro de evento
    logEvent(type, description) {
        this.history.push({
            timestamp: new Date().toISOString(),
            type,
            description,
            status: this.isActive
        });
        localStorage.setItem('irrigation_history', JSON.stringify(this.history));
    }

    // Estadísticas
    getStatistics(days = 7) {
        const cutoff = new Date(Date.now() - days * 24 * 60 * 60 * 1000);
        const recent = this.history.filter(h => new Date(h.timestamp) > cutoff);
        
        return {
            activations: recent.filter(h => h.type === 'toggle' && h.status).length,
            totalMinutes: recent.reduce((sum, h) => sum + (h.duration || 0), 0),
            averagePerDay: recent.length / days
        };
    }

    getLastActivation() {
        return this.history.length > 0 ? this.history[this.history.length - 1] : null;
    }
}

const irrigationControl = new IrrigationControl();
