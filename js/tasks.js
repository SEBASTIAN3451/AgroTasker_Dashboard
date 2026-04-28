// Gestión de Tareas Agrícolas
class AgriculturalTasks {
    constructor() {
        this.tasks = JSON.parse(localStorage.getItem('agrotasker_tasks') || '[]');
    }

    addTask(name, date, type, priority = 'normal') {
        const task = {
            id: Date.now(),
            name,
            date,
            type, // 'riego', 'fertilizacion', 'poda', 'fumigacion', 'cosecha'
            priority,
            completed: false,
            createdAt: new Date().toISOString()
        };
        this.tasks.push(task);
        this.save();
        return task;
    }

    completeTask(id) {
        const task = this.tasks.find(t => t.id === id);
        if (task) {
            task.completed = true;
            this.save();
        }
    }

    deleteTask(id) {
        this.tasks = this.tasks.filter(t => t.id !== id);
        this.save();
    }

    getUpcoming(days = 7) {
        const now = new Date();
        const future = new Date(now.getTime() + days * 24 * 60 * 60 * 1000);
        return this.tasks.filter(t => {
            const taskDate = new Date(t.date);
            return taskDate >= now && taskDate <= future && !t.completed;
        }).sort((a, b) => new Date(a.date) - new Date(b.date));
    }

    save() {
        localStorage.setItem('agrotasker_tasks', JSON.stringify(this.tasks));
    }

    getByType(type) {
        return this.tasks.filter(t => t.type === type && !t.completed);
    }

    getStatistics() {
        return {
            total: this.tasks.length,
            completed: this.tasks.filter(t => t.completed).length,
            pending: this.tasks.filter(t => !t.completed).length,
            byType: {
                riego: this.getByType('riego').length,
                fertilizacion: this.getByType('fertilizacion').length,
                poda: this.getByType('poda').length,
                fumigacion: this.getByType('fumigacion').length,
                cosecha: this.getByType('cosecha').length
            }
        };
    }
}

// Instancia global
const taskManager = new AgriculturalTasks();
