// Main Dashboard Bridge Service
// Maksimal 50 baris per file

class MainBridgeService {
    static async loadDashboardStatsWithBridge() {
        try {
            if (window.DashboardBridge && window.DashboardBridge.isInitialized) {
                console.log('📊 Loading dashboard stats via module bridge...');
                await window.DashboardBridge.loadDashboardStats();
            } else {
                console.log('📊 Loading dashboard stats via fallback...');
                const stats = await MainAPIService.loadDashboardStats();
                MainUIService.updateStatsCards(stats);
            }
        } catch (error) {
            console.error('Error loading dashboard stats via bridge:', error);
            // Fallback to original implementation
            const stats = await MainAPIService.loadDashboardStats();
            MainUIService.updateStatsCards(stats);
        }
    }

    static async loadDiscordStatsWithBridge() {
        try {
            if (window.DashboardBridge && window.DashboardBridge.isInitialized) {
                console.log('🤖 Loading Discord stats via module bridge...');
                await window.DashboardBridge.loadDiscordStats();
            } else {
                console.log('🤖 Loading Discord stats via fallback...');
                if (window.loadDiscordStats) {
                    await window.loadDiscordStats();
                }
            }
        } catch (error) {
            console.error('Error loading Discord stats via bridge:', error);
            // Fallback to original implementation
            if (window.loadDiscordStats) {
                await window.loadDiscordStats();
            }
        }
    }

    static async refreshDashboardWithBridge() {
        NotificationService.showLoading(true);
        try {
            if (window.DashboardBridge && window.DashboardBridge.isInitialized) {
                console.log('🔄 Refreshing dashboard via module bridge...');
                await window.DashboardBridge.refreshDashboard();
            } else {
                console.log('🔄 Refreshing dashboard via fallback...');
                const { stats, transactions } = await MainAPIService.refreshDashboard();
                MainUIService.updateStatsCards(stats);
                MainUIService.renderRecentTransactions(transactions);
            }
            NotificationService.showToast('Dashboard berhasil diperbarui', 'success', 3000);
        } catch (error) {
            NotificationService.showToast('Gagal memperbarui dashboard', 'error');
        } finally {
            NotificationService.showLoading(false);
        }
    }
}

window.MainBridgeService = MainBridgeService;
