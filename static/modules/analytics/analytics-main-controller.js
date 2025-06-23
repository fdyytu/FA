// Analytics Main Controller
// Controller utama untuk analytics dashboard

class AnalyticsMainController {
    constructor() {
        this.currentDateRange = 30;
        this.isInitialized = false;
    }

    // Initialize analytics dashboard
    async initAnalyticsDashboard() {
        const token = checkAuth();
        if (!token) return;

        showLoading(true);
        
        try {
            await Promise.all([
                this.loadOverviewStats(),
                this.loadChartData(),
                this.loadTopProducts(),
                this.loadRecentActivity(),
                this.loadPerformanceMetrics(),
                this.loadGeographicData()
            ]);
            
            analyticsChartManager.initCharts();
            this.initEventListeners();
            this.isInitialized = true;
            showToast('Dashboard analytics berhasil dimuat', 'success', 3000);
        } catch (error) {
            console.error('Error loading analytics dashboard:', error);
            showToast('Gagal memuat data analytics', 'error');
        } finally {
            showLoading(false);
        }
    }

    // Load overview statistics
    async loadOverviewStats() {
        try {
            const stats = await analyticsApiService.loadOverviewStats();
            analyticsUIComponents.updateOverviewStats(stats);
        } catch (error) {
            console.error('Error in loadOverviewStats:', error);
            showError('Gagal memuat statistik overview');
        }
    }

    // Load chart data
    async loadChartData() {
        try {
            const chartData = await analyticsApiService.loadChartData();
            analyticsChartManager.setAnalyticsData(chartData);
        } catch (error) {
            console.error('Error in loadChartData:', error);
        }
    }

    // Load top products
    async loadTopProducts() {
        try {
            const products = await analyticsApiService.loadTopProducts();
            analyticsUIComponents.renderTopProducts(products);
        } catch (error) {
            console.error('Error in loadTopProducts:', error);
        }
    }

    // Load recent activity
    async loadRecentActivity() {
        try {
            const activities = await analyticsApiService.loadRecentActivity();
            analyticsUIComponents.renderRecentActivity(activities);
        } catch (error) {
            console.error('Error in loadRecentActivity:', error);
        }
    }

    // Load performance metrics
    async loadPerformanceMetrics() {
        try {
            const metrics = await analyticsApiService.loadPerformanceMetrics();
            analyticsUIComponents.renderPerformanceMetrics(metrics);
        } catch (error) {
            console.error('Error in loadPerformanceMetrics:', error);
        }
    }

    // Load geographic data
    async loadGeographicData() {
        try {
            const geoData = await analyticsApiService.loadGeographicData();
            this.renderGeographicData(geoData);
        } catch (error) {
            console.error('Error in loadGeographicData:', error);
        }
    }

    // Render geographic data
    renderGeographicData(countries) {
        const container = document.getElementById('geographicData');
        if (!container) return;
        
        container.innerHTML = countries.map(country => `
            <div class="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div class="flex items-center">
                    <div class="w-6 h-6 bg-blue-500 rounded-full flex items-center justify-center">
                        <span class="text-white text-xs font-bold">${country.code}</span>
                    </div>
                    <span class="ml-3 text-sm font-medium text-gray-900">${country.name}</span>
                </div>
                <div class="text-right">
                    <p class="text-sm font-semibold text-gray-900">${formatNumber(country.users)}</p>
                    <p class="text-xs text-gray-500">${country.percentage}%</p>
                </div>
            </div>
        `).join('');
    }

    // Initialize event listeners
    initEventListeners() {
        // Date range selector
        const dateRangeSelect = document.getElementById('dateRange');
        if (dateRangeSelect) {
            dateRangeSelect.addEventListener('change', (e) => {
                this.currentDateRange = parseInt(e.target.value);
                this.refreshAnalytics();
            });
        }

        // Refresh buttons
        const refreshButtons = document.querySelectorAll('[id^="refresh"]');
        refreshButtons.forEach(button => {
            button.addEventListener('click', () => {
                this.refreshSection(button.id);
            });
        });

        // Export button
        const exportButton = document.getElementById('exportAnalytics');
        if (exportButton) {
            exportButton.addEventListener('click', () => {
                this.exportAnalytics();
            });
        }

        // Auto-refresh setup
        this.setupAutoRefresh();
    }

    // Setup auto-refresh
    setupAutoRefresh() {
        // Auto-refresh every 5 minutes
        setInterval(() => {
            if (this.isInitialized) {
                this.loadRecentActivity();
                this.loadPerformanceMetrics();
            }
        }, 5 * 60 * 1000);
    }

    // Refresh analytics
    async refreshAnalytics() {
        showLoading(true);
        
        try {
            await Promise.all([
                this.loadOverviewStats(),
                this.loadChartData(),
                this.loadTopProducts(),
                this.loadRecentActivity(),
                this.loadPerformanceMetrics(),
                this.loadGeographicData()
            ]);
            
            analyticsChartManager.updateAllCharts();
            showToast('Dashboard analytics berhasil diperbarui', 'success', 3000);
        } catch (error) {
            showToast('Gagal memperbarui dashboard analytics', 'error');
        } finally {
            showLoading(false);
        }
    }

    // Refresh specific section
    async refreshSection(buttonId) {
        const button = document.getElementById(buttonId);
        if (button) {
            button.innerHTML = '<i class="fas fa-spinner fa-spin mr-1"></i>Refreshing...';
        }
        
        try {
            switch (buttonId) {
                case 'refreshPaymentMethods':
                    await this.loadChartData();
                    if (analyticsChartManager.charts.paymentMethods) {
                        analyticsChartManager.charts.paymentMethods.destroy();
                        analyticsChartManager.initPaymentMethodsChart();
                    }
                    break;
                case 'refreshGeographic':
                    await this.loadGeographicData();
                    break;
                case 'refreshActivity':
                    await this.loadRecentActivity();
                    break;
                case 'refreshMetrics':
                    await this.loadPerformanceMetrics();
                    break;
            }
            
            showToast('Data berhasil diperbarui', 'success', 2000);
        } catch (error) {
            showToast('Gagal memperbarui data', 'error');
        } finally {
            if (button) {
                button.innerHTML = '<i class="fas fa-sync-alt mr-1"></i>Refresh';
            }
        }
    }

    // Export analytics
    exportAnalytics() {
        const exportData = {
            overview: analyticsChartManager.analyticsData,
            date_range: this.currentDateRange,
            exported_at: new Date().toISOString()
        };
        
        const dataStr = JSON.stringify(exportData, null, 2);
        const dataBlob = new Blob([dataStr], { type: 'application/json' });
        
        const link = document.createElement('a');
        link.href = URL.createObjectURL(dataBlob);
        link.download = `analytics-${new Date().toISOString().split('T')[0]}.json`;
        link.click();
        
        showToast('Data analytics berhasil diekspor', 'success');
    }
}

// Export instance
window.analyticsMainController = new AnalyticsMainController();
