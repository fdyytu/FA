// Dashboard Module Bridge - Menghubungkan dashboard lama dengan sistem modul baru
class DashboardModuleBridge {
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
                this.loadedModules.add(module);
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
                this.loadedModules.add(module);
            } catch (error) {
                console.warn(`Failed to load main module ${module}:`, error);
            }
        }
    }

    async loadDiscordModules() {
        if (this.loadedModules.has('discord-main')) return;
        
        console.log('Loading Discord modules...');
        
        try {
            await window.loadModuleGroup('discord');
            this.loadedModules.add('discord-main');
            
            // Initialize Discord module instance
            if (window.DiscordMainController) {
                this.moduleInstances.discord = new window.DiscordMainController();
            }
            
        } catch (error) {
            console.warn('Failed to load Discord modules:', error);
        }
    }

    async loadAnalyticsModules() {
        if (this.loadedModules.has('analytics-main')) return;
        
        console.log('Loading Analytics modules...');
        
        try {
            await window.loadModuleGroup('analytics');
            this.loadedModules.add('analytics-main');
            
            // Initialize Analytics module instance
            if (window.AnalyticsMainController) {
                this.moduleInstances.analytics = new window.AnalyticsMainController();
            }
            
        } catch (error) {
            console.warn('Failed to load Analytics modules:', error);
        }
    }

    async loadProductsModules() {
        if (this.loadedModules.has('products-main')) return;
        
        console.log('Loading Products modules...');
        
        try {
            await window.loadModuleGroup('products');
            this.loadedModules.add('products-main');
            
            // Initialize Products module instance
            if (window.ProductsMainController) {
                this.moduleInstances.products = new window.ProductsMainController();
            }
            
        } catch (error) {
            console.warn('Failed to load Products modules:', error);
        }
    }

    async loadUsersModules() {
        if (this.loadedModules.has('users-main')) return;
        
        console.log('Loading Users modules...');
        
        try {
            await window.loadModuleGroup('users');
            this.loadedModules.add('users-main');
            
            // Initialize Users module instance
            if (window.UsersMainController) {
                this.moduleInstances.users = new window.UsersMainController();
            }
            
        } catch (error) {
            console.warn('Failed to load Users modules:', error);
        }
    }

    initializeModuleInstances() {
        // Initialize main controller if available
        if (window.MainController && !this.moduleInstances.main) {
            this.moduleInstances.main = new window.MainController();
        }
    }

    // Bridge methods untuk kompatibilitas dengan kode lama
    async loadDashboardStats() {
        if (this.moduleInstances.main && this.moduleInstances.main.loadDashboardStats) {
            return await this.moduleInstances.main.loadDashboardStats();
        }
        
        // Fallback ke implementasi lama
        if (window.loadDashboardStats) {
            return await window.loadDashboardStats();
        }
        
        console.warn('No dashboard stats loader available');
    }

    async loadDiscordStats() {
        // Load Discord modules if not loaded
        await this.loadDiscordModules();
        
        if (this.moduleInstances.discord && this.moduleInstances.discord.loadDiscordStats) {
            return await this.moduleInstances.discord.loadDiscordStats();
        }
        
        // Fallback ke implementasi lama
        if (window.loadDiscordStats) {
            return await window.loadDiscordStats();
        }
        
        console.warn('No Discord stats loader available');
    }

    async refreshDashboard() {
        console.log('🔄 Refreshing dashboard using module bridge...');
        
        try {
            const promises = [];
            
            // Refresh main dashboard
            if (this.moduleInstances.main && this.moduleInstances.main.refreshDashboard) {
                promises.push(this.moduleInstances.main.refreshDashboard());
            } else if (window.refreshDashboard) {
                promises.push(window.refreshDashboard());
            }
            
            // Refresh Discord if loaded
            if (this.loadedModules.has('discord-main') && this.moduleInstances.discord) {
                if (this.moduleInstances.discord.loadDiscordStats) {
                    promises.push(this.moduleInstances.discord.loadDiscordStats());
                }
            }
            
            await Promise.all(promises);
            console.log('✅ Dashboard refreshed successfully');
            
        } catch (error) {
            console.error('❌ Failed to refresh dashboard:', error);
            throw error;
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

// Global instance
const dashboardBridge = new DashboardModuleBridge();

// Export untuk penggunaan global
window.DashboardBridge = dashboardBridge;

// Auto-initialize when DOM is ready
document.addEventListener('DOMContentLoaded', async () => {
    try {
        await dashboardBridge.initializeModules();
    } catch (error) {
        console.error('Failed to initialize dashboard bridge:', error);
    }
});
