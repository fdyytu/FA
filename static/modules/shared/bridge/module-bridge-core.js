// Module Bridge Core - Inti sistem bridge untuk modul dashboard
class ModuleBridgeCore {
    constructor() {
        this.loadedModules = new Set();
        this.moduleInstances = {};
        this.isInitialized = false;
    }

    async initializeModules() {
        if (this.isInitialized) return;
        
        console.log('🔄 Initializing Dashboard Module Bridge...');
        
        try {
            // Load shared utilities first
            await this.loadSharedModules();
            
            // Load main dashboard modules
            await this.loadMainModules();
            
            // Initialize module instances
            this.initializeModuleInstances();
            
            this.isInitialized = true;
            console.log('✅ Dashboard Module Bridge initialized successfully');
            
        } catch (error) {
            console.error('❌ Failed to initialize Dashboard Module Bridge:', error);
            throw error;
        }
    }

    initializeModuleInstances() {
        // Initialize main controller if available
        if (window.MainController && !this.moduleInstances.main) {
            this.moduleInstances.main = new window.MainController();
        }
    }

    getModuleInstance(moduleName) {
        return this.moduleInstances[moduleName];
    }

    isModuleLoaded(moduleName) {
        return this.loadedModules.has(moduleName);
    }

    getLoadedModules() {
        return Array.from(this.loadedModules);
    }

    getPerformanceMetrics() {
        if (window.getModuleMetrics) {
            return window.getModuleMetrics();
        }
        return null;
    }
}

// Export untuk penggunaan global
window.ModuleBridgeCore = ModuleBridgeCore;
