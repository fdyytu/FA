// Dashboard Bridge Main - File utama yang menggabungkan semua komponen bridge
class DashboardModuleBridge extends ModuleBridgeCore {
    constructor() {
        super();
        this.moduleLoaders = new ModuleLoaders(this);
        this.bridgeMethods = new BridgeMethods(this, this.moduleLoaders);
    }

    // Override method dari parent class untuk menggunakan moduleLoaders
    async loadSharedModules() {
        return await this.moduleLoaders.loadSharedModules();
    }

    async loadMainModules() {
        return await this.moduleLoaders.loadMainModules();
    }

    // Expose bridge methods
    async loadDashboardStats() {
        return await this.bridgeMethods.loadDashboardStats();
    }

    async loadDiscordStats() {
        return await this.bridgeMethods.loadDiscordStats();
    }

    async refreshDashboard() {
        return await this.bridgeMethods.refreshDashboard();
    }

    // Additional module loaders
    async loadDiscordModules() {
        return await this.moduleLoaders.loadDiscordModules();
    }

    async loadAnalyticsModules() {
        return await this.moduleLoaders.loadAnalyticsModules();
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
