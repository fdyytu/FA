// Android Dashboard Main Module
class AndroidMain {
    constructor() {
        this.dataService = new AndroidDataService();
        this.uiController = new AndroidUIController();
        this.chartManager = new AndroidChartManager();
    }

    // Initialize dashboard
    async initDashboard() {
        const token = this.dataService.checkAuth();
        if (!token) return;

        this.uiController.showLoading(true);
        
        try {
            await Promise.all([
                this.loadDashboardStats(),
                this.loadRecentTransactions(),
                this.chartManager.initCharts()
            ]);
        } catch (error) {
            console.error('Error loading dashboard:', error);
            this.uiController.showError('Gagal memuat data dashboard');
        } finally {
            this.uiController.showLoading(false);
        }
    }

    // Load dashboard statistics
    async loadDashboardStats() {
        try {
            const stats = await this.dataService.loadDashboardStats();
            this.uiController.updateStatsCards(stats);
        } catch (error) {
            console.error('Error loading stats:', error);
            // Use mock data as fallback
            const mockStats = this.dataService.getMockStats();
            this.uiController.updateStatsCards(mockStats);
        }
    }

    // Load recent transactions
    async loadRecentTransactions() {
        try {
            // For now, use mock data
            const transactions = this.dataService.getMockTransactions();
            this.uiController.loadRecentTransactions(transactions);
        } catch (error) {
            console.error('Error loading transactions:', error);
        }
    }

    // Initialize logout functionality
    initLogout() {
        document.getElementById('logoutBtn').addEventListener('click', async () => {
            await this.dataService.performLogout();
        });
    }

    // Initialize all components
    init() {
        this.initDashboard();
        this.uiController.initMobileMenu();
        this.uiController.initNavigation();
        this.initLogout();
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    const androidDashboard = new AndroidMain();
    androidDashboard.init();
});

// Export for use in other modules
window.AndroidMain = AndroidMain;
