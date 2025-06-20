// Main Dashboard Controller
class MainDashboardController {
    constructor() {
        this.dataService = new MainDashboardDataService();
        this.uiController = new MainDashboardUIController();
    }

    async initDashboard() {
        const token = localStorage.getItem('authToken');
        if (!token) {
            window.location.href = '/login';
            return;
        }

        UIUtils.showLoading(true);
        
        try {
            await Promise.all([
                this.loadDashboardStats(),
                this.loadRecentTransactions(),
                this.loadChartData()
            ]);
            
            UIUtils.showToast('Dashboard berhasil dimuat', 'success', 3000);
        } catch (error) {
            console.error('Error loading dashboard:', error);
            UIUtils.showToast('Gagal memuat data dashboard', 'error');
        } finally {
            UIUtils.showLoading(false);
        }
    }

    async loadDashboardStats() {
        const stats = await this.dataService.loadDashboardStats();
        this.uiController.updateStatsCards(stats);
    }

    async loadRecentTransactions() {
        const transactions = await this.dataService.loadRecentTransactions();
        this.uiController.renderRecentTransactions(transactions);
    }

    async loadChartData() {
        const chartData = await this.dataService.loadChartData();
        this.uiController.initCharts(chartData);
    }

    async refreshDashboard() {
        UIUtils.showLoading(true);
        
        try {
            await Promise.all([
                this.loadDashboardStats(),
                this.loadRecentTransactions()
            ]);
            
            UIUtils.showToast('Dashboard berhasil diperbarui', 'success');
        } catch (error) {
            console.error('Error refreshing dashboard:', error);
            UIUtils.showToast('Gagal memperbarui dashboard', 'error');
        } finally {
            UIUtils.showLoading(false);
        }
    }
}

// Global instance
const mainDashboardController = new MainDashboardController();
