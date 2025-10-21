class IrrigationCalendar {
    constructor() {
        this.currentDate = new Date();
        this.selectedDate = new Date();
        this.irrigationDays = new Set();
        
        this.init();
    }

    init() {
        // Elementos del DOM
        this.prevButton = document.getElementById('prev-month');
        this.nextButton = document.getElementById('next-month');
        this.monthDisplay = document.getElementById('current-month');
        this.calendarGrid = document.getElementById('calendar-grid');

        // Eventos
        this.prevButton.addEventListener('click', () => this.previousMonth());
        this.nextButton.addEventListener('click', () => this.nextMonth());

        // Renderizar calendario inicial
        this.render();
    }

    render() {
        // Actualizar texto del mes
        const monthNames = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
                          'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'];
        this.monthDisplay.textContent = `${monthNames[this.currentDate.getMonth()]} ${this.currentDate.getFullYear()}`;

        // Limpiar grid
        this.calendarGrid.innerHTML = '';

        // Agregar días de la semana
        const weekDays = ['Dom', 'Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb'];
        weekDays.forEach(day => {
            const dayElement = document.createElement('div');
            dayElement.className = 'calendar-day weekday';
            dayElement.textContent = day;
            this.calendarGrid.appendChild(dayElement);
        });

        // Obtener primer día del mes
        const firstDay = new Date(this.currentDate.getFullYear(), this.currentDate.getMonth(), 1);
        const startingDay = firstDay.getDay();

        // Agregar días vacíos al inicio
        for (let i = 0; i < startingDay; i++) {
            const emptyDay = document.createElement('div');
            emptyDay.className = 'calendar-day empty';
            this.calendarGrid.appendChild(emptyDay);
        }

        // Agregar días del mes
        const daysInMonth = new Date(this.currentDate.getFullYear(), this.currentDate.getMonth() + 1, 0).getDate();
        
        for (let day = 1; day <= daysInMonth; day++) {
            const dayElement = document.createElement('div');
            dayElement.className = 'calendar-day';
            dayElement.textContent = day;

            // Verificar si es un día de riego
            const dateString = `${this.currentDate.getFullYear()}-${this.currentDate.getMonth() + 1}-${day}`;
            if (this.irrigationDays.has(dateString)) {
                dayElement.classList.add('irrigation-day');
                const icon = document.createElement('span');
                icon.className = 'material-icons';
                icon.textContent = 'water_drop';
                dayElement.appendChild(icon);
            }

            // Agregar evento click
            dayElement.addEventListener('click', () => this.toggleIrrigationDay(day));

            this.calendarGrid.appendChild(dayElement);
        }
    }

    previousMonth() {
        this.currentDate.setMonth(this.currentDate.getMonth() - 1);
        this.render();
    }

    nextMonth() {
        this.currentDate.setMonth(this.currentDate.getMonth() + 1);
        this.render();
    }

    toggleIrrigationDay(day) {
        const dateString = `${this.currentDate.getFullYear()}-${this.currentDate.getMonth() + 1}-${day}`;
        
        if (this.irrigationDays.has(dateString)) {
            this.irrigationDays.delete(dateString);
        } else {
            this.irrigationDays.add(dateString);
        }

        // Guardar en localStorage
        localStorage.setItem('irrigationDays', JSON.stringify(Array.from(this.irrigationDays)));

        // Re-renderizar el calendario
        this.render();
    }

    loadIrrigationDays() {
        const saved = localStorage.getItem('irrigationDays');
        if (saved) {
            this.irrigationDays = new Set(JSON.parse(saved));
            this.render();
        }
    }
}

// Inicializar el calendario
const calendar = new IrrigationCalendar();
calendar.loadIrrigationDays();