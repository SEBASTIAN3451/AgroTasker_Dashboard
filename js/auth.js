// Configuración inicial
const AUTH_TOKEN_KEY = 'agrotasker_auth_token';
const API_URL = 'https://api.agrotasker.com';

class AuthService {
    constructor() {
        this.token = localStorage.getItem(AUTH_TOKEN_KEY);
        this.user = null;
        this.init();
    }

    init() {
        if (this.token) {
            this.validateToken();
        } else {
            this.showLoginModal();
        }
    }

    async login(username, password) {
        try {
            const response = await fetch(`${API_URL}/auth/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ username, password })
            });

            if (!response.ok) {
                throw new Error('Credenciales inválidas');
            }

            const data = await response.json();
            this.token = data.token;
            this.user = data.user;
            
            localStorage.setItem(AUTH_TOKEN_KEY, this.token);
            
            this.hideLoginModal();
            this.initializeApp();
        } catch (error) {
            console.error('Error de autenticación:', error);
            this.showError(error.message);
        }
    }

    async validateToken() {
        try {
            const response = await fetch(`${API_URL}/auth/validate`, {
                headers: {
                    'Authorization': `Bearer ${this.token}`
                }
            });

            if (!response.ok) {
                throw new Error('Token inválido');
            }

            const data = await response.json();
            this.user = data.user;
            this.initializeApp();
        } catch (error) {
            console.error('Error validando token:', error);
            this.logout();
        }
    }

    logout() {
        localStorage.removeItem(AUTH_TOKEN_KEY);
        this.token = null;
        this.user = null;
        this.showLoginModal();
    }

    showLoginModal() {
        const modal = document.getElementById('authModal');
        modal.style.display = 'flex';

        const form = document.getElementById('loginForm');
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            const username = form.querySelector('input[type="text"]').value;
            const password = form.querySelector('input[type="password"]').value;
            await this.login(username, password);
        });
    }

    hideLoginModal() {
        const modal = document.getElementById('authModal');
        modal.style.display = 'none';
    }

    showError(message) {
        // Implementar mostrar error en la UI
        alert(message);
    }

    initializeApp() {
        // Evento personalizado para notificar que la autenticación está lista
        const event = new CustomEvent('authReady', { detail: { user: this.user } });
        document.dispatchEvent(event);
    }

    getAuthHeader() {
        return {
            'Authorization': `Bearer ${this.token}`
        };
    }
}

// Inicializar el servicio de autenticación
const authService = new AuthService();

// Exportar para uso en otros módulos
export { authService };