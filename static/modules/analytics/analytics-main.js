// Analytics Main Module
class AnalyticsDashboard {
    constructor() {
        this.initialized = false;
    }

    async init() {
        if (this.initialized) return;

        const token = UIUtils.checkAuth();
        if (!token) return;

        UIUtils.showLoading(true);
        
        try {
            await this.loadAllData();
            analyticsUIController.initEventListeners();
            
            this.setupAutoRefresh();
            this.initialized = true;
            
            UIUtils.showToast('Dashboard analytics berhasil dimuat', 'success', 3000);
        } catch (error) {
            console.error('Error loading analytics dashboard:', error);
            UIUtils.showToast('Gagal memuat data analytics', 'error');
        } finally {
            UIUtils.showLoading(false);
        }
    }

    async loadAllData() {
        const [overviewStats, chartData] = await Promise.all([
            analyticsDataService.loadOverviewStats(),
            analyticsDataService.loadChartData()
        ]);

        analyticsUIController.updateOverviewStats(overviewStats);
        analyticsUIController.updateCharts(chartData);
    }

    setupAutoRefresh() {
        // Auto-refresh every 5 minutes
        setInterval(() => {
            if (document.visibilityState === 'visible') {
                this.refreshData();
            }
        }, 5 * 60 * 1000);
    }

    async refreshData() {
        try {
            await this.loadAllData();
        } catch (error) {
            console.error('Error during auto-refresh:', error);
        }
    }
}

// Global analytics dashboard instance
const analyticsDashboard = new AnalyticsDashboard();

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    analyticsDashboard.init();
});

// Legacy compatibility functions
async function initAnalyticsDashboard() {
    return analyticsDashboard.init();
}

async function refreshAnalytics() {
    return analyticsUIController.refreshAnalytics();
}

async function refreshSection(buttonId) {
    return analyticsUIController.refreshSection(buttonId);
}

function exportAnalytics() {
    return analyticsUIController.exportAnalytics();
}
