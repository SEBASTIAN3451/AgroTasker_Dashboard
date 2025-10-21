class IrrigationControl {
    constructor() {
        this.isIrrigating = false;
        this.schedules = [];
        this.loadSchedules();
        this.initializeControls();
    }

    initializeControls() {
        // Eventos para botones de control manual
        document.getElementById('irrigation-toggle').addEventListener('click', () => {
            this.toggleIrrigation();
        });

        // Eventos para programación
        document.getElementById('add-schedule').addEventListener('click', () => {
            this.addNewSchedule();
        });

        this.updateControlPanel();
    }

    toggleIrrigation() {
        this.isIrrigating = !this.isIrrigating;
        
        // Publicar estado en MQTT
        mqttClient.publish('agrotasker/control/riego', 
            this.isIrrigating ? 'ON' : 'OFF');

        // Actualizar UI
        this.updateControlPanel();

        // Notificar
        notificationSystem.notify(
            this.isIrrigating ? 'Riego Activado' : 'Riego Desactivado',
            {
                body: this.isIrrigating 
                    ? 'Sistema de riego iniciado manualmente'
                    : 'Sistema de riego detenido manualmente',
                type: this.isIrrigating ? 'success' : 'info'
            }
        );
    }

    addNewSchedule() {
        const time = document.getElementById('schedule-time').value;
        const duration = document.getElementById('schedule-duration').value;
        const days = Array.from(document.querySelectorAll('.schedule-day:checked'))
            .map(checkbox => checkbox.value);

        if (!time || !duration || days.length === 0) {
            notificationSystem.notify('Error de Programación', {
                body: 'Por favor complete todos los campos',
                type: 'error'
            });
            return;
        }

        const schedule = {
            id: Date.now(),
            time,
            duration: parseInt(duration),
            days,
            active: true
        };

        this.schedules.push(schedule);
        this.saveSchedules();
        this.updateSchedulePanel();
    }

    removeSchedule(id) {
        this.schedules = this.schedules.filter(s => s.id !== id);
        this.saveSchedules();
        this.updateSchedulePanel();
    }

    toggleSchedule(id) {
        const schedule = this.schedules.find(s => s.id === id);
        if (schedule) {
            schedule.active = !schedule.active;
            this.saveSchedules();
            this.updateSchedulePanel();
        }
    }

    saveSchedules() {
        localStorage.setItem('irrigation-schedules', JSON.stringify(this.schedules));
    }

    loadSchedules() {
        const saved = localStorage.getItem('irrigation-schedules');
        this.schedules = saved ? JSON.parse(saved) : [];
    }

    updateControlPanel() {
        const toggleButton = document.getElementById('irrigation-toggle');
        toggleButton.className = `button ${this.isIrrigating ? 'active' : ''}`;
        toggleButton.innerHTML = `
            <span class="material-icons">
                ${this.isIrrigating ? 'water_drop' : 'water_off'}
            </span>
            ${this.isIrrigating ? 'Detener Riego' : 'Iniciar Riego'}
        `;

        this.updateSchedulePanel();
    }

    updateSchedulePanel() {
        const container = document.getElementById('schedules-container');
        if (!container) return;

        container.innerHTML = this.schedules
            .map(schedule => `
                <div class="schedule-item ${schedule.active ? 'active' : ''}">
                    <div class="schedule-header">
                        <span class="material-icons">schedule</span>
                        <span class="schedule-time">${schedule.time}</span>
                        <button class="schedule-toggle" onclick="irrigationControl.toggleSchedule(${schedule.id})">
                            <span class="material-icons">
                                ${schedule.active ? 'toggle_on' : 'toggle_off'}
                            </span>
                        </button>
                        <button class="schedule-delete" onclick="irrigationControl.removeSchedule(${schedule.id})">
                            <span class="material-icons">delete</span>
                        </button>
                    </div>
                    <div class="schedule-details">
                        <span>Duración: ${schedule.duration} minutos</span>
                        <span>Días: ${this.formatDays(schedule.days)}</span>
                    </div>
                </div>
            `)
            .join('');
    }

    formatDays(days) {
        const dayNames = {
            'mon': 'Lun',
            'tue': 'Mar',
            'wed': 'Mié',
            'thu': 'Jue',
            'fri': 'Vie',
            'sat': 'Sáb',
            'sun': 'Dom'
        };
        return days.map(day => dayNames[day]).join(', ');
    }

    checkSchedules() {
        const now = new Date();
        const currentTime = now.toLocaleTimeString('es', { hour: '2-digit', minute: '2-digit' });
        const currentDay = now.toLocaleDateString('en', { weekday: 'short' }).toLowerCase();

        this.schedules.forEach(schedule => {
            if (schedule.active && 
                schedule.time === currentTime && 
                schedule.days.includes(currentDay) &&
                !this.isIrrigating) {
                
                this.startScheduledIrrigation(schedule);
            }
        });
    }

    startScheduledIrrigation(schedule) {
        this.isIrrigating = true;
        this.updateControlPanel();

        notificationSystem.notify('Riego Programado Iniciado', {
            body: `Riego iniciado por programación. Duración: ${schedule.duration} minutos`,
            type: 'success'
        });

        mqttClient.publish('agrotasker/control/riego', 'ON');

        // Programar el apagado
        setTimeout(() => {
            this.isIrrigating = false;
            this.updateControlPanel();
            mqttClient.publish('agrotasker/control/riego', 'OFF');

            notificationSystem.notify('Riego Programado Finalizado', {
                body: `Riego completado según programación`,
                type: 'success'
            });
        }, schedule.duration * 60 * 1000);
    }
}

// Inicializar el control de riego
const irrigationControl = new IrrigationControl();

// Verificar programaciones cada minuto
setInterval(() => irrigationControl.checkSchedules(), 60000);