// Controlador del tema
class ThemeController {
    constructor() {
        this.themeToggle = document.getElementById('theme-toggle');
        this.themeIcon = this.themeToggle.querySelector('.material-icons');
        this.currentTheme = localStorage.getItem('theme') || 'light';
        
        this.init();
    }

    init() {
        // Aplicar tema guardado
        document.documentElement.setAttribute('data-theme', this.currentTheme);
        this.updateIcon();

        // Eventos
        this.themeToggle.addEventListener('click', () => this.toggleTheme());
    }

    toggleTheme() {
        this.currentTheme = this.currentTheme === 'light' ? 'dark' : 'light';
        document.documentElement.setAttribute('data-theme', this.currentTheme);
        localStorage.setItem('theme', this.currentTheme);
        this.updateIcon();

        // Animar el botón
        this.themeToggle.style.animation = 'none';
        this.themeToggle.offsetHeight; // Trigger reflow
        this.themeToggle.style.animation = 'pulse 0.3s ease-in-out';
    }

    updateIcon() {
        this.themeIcon.textContent = this.currentTheme === 'light' ? 'dark_mode' : 'light_mode';
    }
}

// Inicializar el controlador del tema
const themeController = new ThemeController();