// Analytics Module Loader
// Loader untuk semua modul analytics

class AnalyticsModuleLoader {
    constructor() {
        this.modulesLoaded = false;
        this.basePath = '/static/modules/analytics';
    }

    // Load all analytics modules
    async loadAllModules() {
        if (this.modulesLoaded) {
            return Promise.resolve();
        }

        const modules = [
            `${this.basePath}/api/analytics-api-service.js`,
            `${this.basePath}/ui/analytics-ui-components.js`,
            `${this.basePath}/components/analytics-chart-manager.js`,
            `${this.basePath}/analytics-main-controller.js`
        ];

        try {
            await this.loadScripts(modules);
            this.modulesLoaded = true;
            console.log('Analytics modules loaded successfully');
            
            // Initialize analytics dashboard after modules are loaded
            if (typeof analyticsMainController !== 'undefined') {
                analyticsMainController.initAnalyticsDashboard();
            }
        } catch (error) {
            console.error('Error loading analytics modules:', error);
            showToast('Gagal memuat modul analytics', 'error');
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
window.analyticsModuleLoader = new AnalyticsModuleLoader();

// Auto-load modules when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    analyticsModuleLoader.loadAllModules();
});
