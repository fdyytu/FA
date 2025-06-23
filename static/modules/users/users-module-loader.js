// Users Module Loader
// Loader untuk semua modul users

class UsersModuleLoader {
    constructor() {
        this.modulesLoaded = false;
        this.basePath = '/static/modules/users';
    }

    // Load all users modules
    async loadAllModules() {
        if (this.modulesLoaded) {
            return Promise.resolve();
        }

        const modules = [
            `${this.basePath}/api/users-api-service.js`,
            `${this.basePath}/ui/users-ui-components.js`,
            `${this.basePath}/users-main-controller.js`
        ];

        try {
            await this.loadScripts(modules);
            this.modulesLoaded = true;
            console.log('Users modules loaded successfully');
            
            // Initialize users dashboard after modules are loaded
            if (typeof usersMainController !== 'undefined') {
                usersMainController.initUsersDashboard();
            }
        } catch (error) {
            console.error('Error loading users modules:', error);
            showToast('Gagal memuat modul users', 'error');
        }
    }

    // Load scripts dynamically
    loadScripts(scripts) {
        return Promise.all(scripts.map(src => this.loadScript(src)));
    }

    // Load single script
    loadScript(src) {
        return new Promise((resolve, reject) => {
            const script = document.createElement('script');
            script.src = src;
            script.onload = resolve;
            script.onerror = reject;
            document.head.appendChild(script);
        });
    }

    // Check if modules are loaded
    isLoaded() {
        return this.modulesLoaded;
    }
}

// Export instance and auto-load
window.usersModuleLoader = new UsersModuleLoader();

// Auto-load modules when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    usersModuleLoader.loadAllModules();
});
