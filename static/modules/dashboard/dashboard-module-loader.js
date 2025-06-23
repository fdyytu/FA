// Dashboard Module Loader
class DashboardModuleLoader {
    constructor() {
        this.loadedModules = new Set();
        this.basePath = '/static/modules/dashboard';
    }

    async loadModule(moduleName) {
        if (this.loadedModules.has(moduleName)) {
            return Promise.resolve();
        }

        return new Promise((resolve, reject) => {
            const script = document.createElement('script');
            script.src = `${this.basePath}/${moduleName}`;
            script.onload = () => {
                this.loadedModules.add(moduleName);
                console.log(`Dashboard module loaded: ${moduleName}`);
                resolve();
            };
            script.onerror = () => {
                console.error(`Failed to load dashboard module: ${moduleName}`);
                reject(new Error(`Failed to load module: ${moduleName}`));
            };
            document.head.appendChild(script);
        });
    }

    async loadAllModules() {
        const modules = [
            'api/dashboard-api-service.js',
            'ui/dashboard-stats-ui.js',
            'components/dashboard-chart.js',
            'utils/dashboard-notifications.js',
            'utils/dashboard-auth.js',
            'dashboard-main-controller.js'
        ];

        try {
            for (const module of modules) {
                await this.loadModule(module);
            }
            console.log('All dashboard modules loaded successfully');
            return true;
        } catch (error) {
            console.error('Error loading dashboard modules:', error);
            return false;
        }
    }

    isModuleLoaded(moduleName) {
        return this.loadedModules.has(moduleName);
    }

    getLoadedModules() {
        return Array.from(this.loadedModules);
    }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', async function() {
    const loader = new DashboardModuleLoader();
    const success = await loader.loadAllModules();
    
    if (success) {
        // Initialize dashboard controller
        window.dashboardController = new DashboardMainController();
    } else {
        console.error('Failed to load dashboard modules');
    }
});

// Export untuk digunakan di modul lain
window.DashboardModuleLoader = DashboardModuleLoader;
