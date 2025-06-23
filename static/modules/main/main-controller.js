// Main Dashboard Controller
// Maksimal 50 baris per file

class MainController {
    static async initDashboard() {
        const token = AuthService.checkAuth();
        if (!token) return;

        NotificationService.showLoading(true);
        
        try {
            const [stats, transactions] = await Promise.all([
                MainAPIService.loadDashboardStats(),
                MainAPIService.loadRecentTransactions()
            ]);
            
            MainUIService.updateStatsCards(stats);
            MainUIService.renderRecentTransactions(transactions);
            
            NotificationService.showToast('Dashboard berhasil dimuat', 'success', 3000);
        } catch (error) {
            console.error('Error loading dashboard:', error);
            NotificationService.showToast('Gagal memuat data dashboard', 'error');
        } finally {
            NotificationService.showLoading(false);
        }
    }

    static async initDashboardWithBridge() {
        const token = AuthService.checkAuth();
        if (!token) return;

        NotificationService.showLoading(true);
        
        try {
            // Wait for module bridge to initialize
            if (window.DashboardBridge && !window.DashboardBridge.isInitialized) {
                console.log('⏳ Waiting for module bridge to initialize...');
                await this.waitForBridge();
            }

            await Promise.all([
                MainBridgeService.loadDashboardStatsWithBridge(),
                MainAPIService.loadRecentTransactions().then(transactions => 
                    MainUIService.renderRecentTransactions(transactions)
                )
            ]);
            
            NotificationService.showToast('Dashboard berhasil dimuat', 'success', 3000);
        } catch (error) {
            console.error('Error loading dashboard:', error);
            NotificationService.showToast('Gagal memuat data dashboard', 'error');
        } finally {
            NotificationService.showLoading(false);
        }
    }

    static waitForBridge() {
        return new Promise(resolve => {
            const checkBridge = setInterval(() => {
                if (window.DashboardBridge && window.DashboardBridge.isInitialized) {
                    clearInterval(checkBridge);
                    resolve();
                }
            }, 100);
            
            // Timeout after 5 seconds
            setTimeout(() => {
                clearInterval(checkBridge);
                resolve();
            }, 5000);
        });
    }
}

window.MainController = MainController;
