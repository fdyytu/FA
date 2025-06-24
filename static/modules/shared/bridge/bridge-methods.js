// Bridge Methods - Metode kompatibilitas untuk dashboard lama
class BridgeMethods {
    constructor(bridgeCore, moduleLoaders) {
        this.bridgeCore = bridgeCore;
        this.moduleLoaders = moduleLoaders;
    }

    // Bridge methods untuk kompatibilitas dengan kode lama
    async loadDashboardStats() {
        if (this.bridgeCore.moduleInstances.main && this.bridgeCore.moduleInstances.main.loadDashboardStats) {
            return await this.bridgeCore.moduleInstances.main.loadDashboardStats();
        }
        
        // Fallback ke implementasi lama
        if (window.loadDashboardStats) {
            return await window.loadDashboardStats();
        }
        
        console.warn('No dashboard stats loader available');
    }

    async loadDiscordStats() {
        // Load Discord modules if not loaded
        await this.moduleLoaders.loadDiscordModules();
        
        if (this.bridgeCore.moduleInstances.discord && this.bridgeCore.moduleInstances.discord.loadDiscordStats) {
            return await this.bridgeCore.moduleInstances.discord.loadDiscordStats();
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
            if (this.bridgeCore.moduleInstances.main && this.bridgeCore.moduleInstances.main.refreshDashboard) {
                promises.push(this.bridgeCore.moduleInstances.main.refreshDashboard());
            } else if (window.refreshDashboard) {
                promises.push(window.refreshDashboard());
            }
            
            // Refresh Discord if loaded
            if (this.bridgeCore.loadedModules.has('discord-main') && this.bridgeCore.moduleInstances.discord) {
                if (this.bridgeCore.moduleInstances.discord.loadDiscordStats) {
                    promises.push(this.bridgeCore.moduleInstances.discord.loadDiscordStats());
                }
            }
            
            await Promise.all(promises);
            console.log('✅ Dashboard refreshed successfully');
            
        } catch (error) {
            console.error('❌ Failed to refresh dashboard:', error);
            throw error;
        }
    }
}

// Export untuk penggunaan global
window.BridgeMethods = BridgeMethods;
