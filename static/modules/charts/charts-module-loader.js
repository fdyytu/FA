// Charts Module Loader
// Maksimal 50 baris per file

class ChartsModuleLoader {
    static async loadModule() {
        const basePath = '/static/modules/charts';
        
        const modules = [
            `${basePath}/utils/charts-config.js`,
            `${basePath}/api/charts-api-service.js`,
            `${basePath}/components/transaction-chart.js`,
            `${basePath}/components/category-chart.js`,
            `${basePath}/charts-main-controller.js`
        ];

        try {
            // Load all modules sequentially
            for (const module of modules) {
                await this.loadScript(module);
            }
            
            console.log('Charts modules loaded successfully');
            return true;
        } catch (error) {
            console.error('Error loading charts modules:', error);
            return false;
        }
    }

    static loadScript(src) {
        return new Promise((resolve, reject) => {
            const script = document.createElement('script');
            script.src = src;
            script.onload = resolve;
            script.onerror = reject;
            document.head.appendChild(script);
        });
    }
}

// Auto-load if not in test environment
if (typeof window !== 'undefined' && !window.isTestEnvironment) {
    ChartsModuleLoader.loadModule().then(() => {
        console.log('Charts module ready');
    }).catch(error => {
        console.error('Failed to load charts module:', error);
    });
}
