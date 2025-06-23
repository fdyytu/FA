// Products Module Loader
// Maksimal 50 baris per file

class ProductsModuleLoader {
    constructor() {
        this.modulesLoaded = false;
        this.basePath = '/static/modules/products';
    }

    // Load all product modules
    async loadModules() {
        if (this.modulesLoaded) return;

        const modules = [
            // API Services
            `${this.basePath}/api/products-api-service.js`,
            `${this.basePath}/api/products-operations-api.js`,
            
            // UI Components
            `${this.basePath}/ui/products-table-ui.js`,
            `${this.basePath}/ui/products-stats-ui.js`,
            
            // Components
            `${this.basePath}/components/products-pagination.js`,
            
            // Handlers
            `${this.basePath}/handlers/products-data-handler.js`,
            
            // Utils
            `${this.basePath}/utils/products-export-utils.js`,
            
            // Main Controller
            `${this.basePath}/products-main-controller.js`
        ];

        try {
            await this.loadScripts(modules);
            this.modulesLoaded = true;
            console.log('Products modules loaded successfully');
        } catch (error) {
            console.error('Error loading products modules:', error);
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
window.productsModuleLoader = new ProductsModuleLoader();
