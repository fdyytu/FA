// Android Dashboard Main Controller
// Maksimal 50 baris per file

class AndroidMainController {
    static async initDashboard() {
        const token = AuthService.checkAuth();
        if (!token) return;

        NotificationService.showLoading(true);
        
        try {
            await Promise.all([
                this.loadDashboardStats(),
                this.loadRecentTransactions(),
                AndroidChartService.initCharts()
            ]);
        } catch (error) {
            console.error('Error loading dashboard:', error);
            NotificationService.showToast('Gagal memuat data dashboard', 'error');
        } finally {
            NotificationService.showLoading(false);
        }
    }

    static async loadDashboardStats() {
        try {
            const stats = await AndroidAPIService.loadDashboardStats();
            AndroidUIService.updateStatsCards(stats);
        } catch (error) {
            console.error('Error loading stats:', error);
            NotificationService.showToast('Gagal memuat statistik dashboard', 'error');
        }
    }

    static async loadRecentTransactions() {
        try {
            const transactions = await AndroidAPIService.loadRecentTransactions();
            AndroidUIService.renderRecentTransactions(transactions);
        } catch (error) {
            console.error('Error loading recent transactions:', error);
            const container = document.getElementById('recentTransactions');
            container.innerHTML = '<p class="text-red-500 text-center py-4">Gagal memuat transaksi terbaru</p>';
        }
    }

    static init() {
        this.initDashboard();
        UIService.initMobileMenu();
        UIService.initNavigation();
        AuthService.initLogout();
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    AndroidMainController.init();
});

window.AndroidMainController = AndroidMainController;
