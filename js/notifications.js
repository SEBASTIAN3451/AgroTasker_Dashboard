class NotificationSystem {
    constructor() {
        this.permission = false;
        this.notifications = [];
        this.checkPermission();
    }

    async checkPermission() {
        if (!("Notification" in window)) {
            console.log("Este navegador no soporta notificaciones");
            return;
        }

        if (Notification.permission === "granted") {
            this.permission = true;
        } else if (Notification.permission !== "denied") {
            const permission = await Notification.requestPermission();
            this.permission = permission === "granted";
        }
    }

    async notify(title, options = {}) {
        if (!this.permission) {
            await this.checkPermission();
        }

        if (this.permission) {
            const notification = new Notification(title, {
                icon: '/dashboard/img/logo.png',
                badge: '/dashboard/img/badge.png',
                ...options
            });

            // Guardar notificación en el historial
            this.notifications.unshift({
                title,
                message: options.body || '',
                timestamp: new Date(),
                type: options.type || 'info'
            });

            // Mantener solo las últimas 50 notificaciones
            if (this.notifications.length > 50) {
                this.notifications.pop();
            }

            // Actualizar panel de notificaciones
            this.updateNotificationPanel();
        }
    }

    updateNotificationPanel() {
        const container = document.getElementById('notifications-container');
        if (!container) return;

        container.innerHTML = this.notifications
            .map(notification => `
                <div class="notification-item ${notification.type}">
                    <div class="notification-header">
                        <span class="material-icons">${this.getIconForType(notification.type)}</span>
                        <span class="notification-title">${notification.title}</span>
                        <span class="notification-time">${this.formatTime(notification.timestamp)}</span>
                    </div>
                    <div class="notification-body">${notification.message}</div>
                </div>
            `)
            .join('');
    }

    getIconForType(type) {
        switch (type) {
            case 'error': return 'error';
            case 'warning': return 'warning';
            case 'success': return 'check_circle';
            default: return 'info';
        }
    }

    formatTime(date) {
        return new Intl.DateTimeFormat('es', {
            hour: '2-digit',
            minute: '2-digit'
        }).format(date);
    }
}

// Inicializar el sistema de notificaciones
const notificationSystem = new NotificationSystem();