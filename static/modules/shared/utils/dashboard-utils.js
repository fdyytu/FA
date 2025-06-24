// Dashboard Utils - Utility functions untuk dashboard
class DashboardUtils {
    constructor() {
        this.fab = new FloatingActionButton();
    }

    // Initialize all dashboard utilities
    init() {
        this.fab.init();
    }

    // Refresh all data
    async refreshAllData() {
        if (window.showLoading) {
            window.showLoading(true);
        }
        
        try {
            const promises = [];
            
            // Use bridge if available
            if (window.DashboardBridge) {
                promises.push(window.DashboardBridge.refreshDashboard());
                promises.push(window.DashboardBridge.loadDiscordStats());
            } else {
                // Fallback to direct functions
                if (window.refreshDashboard) {
                    promises.push(window.refreshDashboard());
                }
                if (window.loadDiscordStats) {
                    promises.push(window.loadDiscordStats());
                }
            }
            
            await Promise.all(promises);
            
            if (window.showToast) {
                window.showToast('Semua data berhasil diperbarui', 'success', 3000);
            }
        } catch (error) {
            console.error('Error refreshing data:', error);
            if (window.showToast) {
                window.showToast('Gagal memperbarui beberapa data', 'warning');
            }
        } finally {
            if (window.showLoading) {
                window.showLoading(false);
            }
        }
    }
}

// Export untuk penggunaan global
window.DashboardUtils = DashboardUtils;

// Auto-initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    const dashboardUtils = new DashboardUtils();
    dashboardUtils.init();
    window.dashboardUtils = dashboardUtils;
});
