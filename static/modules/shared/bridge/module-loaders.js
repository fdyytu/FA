// Module Loaders - Sistem loading untuk berbagai modul dashboard
class ModuleLoaders {
    constructor(bridgeCore) {
        this.bridgeCore = bridgeCore;
    }

    async loadSharedModules() {
        const sharedModules = [
            'api-client',
            'formatters', 
            'ui-utils'
        ];

        console.log('Loading shared modules:', sharedModules);
        
        for (const module of sharedModules) {
            try {
                await window.loadModule(module);
                this.bridgeCore.loadedModules.add(module);
            } catch (error) {
                console.warn(`Failed to load shared module ${module}:`, error);
            }
        }
    }

    async loadMainModules() {
        const mainModules = [
            'main-data-service',
            'main-ui-controller', 
            'main-controller'
        ];

        console.log('Loading main modules:', mainModules);
        
        for (const module of mainModules) {
            try {
                await window.loadModule(module);
                this.bridgeCore.loadedModules.add(module);
            } catch (error) {
                console.warn(`Failed to load main module ${module}:`, error);
            }
        }
    }

    async loadDiscordModules() {
        if (this.bridgeCore.loadedModules.has('discord-main')) return;
        
        console.log('Loading Discord modules...');
        
        try {
            await window.loadModuleGroup('discord');
            this.bridgeCore.loadedModules.add('discord-main');
            
            // Initialize Discord module instance
            if (window.DiscordMainController) {
                this.bridgeCore.moduleInstances.discord = new window.DiscordMainController();
            }
            
        } catch (error) {
            console.warn('Failed to load Discord modules:', error);
        }
    }

    async loadAnalyticsModules() {
        if (this.bridgeCore.loadedModules.has('analytics-main')) return;
        
        console.log('Loading Analytics modules...');
        
        try {
            await window.loadModuleGroup('analytics');
            this.bridgeCore.loadedModules.add('analytics-main');
            
            // Initialize Analytics module instance
            if (window.AnalyticsMainController) {
                this.bridgeCore.moduleInstances.analytics = new window.AnalyticsMainController();
            }
            
        } catch (error) {
            console.warn('Failed to load Analytics modules:', error);
        }
    }
}

// Export untuk penggunaan global
window.ModuleLoaders = ModuleLoaders;
