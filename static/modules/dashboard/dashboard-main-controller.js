// Dashboard Main Controller
class DashboardMainController {
    constructor() {
        this.apiService = new DashboardApiService();
        this.statsUI = new DashboardStatsUI();
        this.chart = new DashboardChart();
        this.notifications = new DashboardNotifications();
        this.auth = new DashboardAuth();
        
        this.refreshInterval = null;
        this.init();
    }

    async init() {
        // Check authentication
        if (!this.auth.checkAuthentication()) {
            return;
        }

        // Setup logout button
        this.auth.setupLogoutButton();

        // Load dashboard data
        await this.loadDashboardData();
        
        // Setup refresh interval (every 30 seconds)
        this.refreshInterval = setInterval(() => this.loadDashboardData(), 30000);
    }

    async loadDashboardData() {
        try {
            await Promise.all([
                this.loadOverviewStats(),
                this.loadRecentTransactions()
            ]);
        } catch (error) {
            console.error('Error loading dashboard data:', error);
            this.notifications.showError('Failed to load dashboard data. Please refresh the page.');
        }
    }

    async loadOverviewStats() {
        try {
            const response = await this.apiService.getOverviewStats();
            this.statsUI.updateStatsCards(response.data);
        } catch (error) {
            console.error('Error loading overview stats:', error);
            throw error;
        }
    }

    async loadRecentTransactions() {
        try {
            const response = await this.apiService.getRecentTransactions();
            if (response.transaction_trends) {
                this.chart.updateTransactionChart(response.transaction_trends);
            }
        } catch (error) {
            console.error('Error loading recent transactions:', error);
            throw error;
        }
    }

    destroy() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
        }
        this.chart.destroy();
    }
}

// Export untuk digunakan di modul lain
window.DashboardMainController = DashboardMainController;
