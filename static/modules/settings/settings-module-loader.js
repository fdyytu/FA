// Settings Module Loader
// Maksimal 50 baris per file

class SettingsModuleLoader {
    constructor() {
        this.modulesLoaded = false;
        this.basePath = '/static/modules/settings';
    }

    // Load all settings modules
    async loadModules() {
        if (this.modulesLoaded) return;

        const modules = [
            // API Services
            `${this.basePath}/api/settings-api-service.js`,
            `${this.basePath}/api/settings-operations-api.js`,
            
            // UI Components
            `${this.basePath}/ui/settings-form-ui.js`,
            
            // Components
            `${this.basePath}/components/settings-tabs.js`,
            
            // Handlers
            `${this.basePath}/handlers/settings-data-handler.js`,
            
            // Utils
            `${this.basePath}/utils/settings-export-utils.js`,
            
            // Main Controller
            `${this.basePath}/settings-main-controller.js`
        ];

        try {
            await this.loadScripts(modules);
            this.modulesLoaded = true;
            console.log('Settings modules loaded successfully');
        } catch (error) {
            console.error('Error loading settings modules:', error);
            throw error;
        }
    }

    // Load scripts sequentially
    async loadScripts(scripts) {
        for (const script of scripts) {
            await this.loadScript(script);
        }
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
}

// Export instance and auto-load
window.settingsModuleLoader = new SettingsModuleLoader();
